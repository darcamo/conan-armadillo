#include <iostream>
#include <armadillo>
#include <iostream>

#ifdef ARMA_USE_EXTERN_RNG
namespace arma {
thread_local std::mt19937_64 mt19937_64_instance; // NOLINT
} // namespace arma
#endif

int main() {
    arma::mat m = {{1, 2, 3},
                   {4, 5, 6},
                   {7, 8, 9}};
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


    #ifdef ARMA_USE_EXTERN_RNG
    std::cout << "Using external RNG" << std::endl;
    arma::mat random_m= arma::randn( 3, 4 );
    random_m.print("m");
    #else
    std::cout << "NOT Using external RNG" << std::endl;
    arma::mat random_m = arma::randn( 3, 4 );
    random_m.print("m");
    #endif // ARMA_USE_EXTERN_RNG
    
}
