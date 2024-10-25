#include "punto3.h"
#include <iostream>
#include <iomanip>
#include <cmath>

float infinityNorm(const Vector& vec) {
    float maxVal = 0.0f;
    for (float val : vec) {
        maxVal = std::max(maxVal, std::abs(val));
    }
    return maxVal;
}

Vector createPerturbationVector(const Vector& b) {
    float normB = infinityNorm(b);
    Vector deltaB(b.size());
    for (size_t i = 0; i < b.size(); ++i) {
        deltaB[i] = normB * (i % 2 == 0 ? -0.01f : 0.01f);
    }
    return deltaB;
}

void printComparison(std::ofstream &outFile, const Vector& x, const Vector& xPerturbed, const std::string& matrixName) {
    outFile << "Comparison for " << matrixName << ":\n";
    outFile << std::setw(15) << "x" << std::setw(20) << "Perturbed x\n";
    for (size_t i = 0; i < x.size(); ++i) {
        outFile << std::setw(15) << std::fixed << std::setprecision(6) << x[i]
                  << std::setw(20) << xPerturbed[i] << "\n";
    }
    outFile << std::endl;
}

Vector addVectors(const Vector& vec1, const Vector& vec2) {
    Vector result(vec1.size());
    for (size_t i = 0; i < vec1.size(); ++i) {
        result[i] = vec1[i] + vec2[i];
    }
    return result;
}