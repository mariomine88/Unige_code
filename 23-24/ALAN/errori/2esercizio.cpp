#include <iostream>
#include <cmath>
#include <fstream>

// Tail-recursive factorial function
double factorial_tail(double n, double acc) {
    return (n == 0) ? acc : factorial_tail(n - 1, n * acc);
}

// Main factorial function using tail recursion
double factorial(int n) {
    return factorial_tail(n, 1);
}

double taylor_exp(double x, int n) {
    if (n < 0) return -1.0;
    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        sum += pow(x, i) / factorial(i);
    }
    return sum;
}

void printTaylorResults(std::ofstream &outFile, double x, double res, int N, bool inverse = false) {
    double resN = inverse ? 1 / taylor_exp(x, N) : taylor_exp(x, N);
    double errA = resN - res;
    outFile << (inverse ? "1/fN(x) = " : "fN(x) = ") << resN << " con N = " << N << std::endl;
    outFile << "Errore assoluto " << resN << " - " << res << " = " << errA << std::endl;
    outFile << "Errore relativo " << (errA / res) << std::endl << std::endl;
}

void printResults(std::ofstream &outFile, double x, int ALG) {
    int N[5] = {3, 10, 50, 100, 150};

    outFile << "_______________________________________________________________" << std::endl << std::endl;
    outFile << "Valore x = " << x << std::endl;

    double res = exp(x);
    outFile << "f(x) = " << res << std::endl;

    outFile.precision(17);
    if (ALG == 1) {
        for (int i = 0; i < 5; ++i) {
            printTaylorResults(outFile, x, res, N[i]);
        }
    } else { // ALG == 2
        x = -x;
        for (int i = 0; i < 5; ++i) {
            printTaylorResults(outFile, x, res, N[i], true);
        }
    }
}

int main() {
    std::ofstream outFile("errori2es.txt", std::ios::trunc); // Open file in truncate mode

    if (outFile.is_open()) {
        double values1[] = {0.5, 30, -0.5, -30};
        double values2[] = {-0.5, -30};

        // algoritmo 1
        outFile << "algoritmo 1\n";
        for (double value : values1) {
            printResults(outFile, value, 1);
        }

        // algoritmo 2
        outFile << "algoritmo 2\n";
        for (double value : values2) {
            printResults(outFile, value, 2);
        }

        outFile.close();
    } else {
        std::cerr << "Unable to open file";
    }
    return 0;
}