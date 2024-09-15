#include <iostream>
#include <cmath>

int main() {
    // Biberia Mario 5608210
    int d0 = 0, d1 = 1;

    double a, b, c;
    b = (d1 + 1) * pow(10, 20);
    c = -b;

    for (int i = 0; i <= 6; i++) {
        a = (d0 + 1) * pow(10, i);
        double result1 = (a + b) + c;
        double result2 = a + (b + c);

        std::cout << "For i = " << i << ", (a + b) + c = " << result1 << ", a + (b + c) = " << result2 << std::endl;
    }

    return 0;
}
