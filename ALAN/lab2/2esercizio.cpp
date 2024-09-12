#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

// Function to perform Gaussian elimination with partial pivoting
std::vector<float> gaussianElimination(std::vector<std::vector<float>> A, std::vector<float> b) {
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
    std::vector<float> x(n);
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
std::vector<float> constructVectorB(const std::vector<std::vector<float>>& A) {
    int n = A.size();
    std::vector<float> b(n, 0.0f);

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            b[i] += A[i][j];
        }
    }

    return b;
}

// Function to create Pascal matrix of size n x n
std::vector<std::vector<float>> createPascalMatrix(int n) {
    std::vector<std::vector<float>> pascalMatrix(n, std::vector<float>(n));

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            pascalMatrix[i][j] = tgamma(i + j + 1) / (tgamma(i + 1) * tgamma(j + 1)); // (i+j)! / (i! * j!)
        }
    }

    return pascalMatrix;
}

// Function to create a tridiagonal matrix of size n x n
std::vector<std::vector<float>> createTridiagonalMatrix(int n) {
    std::vector<std::vector<float>> tridiagonalMatrix(n, std::vector<float>(n, 0.0f));

    for (int i = 0; i < n; ++i) {
        tridiagonalMatrix[i][i] = 2; // Diagonal elements
        if (i > 0) {
            tridiagonalMatrix[i][i - 1] = -1; // Sub-diagonal elements
            tridiagonalMatrix[i - 1][i] = -1; // Super-diagonal elements
        }
    }

    return tridiagonalMatrix;
}

int main() {
    // Define matrices A1 and A2
    std::vector<std::vector<float>> A1 = {
        {3, 1, -1, 0},
        {0, 7, -3, 0},
        {0, -3, 9, -2},
        {0, 0, 4, -10}
    };

    std::vector<std::vector<float>> A2 = {
        {2, 4, -2, 0},
        {1, 3, 0, 1},
        {3, -1, 1, 2},
        {0, -1, 2, 1}
    };

    // Calculate vector b for A1 and A2
    std::vector<float> b1 = constructVectorB(A1);
    std::vector<float> b2 = constructVectorB(A2);

    // Solve Ax = b using Gaussian elimination
    std::vector<float> x1 = gaussianElimination(A1, b1);
    std::vector<float> x2 = gaussianElimination(A2, b2);

    // Output results for A1
    std::cout << "Solution for A1:" << std::endl;
    for (float x : x1) {
        std::cout << std::fixed << std::setprecision(6) << x << " ";
    }
    std::cout << std::endl;

    // Output results for A2
    std::cout << "Solution for A2:" << std::endl;
    for (float x : x2) {
        std::cout << std::fixed << std::setprecision(6) << x << " ";
    }
    std::cout << std::endl;

    // Create Pascal matrix of size 10x10
    int n = 10;
    std::vector<std::vector<float>> pascalMatrix = createPascalMatrix(n);
    std::vector<float> bPascal = constructVectorB(pascalMatrix);
    std::vector<float> xPascal = gaussianElimination(pascalMatrix, bPascal);

    // Output results for Pascal matrix
    std::cout << "Solution for Pascal matrix (10x10):" << std::endl;
    for (float x : xPascal) {
        std::cout << std::fixed << std::setprecision(6) << x << " ";
    }
    std::cout << std::endl;

    // Define n based on the exercise description (example: matricola digits d1 = 2, d0 = 3, so n = 10 * (2 + 1) + 3 = 33)
    int d1 = 2; // Replace with actual value from matricola
    int d0 = 3; // Replace with actual value from matricola
    n = 10 * (d1 + 1) + d0;

    // Create tridiagonal matrix of size n x n
    std::vector<std::vector<float>> tridiagonalMatrix = createTridiagonalMatrix(n);
    std::vector<float> bTridiagonal = constructVectorB(tridiagonalMatrix);
    std::vector<float> xTridiagonal = gaussianElimination(tridiagonalMatrix, bTridiagonal);

    // Output results for Tridiagonal matrix
    std::cout << "Solution for Tridiagonal matrix (" << n << "x" << n << "):" << std::endl;
    for (float x : xTridiagonal) {
        std::cout << std::fixed << std::setprecision(6) << x << " ";
    }
    std::cout << std::endl;

    return 0;
}
