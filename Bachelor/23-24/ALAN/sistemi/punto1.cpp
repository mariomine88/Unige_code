#include "include/punto1.h"

// Function used for debugging
void printMatrix(const Matrix matrix) {
    for (size_t i = 0; i < matrix.size(); i++) {
        for (size_t j = 0; j < matrix[i].size(); j++) {
             cout << matrix[i][j] << " ";
            }
        cout << endl;
    }
}


// la funzione ritorna il valore di norma infinito di una matrice
double infinityNorm(const Matrix matrix) {
    // La norma infinita e il masimo tra le somma dei moduli di ogni riga della matrice
    double maxRowSum = 0.0;

    for (size_t i = 0; i < matrix.size(); i++) {
        double rowSum = 0.0;
        for (size_t j = 0; j < matrix[i].size(); j++) {
            // Aggiorna la somma massima se la somma corrente è maggiore
            rowSum += abs(matrix[i][j]);
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
        // Questa è la formula (i+j)! / (i! * j!). Aggiungiamo +1 perché l'indice inizia da 0.
        }
    }

    return pascalMatrix;
}


Matrix createTridiagonalMatrix(int n) {
    Matrix tridiagonalMatrix(n, Vector(n, 0.0));

    for (int i = 0; i < n; i++) {
        tridiagonalMatrix[i][i] = 2; // i elementi diagonali
        if (i > 0) {
            tridiagonalMatrix[i][i - 1] = -1; // elementi sotto la diagonale
            tridiagonalMatrix[i - 1][i] = -1; // elementi sopra la diagonale
        }
    }

    return tridiagonalMatrix;
}

