#include "include/punto1.h"

// Function used for debugging
void printMatrix(const Matrix& matrix) {
    for (size_t i = 0; i < matrix.size(); i++) {
        for (size_t j = 0; j < matrix[i].size(); j++) {
             std::cout << matrix[i][j] << " ";
            }
        std::cout << std::endl;
    }
}


double infinityNorm(const Matrix& matrix) {
    double maxRowSum = 0.0;

    for (size_t i = 0; i < matrix.size(); i++) {
        double rowSum = 0.0;
        for (size_t j = 0; j < matrix[i].size(); j++) {
            rowSum += std::abs(matrix[i][j]);
        }
        if (rowSum > maxRowSum) {
            maxRowSum = rowSum;
        }
    }

    return maxRowSum;
}

Matrix createPascalMatrix(int n) {
    Matrix pascalMatrix(n, Vector(n));

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            pascalMatrix[i][j] = tgamma(i + j + 1) / (tgamma(i + 1) * tgamma(j + 1)); 
            // This is the formula (i+j)! / (i! * j!). We add +1 because the index starts at 0.
        }
    }

    return pascalMatrix;
}

// Function to create a tridiagonal matrix of size n x n
Matrix createTridiagonalMatrix(int n) {
    Matrix tridiagonalMatrix(n, Vector(n, 0.0));

    for (int i = 0; i < n; i++) {
        tridiagonalMatrix[i][i] = 2; // Diagonal elements
        if (i > 0) {
            tridiagonalMatrix[i][i - 1] = -1; // Sub-diagonal elements
            tridiagonalMatrix[i - 1][i] = -1; // Super-diagonal elements
        }
    }

    return tridiagonalMatrix;
}

