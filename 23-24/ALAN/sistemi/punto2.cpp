#include "include/punto2.h"

// La funzione gaussianElimination esegue l'eliminazione gaussiana su una matrice A e un vettore b
// per risolvere il sistema di equazioni lineari Ax = b. Restituisce il vettore soluzione x.
Vector gaussianElimination(Matrix A, Vector b) {
    int n = A.size(); // Ottiene la dimensione della matrice A
    for (int i = 0; i < n; ++i) {
        int pivot = i; // Inizializza il pivot alla riga corrente
        for (int j = i + 1; j < n; ++j) {
            // Trova la riga con il massimo valore assoluto nella colonna corrente
            if (std::abs(A[j][i]) > std::abs(A[pivot][i])) {
                pivot = j;
            }
        }
        if (pivot != i) {
            // Scambia la riga corrente con la riga pivot
            std::swap(A[i], A[pivot]);
            std::swap(b[i], b[pivot]);
        }
        for (int j = i + 1; j < n; ++j) {
            // Calcola il fattore di eliminazione per la riga j
            float factor = A[j][i] / A[i][i];
            for (int k = i; k < n; ++k) {
                // Aggiorna la riga j sottraendo il multiplo della riga i
                A[j][k] -= factor * A[i][k];
            }
            // Aggiorna il vettore b
            b[j] -= factor * b[i];
        }
    }
    Vector x(n); // Inizializza il vettore soluzione x
    for (int i = n - 1; i >= 0; --i) {
        x[i] = b[i]; // Inizializza x[i] con b[i]
        for (int j = i + 1; j < n; ++j) {
            // Sottrae i termini già risolti
            x[i] -= A[i][j] * x[j];
        }
        // Divide per il coefficiente diagonale per ottenere la soluzione
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