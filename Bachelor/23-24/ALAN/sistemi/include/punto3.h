#ifndef punto3_H
#define punto3_H

#include "matrix.h"
#include <fstream>

float infinityNorm(const Vector vec);
Vector createPerturbationVector(const Vector b);
void printComparison(ofstream &outFile,const Vector x, const Vector xPerturbed, const string matrixName);
Vector addVectors(const Vector vec1, const Vector vec2);


#endif // punto3_H