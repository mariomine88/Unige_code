#include <iostream>
#include <cmath>

double factorial_tail(double n, double acc) {
    return (n == 0) ? acc : factorial_tail(n - 1, n * acc);
}

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

void printTaylorResults(double x, double res, int N, bool algoritmo = false) {
    double resN = algoritmo ? 1 / taylor_exp(x, N) : taylor_exp(x, N);
    double errA = resN - res;
    std::cout << (algoritmo ? "1/fN(x) = " : "fN(x) = ") << resN << " con N = " << N << std::endl;
    std::cout << "Errore assoluto " << resN << " - " << res << " = " << errA << std::endl;
    std::cout << "Errore relativo " << (errA / res) << std::endl << std::endl;
}

void printResults(double x, int ALG) {
    int N[5] = {3, 10, 50, 100, 150};

    std::cout << "_______________________________________________________________" << std::endl;
    std::cout << "Valore x = " << x << std::endl;

    double res = exp(x);
    std::cout << "f(x) = " << res << std::endl<< std::endl<< std::endl;

    std::cout.precision(17);
    if (ALG == 1) {
        for (int i = 0; i < 5; ++i) {
            printTaylorResults( x, res, N[i]);
        }
    } else {
        x = -x;
        for (int i = 0; i < 5; ++i) {
            printTaylorResults( x, res, N[i], true);
        }
    }
}

int main() {
        double values1[] = {0.5, 30, -0.5, -30};
        double values2[] = {-0.5, -30};

        std::cout << "algoritmo 1\n";
        for (double value : values1) {
            printResults(value, 1);
        }

        std::cout << "algoritmo 2\n";
        for (double value : values2) {
            printResults(value, 2);
        }

    return 0;
}