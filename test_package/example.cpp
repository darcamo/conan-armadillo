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

    #ifdef ARMA_USE_HDF5
    std::cout << "Saving using HDF5" << std::endl;
    singular_values.save("singular_values.h5", arma::hdf5_binary);
    m.save(arma::hdf5_name("m_matrix.h5", "m"));
    std::cout << "Saved" << std::endl;
    #else
    std::cout << "HDF5 support in armadillo is not enabled" << std::endl;
    #endif
}
