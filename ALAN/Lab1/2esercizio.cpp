#include <iostream>
#include <cmath>

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

    for (double x : x_values) {
        for (int N : N_values) {
            double approx = taylor_exp(x, N);
            double exact = exp(x);
            double abs_error = std::abs(exact - approx);
            double rel_error = abs_error / std::abs(exact);

            std::cout << "x = " << x << ", N = " << N 
                      << ", Approximation = " << approx
                      << ", Exact = " << exact 
                      << ", Absolute Error = " << abs_error
                      << ", Relative Error = " << rel_error 
                      << std::endl;
        }
    }
    
    return 0;
}
