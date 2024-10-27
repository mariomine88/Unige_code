#include "include/punto3.h"


// La funzione infinityNorm calcola la norma infinita di un vettore.
// La norma infinita è definita come il massimo valore assoluto degli elementi del vettore.
float infinityNorm(const Vector vec) {
    float maxVal = 0.0f; 
    for (float val : vec) {
        // Aggiorna maxVal con il massimo tra maxVal e il valore assoluto dell'elemento corrente
        maxVal = max(maxVal, abs(val));
    }
    return maxVal;
}

// La funzione createPerturbationVector crea un vettore di perturbazione deltaB a partire da un vettore b.
// La perturbazione è proporzionale alla norma infinita di b e alterna segni negativi e positivi.
Vector createPerturbationVector(const Vector b) {
    float normB = infinityNorm(b); // Calcola la norma infinita del vettore b
    Vector deltaB(b.size()); // Inizializza il vettore deltaB con la stessa dimensione di b

    for (size_t i = 0; i < b.size(); ++i) {
        // Assegna a deltaB[i] una perturbazione proporzionale a normB * il vetore Delta
        // Alterna tra -0.01f e 0.01f a seconda che l'indice sia pari o dispari
        deltaB[i] = normB * (i % 2 == 0 ? -0.01f : 0.01f);
    }

    return deltaB;
}

// La funzione printComparison stampa un confronto tra due vettori x e xPerturbed su un file di output.
// Il confronto è etichettato con il nome della matrice fornito come parametro.
void printComparison(ofstream &outFile, const Vector x, const Vector xPerturbed, const string matrixName) {
    // Stampa l'intestazione del confronto con il nome della matrice
    outFile << "Confronto per " << matrixName << ":\n";
    // Stampa l'intestazione delle colonne
    outFile << setw(15) << "x" << setw(20) << "˜x\n";
    
    // Itera su ogni elemento dei vettori x e xPerturbed
    for (size_t i = 0; i < x.size(); ++i) {
        // Stampa l'elemento corrente di x e xPerturbed con una precisione di 6 cifre decimali
        outFile << setw(15) << fixed << setprecision(5) << x[i]
                << setw(20) << xPerturbed[i] << "\n";
    } 
    outFile << endl;
}

// Restituisce un nuovo vettore contenente i risultati delle somme.
Vector addVectors(const Vector vec1, const Vector vec2) {
    Vector result(vec1.size()); // Inizializza il vettore risultato con la stessa dimensione di vec1

    // Itera su ogni elemento dei vettori vec1 e vec2
    for (size_t i = 0; i < vec1.size(); ++i) {
        // Somma gli elementi corrispondenti di vec1 e vec2 e assegna il risultato a result[i]
        result[i] = vec1[i] + vec2[i];
    }
    return result;
}