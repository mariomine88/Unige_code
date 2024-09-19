#ifndef punto3_H
#define punto3_H

#include "matrix.h"
#include "punto2.h"

float infinityNorm(const Vector& vec);
Vector createPerturbationVector(const Vector& b);
void printComparison(const Vector& x, const Vector& xPerturbed, const std::string& matrixName);
Vector addVectors(const Vector& vec1, const Vector& vec2);


#endif 