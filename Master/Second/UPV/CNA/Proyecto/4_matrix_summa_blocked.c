#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <mpi.h>
#include <omp.h>

// SUMMA + blocked local kernel
// Blocking parameters: MC, NC, KC (tunable)
// Column-major storage, square matrices n x n

#define MC 256
#define NC 256
#define KC 256

// Pack A block (m x k, column-major, leading dim lda) into contiguous buffer
static void pack_A(const double *A, int m, int k, int lda, double *buf) {
    for (int j = 0; j < k; j++)
        for (int i = 0; i < m; i++)
            buf[j * m + i] = A[j * lda + i];
}

// Pack B block (k x n, column-major, leading dim ldb) into contiguous buffer
static void pack_B(const double *B, int k, int n, int ldb, double *buf) {
    for (int j = 0; j < n; j++)
        for (int i = 0; i < k; i++)
            buf[j * k + i] = B[j * ldb + i];
}

// Blocked multiply-accumulate: C += A * B
// A: m x k (column-major, lda = b)
// B: k x n (column-major, ldb = b)
// C: m x n (column-major, ldc = b)
// Buffers Abuf (MC*KC) and Bbuf (KC*NC) are workspace
static void blocked_mac(const double *A, const double *B, double *C,
                        int m, int n, int k, int lda, int ldb, int ldc,
                        double *Abuf, double *Bbuf) {
    for (int jc = 0; jc < n; jc += NC) {
        int nc = (jc + NC <= n) ? NC : n - jc;
        for (int pc = 0; pc < k; pc += KC) {
            int kc = (pc + KC <= k) ? KC : k - pc;
            pack_B(&B[jc * ldb + pc], kc, nc, ldb, Bbuf);
            for (int ic = 0; ic < m; ic += MC) {
                int mc = (ic + MC <= m) ? MC : m - ic;
                pack_A(&A[pc * lda + ic], mc, kc, lda, Abuf);
                // Micro-kernel
                #pragma omp parallel for
                for (int j = 0; j < nc; j++) {
                    for (int p = 0; p < kc; p++) {
                        double bval = Bbuf[j * kc + p];
                        const double *a_col = &Abuf[p * mc];
                        double *c_col = &C[(jc + j) * ldc + ic];
                        for (int i = 0; i < mc; i++) {
                            c_col[i] += a_col[i] * bval;
                        }
                    }
                }
            }
        }
    }
}

