#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <matrix_size>\n", argv[0]);
        return 1;
    }
    int n, i, j, k;
    sscanf(argv[1], "%d", &n);

    // Allocazione matrici
    double **A = (double **) malloc(n * sizeof(double *));
    double **B = (double **) malloc(n * sizeof(double *));
    double **Cref = (double **) malloc(n * sizeof(double *));
    double **C = (double **) malloc(n * sizeof(double *));

    A[0] = (double *) malloc(n * n * sizeof(double));
    B[0] = (double *) malloc(n * n * sizeof(double));
    Cref[0] = (double *) malloc(n * n * sizeof(double));
    C[0] = (double *) malloc(n * n * sizeof(double));

    // Inizializzazione A e B
    for (i = 0; i < n * n; i++) {
        A[0][i] = (double) rand() / RAND_MAX * 2.0 - 1.0;
        B[0][i] = (double) rand() / RAND_MAX * 2.0 - 1.0;
    }
    for (i = 1; i < n; i++) {
        A[i] = &(A[0][i * n]);
        B[i] = &(B[0][i * n]);
        Cref[i] = &(Cref[0][i * n]);
        C[i] = &(C[0][i * n]);
    }

    // Riferimento sequenziale (ijk)
    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            Cref[i][j] = 0.0;

    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            for (k = 0; k < n; k++)
                Cref[i][j] += A[i][k] * B[k][j];

    const char *names[6] = {"ijk", "ikj", "jik", "jki", "kij", "kji"};

    // 1. ijk parallelo (parallelizzo il ciclo i)
    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            C[i][j] = 0.0;
    double t1 = omp_get_wtime();
    #pragma omp parallel for private(j,k)
    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            for (k = 0; k < n; k++)
                C[i][j] += A[i][k] * B[k][j];
    double t2 = omp_get_wtime();
    double error = 0.0;
    for (i = 0; i < n * n; i++) error += fabs(C[0][i] - Cref[0][i]);
    printf("Variant %s (par): time = %.4f s, error = %.2e\n", names[0], t2 - t1, error);

    // 2. ikj parallelo (parallelizzo il ciclo i)
    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            C[i][j] = 0.0;
    t1 = omp_get_wtime();
    #pragma omp parallel for private(j,k)
    for (i = 0; i < n; i++)
        for (k = 0; k < n; k++)
            for (j = 0; j < n; j++)
                C[i][j] += A[i][k] * B[k][j];
    t2 = omp_get_wtime();
    error = 0.0;
    for (i = 0; i < n * n; i++) error += fabs(C[0][i] - Cref[0][i]);
    printf("Variant %s (par): time = %.4f s, error = %.2e\n", names[1], t2 - t1, error);

    // 3. jik parallelo (parallelizzo il ciclo j)
    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            C[i][j] = 0.0;
    t1 = omp_get_wtime();
    #pragma omp parallel for private(i,k)
    for (j = 0; j < n; j++)
        for (i = 0; i < n; i++)
            for (k = 0; k < n; k++)
                C[i][j] += A[i][k] * B[k][j];
    t2 = omp_get_wtime();
    error = 0.0;
    for (i = 0; i < n * n; i++) error += fabs(C[0][i] - Cref[0][i]);
    printf("Variant %s (par): time = %.4f s, error = %.2e\n", names[2], t2 - t1, error);

    // 4. jki parallelo (parallelizzo il ciclo j)
    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            C[i][j] = 0.0;
    t1 = omp_get_wtime();
    #pragma omp parallel for private(i,k)
    for (j = 0; j < n; j++)
        for (k = 0; k < n; k++)
            for (i = 0; i < n; i++)
                C[i][j] += A[i][k] * B[k][j];
    t2 = omp_get_wtime();
    error = 0.0;
    for (i = 0; i < n * n; i++) error += fabs(C[0][i] - Cref[0][i]);
    printf("Variant %s (par): time = %.4f s, error = %.2e\n", names[3], t2 - t1, error);

    // 5. kij parallelo (parallelizzo il ciclo i interno al k)
    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            C[i][j] = 0.0;
    t1 = omp_get_wtime();
    for (k = 0; k < n; k++) {
        #pragma omp parallel for private(j)
        for (i = 0; i < n; i++)
            for (j = 0; j < n; j++)
                C[i][j] += A[i][k] * B[k][j];
    }
    t2 = omp_get_wtime();
    error = 0.0;
    for (i = 0; i < n * n; i++) error += fabs(C[0][i] - Cref[0][i]);
    printf("Variant %s (par): time = %.4f s, error = %.2e\n", names[4], t2 - t1, error);

    // 6. kji parallelo (parallelizzo il ciclo j interno al k)
    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            C[i][j] = 0.0;
    t1 = omp_get_wtime();
    for (k = 0; k < n; k++) {
        #pragma omp parallel for private(i)
        for (j = 0; j < n; j++)
            for (i = 0; i < n; i++)
                C[i][j] += A[i][k] * B[k][j];
    }
    t2 = omp_get_wtime();
    error = 0.0;
    for (i = 0; i < n * n; i++) error += fabs(C[0][i] - Cref[0][i]);
    printf("Variant %s (par): time = %.4f s, error = %.2e\n", names[5], t2 - t1, error);

    // Free
    free(A[0]); free(A);
    free(B[0]); free(B);
    free(Cref[0]); free(Cref);
    free(C[0]); free(C);

    return 0;
}