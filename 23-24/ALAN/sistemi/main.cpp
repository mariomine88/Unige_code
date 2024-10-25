#include "punto1.h"
#include "punto2.h"
#include "punto3.h"

int main() {
    // definiamo le matrici
    const Matrix A1 = {
        {3, 1, -1, 0},
        {0, 7, -3, 0},
        {0, -3, 9, -2},
        {0, 0, 4, -10}
    };

    const Matrix A2 = {
        {2, 4, -2, 0},
        {1, 3, 0, 1},
        {3, -1, 1, 2},
        {0, -1, 2, 1}
    };

    const Matrix pascalMatrix = createPascalMatrix(10);

    // EUGENIO VASSALLO 5577783
    int d0 = 3; 
    int d1 = 8; 
    int n = 10 * (d1 + 1) + d0; // 10*(8+1)+3 = 93

    const Matrix tridiagonalMatrix = createTridiagonalMatrix(n);

    std::ofstream outFile("sistemiout.txt", std::ios::trunc); // Open file in truncate mode

    if (outFile.is_open()){
    // 1esercizio
    outFile << "Esercizio 1:Calcolo Norma infinito di una matrice:" << std::endl;
    outFile << "Norma infinito della matrice A1: " << infinityNorm(A1) << std::endl;
    outFile << "Norma infinito della matrice A2: " << infinityNorm(A2) << std::endl;
    outFile << "Norma infinito della matrice di Pascal: (10x10): " << infinityNorm(pascalMatrix) << std::endl;
    outFile << "Norma infinito della matrice tridiagonale (" << n << "x" << n << "): " << infinityNorm(tridiagonalMatrix) << std::endl;
    outFile << std::endl << "_______________________________________________________________" << std::endl << std::endl;
    
    // 2esercizio
    outFile << "Esercizio 2: Soluzione di un sistema lineare:" << std::endl;

    Vector b1 = constructVectorB(A1);
    Vector b2 = constructVectorB(A2);

    //Risolvi Ax = b usando l'eliminazione gaussiana
    Vector x1 = gaussianElimination(A1, b1);
    Vector x2 = gaussianElimination(A2, b2);

    // Output riusultati per A1
    outFile << "Soluzione per A1:" << std::endl;
    for (float x : x1) {
        outFile << std::fixed << std::setprecision(3) << x << " ";
    }
    outFile << std::endl;

    // Output riusultati per A2
    outFile << "Soluzione per A2:" << std::endl;
    for (float x : x2) {
        outFile << std::fixed << std::setprecision(3) << x << " ";
    }
    outFile << std::endl;

    Vector bPascal = constructVectorB(pascalMatrix);
    Vector xPascal = gaussianElimination(pascalMatrix, bPascal);

    // Output riusultati per la matrice di Pascal
    outFile << "Soluzione per la matrice di Pascal (10x10):" << std::endl;
    for (float x : xPascal) {
        outFile << std::fixed << std::setprecision(3) << x << " ";
    }
    outFile << std::endl;

    Vector bTridiagonal = constructVectorB(tridiagonalMatrix);
    Vector xTridiagonal = gaussianElimination(tridiagonalMatrix, bTridiagonal);

    // Output riusultati della Tridiagonal matrix
    outFile << "Soluzione per la matrice tridiagonale (" << n << "x" << n << "):" << std::endl;
    for (float x : xTridiagonal) {
        outFile << std::fixed << std::setprecision(3) << x << " ";
    }
    outFile << std::endl;
    outFile << std::endl << "_______________________________________________________________" << std::endl << std::endl;
    


    // 3esercizio
    outFile << "Esercizio 3: Soluzione di un sistema lineare con pertubazioni:" << std::endl;

    // Crea vettori di perturbazione
    Vector deltaB1 = createPerturbationVector(b1);
    Vector deltaB2 = createPerturbationVector(b2);

    // risolviamo A˜x = b + δb usando l'eliminazione gaussiana
    Vector xPerturbed1 = gaussianElimination(A1, addVectors(b1, deltaB1));
    Vector xPerturbed2 = gaussianElimination(A2, addVectors(b2, deltaB2));

    // Confronti dei risultati senza e con perturbazioni
    printComparison(outFile,x1, xPerturbed1, "Matrice A1");
    printComparison(outFile,x2, xPerturbed2, "Matrice A2");

    // ripetiamo il processo per la matrice di Pascal e la matrice tridiagonale
    Vector deltaBPascal = createPerturbationVector(bPascal);
    Vector xPerturbedPascal = gaussianElimination(pascalMatrix, addVectors(bPascal, deltaBPascal));
    printComparison(outFile,xPascal, xPerturbedPascal, "matrice di Pascal");

    Vector deltaBTridiagonal = createPerturbationVector(bTridiagonal);
    Vector xPerturbedTridiagonal = gaussianElimination(tridiagonalMatrix, addVectors(bTridiagonal, deltaBTridiagonal));
    printComparison(outFile,xTridiagonal, xPerturbedTridiagonal, "matrice tridiagonale");

    } else {
        std::cerr << "Unable to open file";
    }
    return 0;
}
