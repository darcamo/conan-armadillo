#include <iostream>
#include <armadillo>
#include <iostream>

int main() {
    arma::mat m;
    m << 1 << 2 << 3 << arma::endr
      << 4 << 5 << 6 << arma::endr
      << 7 << 8 << 9;
    std::cout << "Hello Armadillo" << std::endl;
    m.print("m");

    (m*m).print();

    arma::vec singular_values = arma::svd(m);
    singular_values.print("S");

    singular_values.save("singular_values.h5", arma::hdf5_binary);
}
