#include "include/punto2.h"

// La funzione gaussianElimination esegue l'eliminazione gaussiana su una matrice A e un vettore b
// per risolvere il sistema di equazioni lineari Ax = b. Restituisce il vettore soluzione x.
Vector gaussianElimination(Matrix A, Vector b) {
     int n = A.size();
    // Fase di eliminazione
    for (int i = 0; i < n; ++i) {
        // Trova il pivot massimo nella colonna corrente
        int pivot = i;
        for (int j = i + 1; j < n; ++j) {
            if (abs(A[j][i]) < abs(A[pivot][i]) && abs(A[j][i]) > 0) {
                pivot = j;
            }
        }

        // Scambia la riga corrente con la riga pivot, se necessario
        if (pivot != i) {
            swap(A[i], A[pivot]);
            swap(b[i], b[pivot]);
        }
        
        // Elimina le righe sotto la riga corrente
        for (int j = i + 1; j < n; ++j) {
            double factor = A[j][i] / A[i][i];
            for (int k = i; k < n; ++k) {
                A[j][k] -= factor * A[i][k];
            }
            b[j] -= factor * b[i];
        }
    }

    // Fase di sostituzione all'indietro
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

// La funzione constructVectorB costruisce un vettore b a partire da una matrice A.
// Ogni elemento del vettore b è la somma degli elementi della corrispondente riga della matrice A.
Vector constructVectorB(const Matrix A) {
    int n = A.size(); // Ottiene la dimensione della matrice A
    Vector b(n, 0.0f); // Inizializza il vettore b con n elementi, tutti a 0.0

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            // Somma gli elementi della riga i della matrice A e li assegna a b[i]
            b[i] += A[i][j];
        }
    }
    return b;
}