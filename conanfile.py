# from conans.errors import ConanException
import os
import shutil

from conans import CMake, ConanFile, tools


class ArmadilloConan(ConanFile):
    name = "armadillo"
    version = "10.1.2"
    license = "Apache License 2.0"
    author = "Darlan Cavalcante Moreira (darcamo@gmail.com)"
    url = "https://github.com/darcamo/conan-armadillo"
    homepage = "http://arma.sourceforge.net/"
    description = "C++ library for linear algebra & scientific computing"
    topics = ("linear algebra",
              "scientific computing",
              "matrix",
              "vector")
    settings = "os", "build_type"
    options = {
        "shared": [True, False],
        # If true the recipe will use blas and lapack from system
        "use_system_blas": [True, False],  # If True conan will not install blas
                                           # -> armadillo will still find and
                                           # link with a blas implementation in
                                           # your compiter, if any.
        "use_system_hdf5": [True, False],  # If True then conan will not install
                                           # HDF5, but armadillo can still find
                                           # and use HDF5 in your system, if it
                                           # is installed
        "use_extern_cxx11_rng": [True, False],
        "link_with_mkl": [True, False]
    }
    default_options = {
        "shared": False,
        "use_system_blas": False,
        "use_system_hdf5": False,
        "link_with_mkl": False,
        "use_extern_cxx11_rng": False
    }
    generators = "cmake"
    source_folder_name = "armadillo-{0}".format(version)
    source_tar_file = "{0}.tar.xz".format(source_folder_name)

    def requirements(self):
        if not self.options.use_system_blas:
            self.requires("openblas/[>=0.3.10]")
            self.requires("lapack/3.7.1@conan/stable")
            self.requires("zlib/1.2.11")
            if self.options.shared:
                self.options["openblas"].shared = True
                self.options["lapack"].shared = True

        if not self.options.use_system_hdf5:
            self.requires("hdf5/1.10.6")
            if self.options.shared:
                self.options["hdf5"].shared = True

    def configure(self):
        if self.options.link_with_mkl and not self.options.use_system_blas:
            raise Exception(
                "Link with MKL options can only be True when use_system_blas is also True"
            )
        if self.options.use_system_blas:
            self.options["openblas"].build_lapack = True

    def source(self):
        tools.download(
            "http://sourceforge.net/projects/arma/files/{0}".format(
                self.source_tar_file), self.source_tar_file)
        if self.settings.os == "Windows":
            self.run("7z x %s" % self.source_tar_file)
            tar_filename = os.path.splitext(self.source_tar_file)[0]
            self.run("7z x %s" % tar_filename)
            os.unlink(self.source_tar_file)
        else:
            self.run("tar -xvf {0}".format(self.source_tar_file))
        # os.remove(self.source_tar_file)
        os.rename(self.source_folder_name, "sources")

        tools.replace_in_file("sources/CMakeLists.txt",
                              "project(armadillo CXX C)",
                              """project(armadillo CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()""")

        tools.replace_in_file("sources/CMakeLists.txt",
                              "target_link_libraries( armadillo ${ARMA_LIBS} )",
                              "target_link_libraries( armadillo ${ARMA_LIBS} ${CONAN_LIBS})")

    def build(self):
        cmake = CMake(self)
        os.mkdir("build")
        shutil.move("conanbuildinfo.cmake", "build/")
        # cmake.definitions["ARMA_DONT_USE_WRAPPER"] = True
        cmake.definitions["ARMA_USE_LAPACK"] = True
        cmake.configure(source_folder="sources", build_folder="build")
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["armadillo"]
