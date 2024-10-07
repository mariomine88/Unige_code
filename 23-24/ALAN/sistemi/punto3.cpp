#include "punto2.cpp"

// Function to calculate the infinity norm of a vector
float infinityNorm(const Vector& vec) {
    float maxVal = 0.0f;
    for (float val : vec) {
        maxVal = std::max(maxVal, std::abs(val));
    }
    return maxVal;
}

// Function to create the perturbation vector δb
Vector createPerturbationVector(const Vector& b) {
    float normB = infinityNorm(b);
    Vector deltaB(b.size());

    for (size_t i = 0; i < b.size(); ++i) {
        deltaB[i] = normB * (i % 2 == 0 ? -0.01f : 0.01f);
    }

    return deltaB;
}


// Function to print vectors for comparison
void printComparison(const Vector& x, const Vector& xPerturbed, const std::string& matrixName) {
    std::cout << "Comparison for " << matrixName << ":\n";
    std::cout << std::setw(15) << "x" << std::setw(20) << "Perturbed x\n";
    for (size_t i = 0; i < x.size(); ++i) {
        std::cout << std::setw(15) << std::fixed << std::setprecision(6) << x[i] 
                  << std::setw(20) << xPerturbed[i] << "\n";
    }
    std::cout << std::endl;
}

// Helper function to add two vectors
Vector addVectors(const Vector& vec1, const Vector& vec2) {
    Vector result(vec1.size());
    for (size_t i = 0; i < vec1.size(); ++i) {
        result[i] = vec1[i] + vec2[i];
    }
    return result;
}

