#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <mpi.h>
#include <omp.h>

// Hybrid MPI+OpenMP matrix multiplication C = A * B
// Column-major storage
// A replicated on all processes, B distributed by columns
// Local computation parallelized with OpenMP (jki variant, cache-friendly)

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
        if (rank == 0) printf("Error: n must be divisible by number of MPI processes (%d)\n", size);
        MPI_Finalize();
        return 1;
    }
    int local_cols = n / size;   // columns of B per process

    // ---------- Allocation ----------
    double *A = (double*) malloc(n * n * sizeof(double));
    double *B = NULL;
    if (rank == 0) B = (double*) malloc(n * n * sizeof(double));
    double *B_local = (double*) malloc(n * local_cols * sizeof(double));
    double *C_local = (double*) malloc(n * local_cols * sizeof(double));
    double *C = NULL;
    if (rank == 0) C = (double*) malloc(n * n * sizeof(double));

    // ---------- Initialization ----------
    if (rank == 0) {
        for (int i = 0; i < n * n; i++) {
            A[i] = (double)rand() / RAND_MAX * 2.0 - 1.0;
            B[i] = (double)rand() / RAND_MAX * 2.0 - 1.0;
        }
    }

    // ---------- Start timing (communication + computation) ----------
    double t_start = MPI_Wtime();

    // Broadcast A
    MPI_Bcast(A, n * n, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    // Scatter B (columns)
    MPI_Scatter(B, n * local_cols, MPI_DOUBLE,
                B_local, n * local_cols, MPI_DOUBLE,
                0, MPI_COMM_WORLD);

    // Initialize C_local to zero
    for (int i = 0; i < n * local_cols; i++) C_local[i] = 0.0;

    // ---------- Local computation: C_local = A * B_local ----------
    // Use jki variant: for each column j of B_local, accumulate over k
    #pragma omp parallel for
    for (int j = 0; j < local_cols; j++) {
        for (int k = 0; k < n; k++) {
            double b = B_local[j * n + k];
            for (int i = 0; i < n; i++) {
                C_local[j * n + i] += A[k * n + i] * b;
            }
        }
    }

    // Gather results
    MPI_Gather(C_local, n * local_cols, MPI_DOUBLE,
               C, n * local_cols, MPI_DOUBLE,
               0, MPI_COMM_WORLD);

    double t_end = MPI_Wtime();

    // ---------- Verification and metrics on rank 0 ----------
    if (rank == 0) {
        double Tpar = t_end - t_start;

        // Sequential reference (for error check and Tseq)
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

        // Max error
        double max_err = 0.0;
        for (int i = 0; i < n * n; i++) {
            double diff = fabs(C[i] - C_ref[i]);
            if (diff > max_err) max_err = diff;
        }

        // Metrics
        double gflops_par = (2.0 * n * n * n) / (Tpar * 1e9);
        double gflops_seq = (2.0 * n * n * n) / (Tseq * 1e9);
        double speedup = Tseq / Tpar;
        int nthreads = omp_get_max_threads();
        double efficiency = speedup / (size * nthreads);

        printf("n = %d, MPI processes = %d, OpenMP threads = %d\n", n, size, nthreads);
        printf("Tseq   = %.6f s  (GFLOPS_seq = %.2f)\n", Tseq, gflops_seq);
        printf("Tpar   = %.6f s  (GFLOPS_par = %.2f)\n", Tpar, gflops_par);
        printf("Speedup = %.2f\n", speedup);
        printf("Efficiency = %.2f\n", efficiency);
        printf("Max error = %.2e\n", max_err);

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