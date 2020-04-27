# from conans.errors import ConanException
import os
import shutil

from conans import CMake, ConanFile, tools


class ArmadilloConan(ConanFile):
    name = "armadillo"
    version = "9.870.2"
    license = "Apache License 2.0"
    author = "Darlan Cavalcante Moreira (darcamo@gmail.com)"
    url = "https://github.com/darcamo/conan-armadillo"
    description = "C++ library for linear algebra & scientific computing"
    settings = "os", "build_type"
    options = {
        # If true the recipe will use blas and lapack from system
        "use_system_blas": [True, False],
        "use_system_hdf5": [True, False],
        "use_extern_cxx11_rng": [True, False],
        "link_with_mkl": [True, False]
    }
    default_options = ("use_system_blas=False", "use_system_hdf5=False",
                       "link_with_mkl=False", "use_extern_cxx11_rng=False")
    generators = "cmake"
    source_folder_name = "armadillo-{0}".format(version)
    source_tar_file = "{0}.tar.xz".format(source_folder_name)

    def requirements(self):
        if self.settings.os == "Windows":
            self.options.use_system_blas = False
            self.options.use_system_hdf5 = False
        if not self.options.use_system_blas:
            self.requires("openblas/[>=0.3.5]@darcamo/stable")
        if not self.options.use_system_hdf5:
            self.requires("hdf5/1.10.6")

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("7z_installer/1.0@conan/stable")
            self.build_requires("cmake_installer/3.11.3@conan/stable")

    def system_requirements(self):
        system_lib_names = []
        if self.options.use_system_hdf5:
            # The 'system_lib_names' variable will have the names of the system
            # libraries to be installed
            if tools.os_info.linux_distro == "ubuntu":
                system_lib_names.append("libhdf5-dev")
            elif tools.os_info.linux_distro == "arch":
                system_lib_names.append("hdf5")

        if self.options.use_system_blas:
            # The 'system_lib_names' variable will have the names of the system
            # libraries to be installed
            if tools.os_info.linux_distro == "ubuntu":
                system_lib_names.extend(["libblas-dev", "liblapacke-dev"])
            elif tools.os_info.linux_distro == "arch":
                system_lib_names.extend(["blas", "lapacke"])

        # Install libraries
        installer = tools.SystemPackageTool()
        for lib in system_lib_names:
            installer.install(lib)

    def configure(self):
        if self.options.link_with_mkl and not self.options.use_system_blas:
            raise Exception(
                "Link with MKL options can only be True when use_system_blas is also True"
            )

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

        tools.replace_in_file("sources/include/armadillo_bits/config.hpp",
                              "// #define ARMA_USE_HDF5",
                              "#define ARMA_USE_HDF5")
        # The command above remove the comment from ARMA_USE_HDF5_ALT, but we want it commented out
        tools.replace_in_file("sources/include/armadillo_bits/config.hpp",
                              "#define ARMA_USE_HDF5_ALT",
                              "// #define ARMA_USE_HDF5_ALT")

    def package(self):
        self.copy("*", dst="include", src="sources/include")

    def package_info(self):
        if self.options.use_extern_cxx11_rng:
            self.cpp_info.defines.append("ARMA_USE_EXTERN_CXX11_RNG")

        if self.settings.build_type == "Release":
            self.cpp_info.defines.append("ARMA_NO_DEBUG")

        if self.options.use_system_hdf5:
            if tools.os_info.linux_distro == "ubuntu":
                # In ubuntu the HDF5 library (both includes and the
                # compiled library) is located in a non-standard paths
                self.cpp_info.includedirs.append("/usr/include/hdf5/serial")
                self.cpp_info.libdirs.append(
                    "/usr/lib/x86_64-linux-gnu/hdf5/serial")

            self.cpp_info.libs.extend(["hdf5"])

        if self.options.use_system_blas:
            if self.options.link_with_mkl:
                self.cpp_info.libs.extend(["mkl_rt"])
                self.cpp_info.libdirs.append("/opt/intel/mkl/lib/intel64")
            else:
                # This will work in both ubuntu and arch
                self.cpp_info.libs.extend(["lapack", "blas"])

    def package_id(self):
        self.info.header_only()
