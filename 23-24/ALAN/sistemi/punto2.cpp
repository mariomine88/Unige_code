#include "punto1.cpp"

// Function to perform Gaussian elimination with partial pivoting
Vector gaussianElimination(Matrix A, Vector b) {
    int n = A.size();

    // Forward elimination with partial pivoting
    for (int i = 0; i < n; ++i) {
        // Pivoting: find the row with the maximum element in column i
        int pivot = i;
        for (int j = i + 1; j < n; ++j) {
            if (std::abs(A[j][i]) > std::abs(A[pivot][i])) {
                pivot = j;
            }
        }

        // Swap rows if needed
        if (pivot != i) {
            std::swap(A[i], A[pivot]);
            std::swap(b[i], b[pivot]);
        }

        // Eliminate entries below the pivot
        for (int j = i + 1; j < n; ++j) {
            float factor = A[j][i] / A[i][i];
            for (int k = i; k < n; ++k) {
                A[j][k] -= factor * A[i][k];
            }
            b[j] -= factor * b[i];
        }
    }

    // Back substitution
    Vector x(n);
    for (int i = n - 1; i >= 0; --i) {
        x[i] = b[i];
        for (int j = i + 1; j < n; ++j) {
            x[i] -= A[i][j] * x[j];
        }
        x[i] /= A[i][i];
    }

    return x;
}

// Function to construct vector b = A * x̄ where x̄ = (1, 1, ..., 1)t
Vector constructVectorB(const Matrix& A) {
    int n = A.size();
    Vector b(n, 0.0f);

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            b[i] += A[i][j];
        }
    }

    return b;
}