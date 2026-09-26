#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <mpi.h>

// Matrix multiplication C = A * B in MPI
// Matrices are stored in column-major order
// A is replicated on all processes
// B is distributed in blocks of columns
// C is gathered on process 0

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

    if (n % size != 0) {
        if (rank == 0) printf("Error: n must be divisible by the number of processes (%d)\n", size);
        MPI_Finalize();
        return 1;
    }
    int local_cols = n / size;   // number of columns of B per process

    // ---------- Allocation ----------
    double *A = (double*) malloc(n * n * sizeof(double));          // full A on all processes
    double *B = NULL;                                              // full B only on rank 0
    if (rank == 0) {
        B = (double*) malloc(n * n * sizeof(double));
    }
    double *B_local = (double*) malloc(n * local_cols * sizeof(double));
    double *C_local = (double*) malloc(n * local_cols * sizeof(double));
    double *C = NULL;
    if (rank == 0) {
        C = (double*) malloc(n * n * sizeof(double));
    }

    // ---------- Initialization ----------
    if (rank == 0) {
        // Initialize A and B with random values in [-1, 1]
        for (int i = 0; i < n * n; i++) {
            A[i] = (double)rand() / RAND_MAX * 2.0 - 1.0;
            B[i] = (double)rand() / RAND_MAX * 2.0 - 1.0;
        }
    }

    // ---------- Collective communications ----------
    // 1. Broadcast A to all processes
    MPI_Bcast(A, n * n, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    // 2. Scatter B: each process receives n*local_cols contiguous elements
    //    (since B is column-major, columns are contiguous)
    MPI_Scatter(B, n * local_cols, MPI_DOUBLE,
                B_local, n * local_cols, MPI_DOUBLE,
                0, MPI_COMM_WORLD);

    // ---------- Local computation: C_local = A * B_local ----------
    double t_start = MPI_Wtime();

    // C_local is n x local_cols, stored in column-major order
    // C_local[i][j] = sum_k A[i][k] * B_local[k][j]
    // In column-major: C_local[j*n + i] = sum_k A[k*n + i] * B_local[j*n + k]
    for (int j = 0; j < local_cols; j++) {
        for (int i = 0; i < n; i++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) {
                sum += A[k * n + i] * B_local[j * n + k];
            }
            C_local[j * n + i] = sum;
        }
    }

    double t_end = MPI_Wtime();

    // ---------- Gather results ----------
    MPI_Gather(C_local, n * local_cols, MPI_DOUBLE,
               C, n * local_cols, MPI_DOUBLE,
               0, MPI_COMM_WORLD);

    // ---------- Verification and timing on process 0 ----------
    if (rank == 0) {
        double Tpar = t_end - t_start;

        // Sequential reference computation for error checking
        double *C_ref = (double*) malloc(n * n * sizeof(double));
        double t_seq_start = MPI_Wtime();
        for (int j = 0; j < n; j++) {
            for (int i = 0; i < n; i++) {
                double sum = 0.0;
                for (int k = 0; k < n; k++) {
                    sum += A[k * n + i] * B[j * n + k];
                }
                C_ref[j * n + i] = sum;
            }
        }
        double t_seq_end = MPI_Wtime();
        double Tseq = t_seq_end - t_seq_start;

        // Maximum error
        double max_err = 0.0;
        for (int i = 0; i < n * n; i++) {
            double diff = fabs(C[i] - C_ref[i]);
            if (diff > max_err) max_err = diff;
        }

        // Metrics
        double gflops_par = (2.0 * n * n * n) / (Tpar * 1e9);
        double gflops_seq = (2.0 * n * n * n) / (Tseq * 1e9);
        double speedup = Tseq / Tpar;
        double efficiency = speedup / size;

        printf("n = %d\n", n);
        printf("Tseq   = %.6f s  (GFLOPS_seq = %.2f)\n", Tseq, gflops_seq);
        printf("Tpar   = %.6f s  (GFLOPS_par = %.2f)\n", Tpar, gflops_par);
        printf("Speedup = %.2f\n", speedup);
        printf("Efficienza = %.2f\n", efficiency);
        printf("Errore massimo = %.2e\n", max_err);

        free(C_ref);
        free(C);
        free(B);
    }

    free(A);
    free(B_local);
    free(C_local);

    MPI_Finalize();
    return 0;
}