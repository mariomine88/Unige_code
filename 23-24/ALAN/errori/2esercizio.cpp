#include <iostream>
#include <cmath>
#include <fstream>
#include <iomanip>

double taylor_exp(double x, int N) {
    double sum = 1.0;  
    double term = 1.0;
    
    for (int n = 1; n <= N; n++) {
        term *= x / n;
        sum += term;
    }

    return sum;
}

int main() {
    int N_values[] = {3, 10, 50, 100, 150};
    double x_values[] = {0.5, 30, -0.5, -30};

    std::ofstream outFile("../output.txt",std::ios::trunc);

    // Step 3: Replace std::cout with outFile
    if (outFile.is_open()) {
                outFile << std::setw(10) << "x" 
                << std::setw(20) << "Exact" 
                << std::setw(10) << "N" 
                << std::setw(20) << "Approximation" 
                << std::setw(20) << "Abs Error" 
                << std::setw(20) << "Rel Error" 
                << std::endl;
        for (double x : x_values) {
            double exact = exp(x);
            for (int N : N_values) {
                double approx = taylor_exp(x, N);
                double abs_error = std::abs(exact - approx);
                double rel_error = abs_error / std::abs(exact);

                outFile << std::setw(10) << x
                        << std::setw(20) << exact
                        << std::setw(10) << N
                        << std::setw(20) << approx 
                        << std::setw(20) << abs_error
                        << std::setw(20) << rel_error
                        << std::endl;
            }
        }


        outFile.close();
    } else {
        std::cerr << "Unable to open file";
    }
    
    return 0;
}