int main(int argc, char *argv[]) {
    int rank, size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc < 2) {
        if (rank == 0) printf("Usage: %s <n>\n", argv[0]);
        MPI_Finalize();
        return 1;
    }
    int n = atoi(argv[1]);

    int N = (int) sqrt((double) size);
    if (N * N != size) {
        if (rank == 0) printf("Error: number of processes (%d) must be a perfect square\n", size);
        MPI_Finalize();
        return 1;
    }
    if (n % N != 0) {
        if (rank == 0) printf("Error: n must be divisible by grid dimension\n");
        MPI_Finalize();
        return 1;
    }
    int b = n / N;

    // ---------- Cartesian topology ----------
    int dims[2] = {N, N}, periods[2] = {0, 0}, reorder = 0;
    MPI_Comm cart_comm;
    MPI_Cart_create(MPI_COMM_WORLD, 2, dims, periods, reorder, &cart_comm);
    int coords[2];
    MPI_Cart_coords(cart_comm, rank, 2, coords);
    int my_row = coords[0], my_col = coords[1];

    int remain_row[2] = {0, 1}, remain_col[2] = {1, 0};
    MPI_Comm row_comm, col_comm;
    MPI_Cart_sub(cart_comm, remain_row, &row_comm);
    MPI_Cart_sub(cart_comm, remain_col, &col_comm);

    // ---------- Local buffers ----------
    double *A_local = (double*) calloc(b * b, sizeof(double));
    double *B_local = (double*) calloc(b * b, sizeof(double));
    double *C_local = (double*) calloc(b * b, sizeof(double));
    double *A_panel = (double*) malloc(b * b * sizeof(double));
    double *B_panel = (double*) malloc(b * b * sizeof(double));

    // Blocking workspace
    double *Abuf = (double*) malloc(MC * KC * sizeof(double));
    double *Bbuf = (double*) malloc(KC * NC * sizeof(double));

    // ---------- Global matrices on P0 ----------
    double *A = NULL, *B = NULL, *C = NULL;
    if (rank == 0) {
        A = (double*) malloc((size_t)n * n * sizeof(double));
        B = (double*) malloc((size_t)n * n * sizeof(double));
        C = (double*) calloc((size_t)n * n, sizeof(double));
        srand(42);
        for (size_t i = 0; i < (size_t)n * n; i++) {
            A[i] = (double)rand() / RAND_MAX * 2.0 - 1.0;
            B[i] = (double)rand() / RAND_MAX * 2.0 - 1.0;
        }
    }

    // ---------- Derived type for b x b blocks ----------
    MPI_Datatype block_type;
    MPI_Type_vector(b, b, n, MPI_DOUBLE, &block_type);
    MPI_Type_commit(&block_type);

    double t_start = MPI_Wtime();

    // ---------- Initial distribution ----------
    double *A_colblock = (double*) malloc(b * n * sizeof(double));
    double *B_colblock = (double*) malloc(b * n * sizeof(double));

    if (rank == 0) {
        for (int j = 0; j < N; j++) {
            if (j == 0) {
                for (int i = 0; i < b * n; i++) {
                    A_colblock[i] = A[i];
                    B_colblock[i] = B[i];
                }
            } else {
                int dest_coords[2] = {0, j}, dest_rank;
                MPI_Cart_rank(cart_comm, dest_coords, &dest_rank);
                MPI_Send(&A[j * b * n], b * n, MPI_DOUBLE, dest_rank, 0, cart_comm);
                MPI_Send(&B[j * b * n], b * n, MPI_DOUBLE, dest_rank, 1, cart_comm);
            }
        }
    } else if (my_row == 0) {
        MPI_Recv(A_colblock, b * n, MPI_DOUBLE, 0, 0, cart_comm, MPI_STATUS_IGNORE);
        MPI_Recv(B_colblock, b * n, MPI_DOUBLE, 0, 1, cart_comm, MPI_STATUS_IGNORE);
    }

    if (my_row == 0) {
        for (int i = 0; i < N; i++) {
            if (i == 0) {
                for (int c = 0; c < b; c++)
                    for (int r = 0; r < b; r++) {
                        A_local[c * b + r] = A_colblock[c * n + r];
                        B_local[c * b + r] = B_colblock[c * n + r];
                    }
            } else {
                int dest_coords[2] = {i, my_col}, dest_rank;
                MPI_Cart_rank(cart_comm, dest_coords, &dest_rank);
                MPI_Send(&A_colblock[i * b], 1, block_type, dest_rank, 2, cart_comm);
                MPI_Send(&B_colblock[i * b], 1, block_type, dest_rank, 3, cart_comm);
            }
        }
    } else {
        MPI_Recv(A_local, b * b, MPI_DOUBLE, MPI_ANY_SOURCE, 2, cart_comm, MPI_STATUS_IGNORE);
        MPI_Recv(B_local, b * b, MPI_DOUBLE, MPI_ANY_SOURCE, 3, cart_comm, MPI_STATUS_IGNORE);
    }

    // ---------- SUMMA iterations with blocked local kernel ----------
    for (int k = 0; k < N; k++) {
        for (int i = 0; i < b * b; i++) {
            A_panel[i] = A_local[i];
            B_panel[i] = B_local[i];
        }
        MPI_Bcast(A_panel, b * b, MPI_DOUBLE, k, row_comm);
        MPI_Bcast(B_panel, b * b, MPI_DOUBLE, k, col_comm);

        // Blocked local multiply-accumulate
        blocked_mac(A_panel, B_panel, C_local, b, b, b, b, b, b, Abuf, Bbuf);
    }

    double t_end = MPI_Wtime();

    // ---------- Gather results ----------
    if (rank == 0) {
        for (int j = 0; j < b; j++)
            for (int i = 0; i < b; i++)
                C[(my_col * b + j) * n + (my_row * b + i)] = C_local[j * b + i];
        for (int r = 1; r < size; r++) {
            int c2[2];
            MPI_Cart_coords(cart_comm, r, 2, c2);
            int pr = c2[0], pc = c2[1];
            double *buf = (double*) malloc(b * b * sizeof(double));
            MPI_Recv(buf, b * b, MPI_DOUBLE, r, 4, cart_comm, MPI_STATUS_IGNORE);
            for (int j = 0; j < b; j++)
                for (int i = 0; i < b; i++)
                    C[(pc * b + j) * n + (pr * b + i)] = buf[j * b + i];
            free(buf);
        }
    } else {
        MPI_Send(C_local, b * b, MPI_DOUBLE, 0, 4, cart_comm);
    }

    // ---------- Verification + metrics ----------
    if (rank == 0) {
        double *C_ref = (double*) malloc((size_t)n * n * sizeof(double));
        double t_seq_start = MPI_Wtime();
        for (int j = 0; j < n; j++)
            for (int i = 0; i < n; i++) {
                double sum = 0.0;
                for (int k = 0; k < n; k++) sum += A[k * n + i] * B[j * n + k];
                C_ref[j * n + i] = sum;
            }
        double t_seq_end = MPI_Wtime();
        double Tseq = t_seq_end - t_seq_start;

        double max_err = 0.0;
        for (size_t i = 0; i < (size_t)n * n; i++) {
            double diff = fabs(C[i] - C_ref[i]);
            if (diff > max_err) max_err = diff;
        }

        double Tpar = t_end - t_start;
        double gflops_par = (2.0 * n * n * n) / (Tpar * 1e9);
        double gflops_seq = (2.0 * n * n * n) / (Tseq * 1e9);
        double speedup = Tseq / Tpar;
        int nthreads = omp_get_max_threads();
        double efficiency = speedup / (size * nthreads);

        printf("=== SUMMA + blocked kernel ===\n");
        printf("n = %d, grid = %dx%d, b = %d\n", n, N, N, b);
        printf("MC = %d, NC = %d, KC = %d\n", MC, NC, KC);
        printf("MPI processes = %d, OpenMP threads = %d\n", size, nthreads);
        printf("Tseq   = %.6f s  (GFLOPS_seq = %.2f)\n", Tseq, gflops_seq);
        printf("Tpar   = %.6f s  (GFLOPS_par = %.2f)\n", Tpar, gflops_par);
        printf("Speedup = %.2f\n", speedup);
        printf("Efficiency = %.2f\n", efficiency);
        printf("Max error = %.2e\n", max_err);

        free(C_ref); free(C); free(A); free(B);
    }

    free(A_local); free(B_local); free(C_local);
    free(A_panel); free(B_panel);
    free(Abuf); free(Bbuf);
    free(A_colblock); free(B_colblock);

    MPI_Type_free(&block_type);
    MPI_Comm_free(&row_comm); MPI_Comm_free(&col_comm); MPI_Comm_free(&cart_comm);
    MPI_Finalize();
    return 0;
}