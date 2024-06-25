# noqa: D100

from conan import ConanFile
from conan.tools.files import get, copy


class armadilloRecipe(ConanFile):  # noqa: D101
    name = "armadillo"
    user = "gtel"
    channel = "stable"

    # Optional metadata
    license = "Apache License 2.0"
    author = "Darlan Cavalcante Moreira (darcamo@gmail.com)"
    url = "https://github.com/darcamo/conan-armadillo"
    description = "C++ library for linear algebra & scientific computing"
    topics = ("linear algebra", "scientific computing", "matrix", "vector")

    package_type = "header-library"

    def source(self):  # noqa: D102
        get(self, self.conan_data['sources'][self.version], strip_root=True)

    def package(self):  # noqa: D102
        copy(self, "include/armadillo",
             self.source_folder,
             self.package_folder)
        copy(self, "*.hpp", self.source_folder, self.package_folder)

    def package_info(self):  # noqa: D102
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.system_libs = ["lapack", "blas"]

        # self.cpp_info.defines.append("ARMA_USE_HDF5")
        self.cpp_info.defines.append("ARMA_DONT_USE_HDF5")
        self.cpp_info.defines.append("ARMA_DONT_USE_WRAPPER")

    def package_id(self):  # noqa: D102
        self.info.clear()
