#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <matrix_size>\n", argv[0]);
        return 1;
    }
    int n;
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
    for (int i = 0; i < n * n; i++) {
        A[0][i] = (double) rand() / RAND_MAX * 2.0 - 1.0;
        B[0][i] = (double) rand() / RAND_MAX * 2.0 - 1.0;
    }
    for (int i = 1; i < n; i++) {
        A[i] = &(A[0][i * n]);
        B[i] = &(B[0][i * n]);
        Cref[i] = &(Cref[0][i * n]);
        C[i] = &(C[0][i * n]);
    }

    // Riferimento: variante ijk
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            Cref[i][j] = 0.0;

    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            for (int k = 0; k < n; k++)
                Cref[i][j] += A[i][k] * B[k][j];

    const char *names[6] = {"ijk", "ikj", "jik", "jki", "kij", "kji"};

    // 1. ijk
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            C[i][j] = 0.0;
    double t1 = omp_get_wtime();
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            for (int k = 0; k < n; k++)
                C[i][j] += A[i][k] * B[k][j];
    double t2 = omp_get_wtime();
    double error = 0.0;
    for (int i = 0; i < n * n; i++) error += fabs(C[0][i] - Cref[0][i]);
    printf("Variant %s: time = %.4f s, error = %.2e\n", names[0], t2 - t1, error);

    // 2. ikj
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            C[i][j] = 0.0;
    t1 = omp_get_wtime();
    for (int i = 0; i < n; i++)
        for (int k = 0; k < n; k++)
            for (int j = 0; j < n; j++)
                C[i][j] += A[i][k] * B[k][j];
    t2 = omp_get_wtime();
    error = 0.0;
    for (int i = 0; i < n * n; i++) error += fabs(C[0][i] - Cref[0][i]);
    printf("Variant %s: time = %.4f s, error = %.2e\n", names[1], t2 - t1, error);

    // 3. jik
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            C[i][j] = 0.0;
    t1 = omp_get_wtime();
    for (int j = 0; j < n; j++)
        for (int i = 0; i < n; i++)
            for (int k = 0; k < n; k++)
                C[i][j] += A[i][k] * B[k][j];
    t2 = omp_get_wtime();
    error = 0.0;
    for (int i = 0; i < n * n; i++) error += fabs(C[0][i] - Cref[0][i]);
    printf("Variant %s: time = %.4f s, error = %.2e\n", names[2], t2 - t1, error);

    // 4. jki
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            C[i][j] = 0.0;
    t1 = omp_get_wtime();
    for (int j = 0; j < n; j++)
        for (int k = 0; k < n; k++)
            for (int i = 0; i < n; i++)
                C[i][j] += A[i][k] * B[k][j];
    t2 = omp_get_wtime();
    error = 0.0;
    for (int i = 0; i < n * n; i++) error += fabs(C[0][i] - Cref[0][i]);
    printf("Variant %s: time = %.4f s, error = %.2e\n", names[3], t2 - t1, error);

    // 5. kij
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            C[i][j] = 0.0;
    t1 = omp_get_wtime();
    for (int k = 0; k < n; k++)
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                C[i][j] += A[i][k] * B[k][j];
    t2 = omp_get_wtime();
    error = 0.0;
    for (int i = 0; i < n * n; i++) error += fabs(C[0][i] - Cref[0][i]);
    printf("Variant %s: time = %.4f s, error = %.2e\n", names[4], t2 - t1, error);

    // 6. kji
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            C[i][j] = 0.0;
    t1 = omp_get_wtime();
    for (int k = 0; k < n; k++)
        for (int j = 0; j < n; j++)
            for (int i = 0; i < n; i++)
                C[i][j] += A[i][k] * B[k][j];
    t2 = omp_get_wtime();
    error = 0.0;
    for (int i = 0; i < n * n; i++) error += fabs(C[0][i] - Cref[0][i]);
    printf("Variant %s: time = %.4f s, error = %.2e\n", names[5], t2 - t1, error);

    // Free
    free(A[0]); free(A);
    free(B[0]); free(B);
    free(Cref[0]); free(Cref);
    free(C[0]); free(C);

    return 0;
}