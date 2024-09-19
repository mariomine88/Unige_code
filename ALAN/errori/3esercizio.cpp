#include <iostream>
#include <cmath>

void find_machine_eps_double(double &eps, int &d) {
    eps = 1.0;
    d = 0;
    while (1.0 + eps > 1.0) {
        eps /= 2.0;
        d++;
    }
    eps *= 2.0;
    d -= 1;
}

void find_machine_eps_float(float &eps, int &d) {
    eps = 1.0f;
    d = 0;
    while (1.0f + eps > 1.0f) {
        eps /= 2.0f;
        d++;
    }
    eps *= 2.0f;
    d -= 1;
}

int main() {
    double eps_double;
    int d_double;
    find_machine_eps_double(eps_double, d_double);

    float eps_float;
    int d_float;
    find_machine_eps_float(eps_float, d_float);

    std::cout << "Machine epsilon for double precision: " << eps_double << " = 2^-d where d is: " << d_double << std::endl;

    std::cout << "Machine epsilon for single precision: " << eps_float << " = 2^-d where d is: " << d_float << std::endl;

    return 0;
}