#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

// Function to perform Gaussian elimination with partial pivoting
std::vector<float> gaussianElimination(std::vector<std::vector<float>> A, std::vector<float> b) {
    int n = A.size();

    // Forward elimination with partial pivoting
    for (int i = 0; i < n; ++i) {
        int pivot = i;
        for (int j = i + 1; j < n; ++j) {
            if (std::abs(A[j][i]) > std::abs(A[pivot][i])) {
                pivot = j;
            }
        }

        if (pivot != i) {
            std::swap(A[i], A[pivot]);
            std::swap(b[i], b[pivot]);
        }

        for (int j = i + 1; j < n; ++j) {
            float factor = A[j][i] / A[i][i];
            for (int k = i; k < n; ++k) {
                A[j][k] -= factor * A[i][k];
            }
            b[j] -= factor * b[i];
        }
    }

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

// Function to calculate the infinity norm of a vector
float infinityNorm(const std::vector<float>& vec) {
    float maxVal = 0.0f;
    for (float val : vec) {
        maxVal = std::max(maxVal, std::abs(val));
    }
    return maxVal;
}

// Function to create the perturbation vector δb
std::vector<float> createPerturbationVector(const std::vector<float>& b) {
    float normB = infinityNorm(b);
    std::vector<float> deltaB(b.size());

    for (size_t i = 0; i < b.size(); ++i) {
        deltaB[i] = normB * (i % 2 == 0 ? -0.01f : 0.01f);
    }

    return deltaB;
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

// Function to print vectors for comparison
void printComparison(const std::vector<float>& x, const std::vector<float>& xPerturbed, const std::string& matrixName) {
    std::cout << "Comparison for " << matrixName << ":\n";
    std::cout << std::setw(15) << "x" << std::setw(20) << "Perturbed x\n";
    for (size_t i = 0; i < x.size(); ++i) {
        std::cout << std::setw(15) << std::fixed << std::setprecision(6) << x[i] 
                  << std::setw(20) << xPerturbed[i] << "\n";
    }
    std::cout << std::endl;
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

    // Solve original systems for A1 and A2
    std::vector<float> b1 = constructVectorB(A1);
    std::vector<float> b2 = constructVectorB(A2);
    std::vector<float> x1 = gaussianElimination(A1, b1);
    std::vector<float> x2 = gaussianElimination(A2, b2);

    // Create perturbation vectors
    std::vector<float> deltaB1 = createPerturbationVector(b1);
    std::vector<float> deltaB2 = createPerturbationVector(b2);

    // Solve perturbed systems for A1 and A2
    std::vector<float> xPerturbed1 = gaussianElimination(A1, b1 + deltaB1);
    std::vector<float> xPerturbed2 = gaussianElimination(A2, b2 + deltaB2);

    // Output comparisons for A1 and A2
    printComparison(x1, xPerturbed1, "Matrix A1");
    printComparison(x2, xPerturbed2, "Matrix A2");

    // Create Pascal matrix of size 10x10 and solve systems
    int n = 10;
    std::vector<std::vector<float>> pascalMatrix = createPascalMatrix(n);
    std::vector<float> bPascal = constructVectorB(pascalMatrix);
    std::vector<float> xPascal = gaussianElimination(pascalMatrix, bPascal);
    std::vector<float> deltaBPascal = createPerturbationVector(bPascal);
    std::vector<float> xPerturbedPascal = gaussianElimination(pascalMatrix, bPascal + deltaBPascal);

    // Output comparison for Pascal matrix
    printComparison(xPascal, xPerturbedPascal, "Pascal Matrix");

    // Define n based on the exercise description (example: matricola digits d1 = 2, d0 = 3, so n = 10 * (2 + 1) + 3 = 33)
    int d1 = 2; // Replace with actual value from matricola
    int d0 = 3; // Replace with actual value from matricola
    n = 10 * (d1 + 1) + d0;

    // Create tridiagonal matrix of size n x n and solve systems
    std::vector<std::vector<float>> tridiagonalMatrix = createTridiagonalMatrix(n);
    std::vector<float> bTridiagonal = constructVectorB(tridiagonalMatrix);
    std::vector<float> xTridiagonal = gaussianElimination(tridiagonalMatrix, bTridiagonal);
    std::vector<float> deltaBTridiagonal = createPerturbationVector(bTridiagonal);
    std::vector<float> xPerturbedTridiagonal = gaussianElimination(tridiagonalMatrix, bTridiagonal + deltaBTridiagonal);

    // Output comparison for Tridiagonal matrix
    printComparison(xTridiagonal, xPerturbedTridiagonal, "Tridiagonal Matrix");

    return 0;
}