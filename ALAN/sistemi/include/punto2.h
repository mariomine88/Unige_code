#ifndef punto2_H
#define punto2_H

#include "matrix.h"
#include "punto1.h"

Vector gaussianElimination(Matrix A, Vector b);
Vector constructVectorB(const Matrix& A);

#endif // punto2_H