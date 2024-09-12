#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

// Function to calculate the infinity norm of a matrix
double infinityNorm(const std::vector<std::vector<double>>& matrix) {
    double maxRowSum = 0.0;

    for (const auto& row : matrix) {
        double rowSum = 0.0;
        for (double element : row) {
            rowSum += std::abs(element);
        }
        if (rowSum > maxRowSum) {
            maxRowSum = rowSum;
        }
    }

    return maxRowSum;
}

// Function to create Pascal matrix of size n x n
std::vector<std::vector<double>> createPascalMatrix(int n) {
    std::vector<std::vector<double>> pascalMatrix(n, std::vector<double>(n));

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            pascalMatrix[i][j] = tgamma(i + j + 1) / (tgamma(i + 1) * tgamma(j + 1)); // (i+j)! / (i! * j!)
        }
    }

    return pascalMatrix;
}

// Function to create a tridiagonal matrix of size n x n
std::vector<std::vector<double>> createTridiagonalMatrix(int n) {
    std::vector<std::vector<double>> tridiagonalMatrix(n, std::vector<double>(n, 0.0));

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
    std::vector<std::vector<double>> A1 = {
        {3, 1, -1, 0},
        {0, 7, -3, 0},
        {0, -3, 9, -2},
        {0, 0, 4, -10}
    };

    std::vector<std::vector<double>> A2 = {
        {2, 4, -2, 0},
        {1, 3, 0, 1},
        {3, -1, 1, 2},
        {0, -1, 2, 1}
    };

    // Calculate infinity norm of A1 and A2
    std::cout << "Infinity norm of A1: " << infinityNorm(A1) << std::endl;
    std::cout << "Infinity norm of A2: " << infinityNorm(A2) << std::endl;

    // Create Pascal matrix of size 10x10
    int n = 10;
    std::vector<std::vector<double>> pascalMatrix = createPascalMatrix(n);
    std::cout << "Infinity norm of Pascal matrix (10x10): " << infinityNorm(pascalMatrix) << std::endl;

    // Define n based on the exercise description (example: matricola digits d1 = 2, d0 = 3, so n = 10 * (2 + 1) + 3 = 33)
    int d1 = 2; // Replace with actual value from matricola
    int d0 = 3; // Replace with actual value from matricola
    n = 10 * (d1 + 1) + d0;
    
    // Create tridiagonal matrix of size n x n
    std::vector<std::vector<double>> tridiagonalMatrix = createTridiagonalMatrix(n);
    std::cout << "Infinity norm of Tridiagonal matrix (" << n << "x" << n << "): " << infinityNorm(tridiagonalMatrix) << std::endl;

    return 0;
}
