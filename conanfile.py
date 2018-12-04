from conans import ConanFile, CMake, tools
# from conans.errors import ConanException
import os
import shutil


class ArmadilloConan(ConanFile):
    name = "armadillo"
    version = "9.200.5"
    license = "Apache License 2.0"
    author = "Darlan Cavalcante Moreira (darcamo@gmail.com)"
    url = "https://github.com/darcamo/conan-armadillo"
    description = "C++ library for linear algebra & scientific computing"
    settings = "os", "build_type"
    options = {
        # If true the recipe will use blas and lapack from system
        "use_system_libs": [True, False],
        "use_extern_cxx11_rng": [True, False],
        "link_with_mkl": [True, False]}
    default_options = "use_system_libs=False", "link_with_mkl=False", "use_extern_cxx11_rng=False"
    generators = "cmake"
    source_folder_name = "armadillo-{0}".format(version)
    source_tar_file = "{0}.tar.xz".format(source_folder_name)

    def requirements(self):
        if self.settings.os == "Windows":
            self.options.use_system_libs = False
        if not self.options.use_system_libs:
            self.requires("openblas/0.3.3@darcamo/stable")
            self.requires("HDF5/1.10.3@darcamo/stable")

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("7z_installer/1.0@conan/stable")
            self.build_requires("cmake_installer/3.11.3@conan/stable")

    def system_requirements(self):
        if self.options.use_system_libs:
            # The 'system_lib_names' variable will have the names of the system
            # libraries to be installed
            if tools.os_info.linux_distro == "ubuntu":
                system_lib_names = (
                    ["libhdf5-dev", "libblas-dev", "liblapacke-dev"])
            elif tools.os_info.linux_distro == "arch":
                system_lib_names = (["hdf5", "blas", "lapacke"])
            else:
                system_lib_names = []

            installer = tools.SystemPackageTool()
            for lib in system_lib_names:
                installer.install(lib)

    def configure(self):
        if self.options.link_with_mkl and not self.options.use_system_libs:
             raise Exception("Link with MKL options can only be True when use_system_libs is also True")

    def source(self):
        tools.download(
            "http://sourceforge.net/projects/arma/files/{0}".format(
                self.source_tar_file),
            self.source_tar_file)
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

        if self.options.use_system_libs:
            if self.options.link_with_mkl:
                self.cpp_info.libs.extend(["mkl_rt", "hdf5"])
                self.cpp_info.libdirs.append("/opt/intel/mkl/lib/intel64")
            else:
                self.cpp_info.libs.extend(["lapack", "blas", "hdf5"])
        # else:
        #     # Maybe conan does this automatically
        #     self.cpp_info.libs.extend(self.deps_cpp_info.libs)

    def package_id(self):
        self.info.header_only()
