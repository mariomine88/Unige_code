#include "3esercizio.cpp"

int main() {
    // Define matrices
    Matrix A1 = {
        {3, 1, -1, 0},
        {0, 7, -3, 0},
        {0, -3, 9, -2},
        {0, 0, 4, -10}
    };

    Matrix A2 = {
        {2, 4, -2, 0},
        {1, 3, 0, 1},
        {3, -1, 1, 2},
        {0, -1, 2, 1}
    };

    Matrix pascalMatrix = createPascalMatrix(10);

    // EUGENIO VASSALLO 5577783
    int d0 = 3; 
    int d1 = 8; 
    int n = 10 * (d1 + 1) + d0;
    // Create tridiagonal matrix of size n x n
    Matrix tridiagonalMatrix = createTridiagonalMatrix(n);


    // 1esercizio
    std::cout << "Result of 1 Exercise:" << std::endl;
    std::cout << "Infinity norm of A1: " << infinityNorm(A1) << std::endl;
    std::cout << "Infinity norm of A2: " << infinityNorm(A2) << std::endl;
    std::cout << "Infinity norm of Pascal matrix (10x10): " << infinityNorm(pascalMatrix) << std::endl;
    std::cout << "Infinity norm of Tridiagonal matrix (" << n << "x" << n << "): " << infinityNorm(tridiagonalMatrix) << std::endl;

    // 2esercizio
    std::cout << "Result of 2 Exercise:" << std::endl;

    Vector b1 = constructVectorB(A1);
    Vector b2 = constructVectorB(A2);

    // Solve Ax = b using Gaussian elimination
    Vector x1 = gaussianElimination(A1, b1);
    Vector x2 = gaussianElimination(A2, b2);

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

    Vector bPascal = constructVectorB(pascalMatrix);
    Vector xPascal = gaussianElimination(pascalMatrix, bPascal);

    // Output results for Pascal matrix
    std::cout << "Solution for Pascal matrix (10x10):" << std::endl;
    for (float x : xPascal) {
        std::cout << std::fixed << std::setprecision(6) << x << " ";
    }
    std::cout << std::endl;

    Vector bTridiagonal = constructVectorB(tridiagonalMatrix);
    Vector xTridiagonal = gaussianElimination(tridiagonalMatrix, bTridiagonal);

    // Output results for Tridiagonal matrix
    std::cout << "Solution for Tridiagonal matrix (" << n << "x" << n << "):" << std::endl;
    for (float x : xTridiagonal) {
        std::cout << std::fixed << std::setprecision(6) << x << " ";
    }
    std::cout << std::endl;


    // 3esercizio
    std::cout << "Result of 3 Exercise:" << std::endl;

    // Create perturbation vectors
    Vector deltaB1 = createPerturbationVector(b1);
    Vector deltaB2 = createPerturbationVector(b2);

    // Solve perturbed systems for A1 and A2
    Vector xPerturbed1 = gaussianElimination(A1, addVectors(b1, deltaB1));
    Vector xPerturbed2 = gaussianElimination(A2, addVectors(b2, deltaB2));

    // Output comparisons for A1 and A2
    printComparison(x1, xPerturbed1, "Matrix A1");
    printComparison(x2, xPerturbed2, "Matrix A2");

    // Create Pascal matrix of size 10x10 and solve systems
    Vector deltaBPascal = createPerturbationVector(bPascal);
    Vector xPerturbedPascal = gaussianElimination(pascalMatrix, addVectors(bPascal, deltaBPascal));

    // Output comparison for Pascal matrix
    printComparison(xPascal, xPerturbedPascal, "Pascal Matrix");

    // Create tridiagonal matrix of size n x n and solve systems
    Vector deltaBTridiagonal = createPerturbationVector(bTridiagonal);
    Vector xPerturbedTridiagonal = gaussianElimination(tridiagonalMatrix, addVectors(bTridiagonal, deltaBTridiagonal));

    // Output comparison for Tridiagonal matrix
    printComparison(xTridiagonal, xPerturbedTridiagonal, "Tridiagonal Matrix");
    
    return 0;
}
