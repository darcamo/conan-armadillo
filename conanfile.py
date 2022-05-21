# from conans.errors import ConanException
import os
import shutil
import warnings

from conans import CMake, ConanFile, tools


class ArmadilloConan(ConanFile):
    name = "armadillo"
    version = "11.1.1"
    license = "Apache License 2.0"
    author = "Darlan Cavalcante Moreira (darcamo@gmail.com)"
    url = "https://github.com/darcamo/conan-armadillo"
    homepage = "http://arma.sourceforge.net/"
    description = "C++ library for linear algebra & scientific computing"
    topics = ("linear algebra", "scientific computing", "matrix", "vector")
    settings = "os", "build_type"
    options = {
        "shared": [True, False],
        # Enable support for HDF5 in armadillo If disabled, use_system_hdf5 option has no effect
        "enable_hdf5_support": [True, False],
        # If True conan will not install blas -> armadillo will still find and
        # link with a blas implementation in your compiter, if any.
        "use_system_blas": [True, False],
        # If True then conan will not install HDF5, but armadillo can still find
        # and use HDF5 in your system -> you must also set "enable_hdf5_support"
        # to True
        "use_system_hdf5": [True, False],
        "use_extern_rng": [True, False],
        "link_with_mkl": [True, False],
        "mkl_library_path": "ANY"
    }
    default_options = {
        "shared": False,
        "enable_hdf5_support": False,
        "use_system_blas": False,
        "use_system_hdf5": False,
        "use_extern_rng": False,
        "link_with_mkl": False,
        "mkl_library_path":
        "default"  # You can also pass the path here. If you
        # don't specify, the string "default"
        # will be replaced by a path depending on
        # the OS
    }

    generators = "cmake"
    source_folder_name = "armadillo-{0}".format(version)
    source_tar_file = "{0}.tar.xz".format(source_folder_name)

    def requirements(self):
        if tools.os_info.is_windows:
            if self.options.use_system_blas and not self.options.link_with_mkl:
                warnings.warn(
                    "use_system_blas is not supported in Windows -> changing to False"
                )
                self.options.use_system_blas = False
            if self.options.use_system_hdf5 and self.options.enable_hdf5_support:
                warnings.warn(
                    "use_system_hdf5 is not supported in Windows -> changing to False"
                )
                self.options.use_system_hdf5 = False

        if not self.options.use_system_blas:
            self.requires("openblas/[>=0.3.10]")
            self.options["openblas"].build_lapack = True
            if self.options.shared:
                self.options["openblas"].shared = True
        if not self.options.use_system_hdf5 and self.options.enable_hdf5_support:
            self.requires("hdf5/1.12.0")
            if self.options.shared:
                self.options["hdf5"].shared = True

    def system_requirements(self):
        system_lib_names = []
        if self.options.use_system_hdf5 and self.options.enable_hdf5_support:
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
        if self.options.link_with_mkl and self.options.mkl_library_path == "default":
            if tools.os_info.is_linux:
                self.options.mkl_library_path = "/opt/intel/mkl/lib/intel64"
            elif tools.os_info.is_windows:
                self.options.mkl_library_path = "C:/IntelSWTools/compilers_and_libraries/windows/mkl/lib/intel64"
            else:
                raise Exception(
                    "A default path for MKL library is now available in conan recipe for your OS. Please pass the 'mkl_library_path' option specifying the path of the MKL library"
                )

    def source(self):
        tools.download(
            "http://sourceforge.net/projects/arma/files/{0}".format(
                self.source_tar_file), self.source_tar_file)
        # if self.settings.os == "Windows":
        #     self.run("7z x %s" % self.source_tar_file)
        #     tar_filename = os.path.splitext(self.source_tar_file)[0]
        #     self.run("7z x %s" % tar_filename)
        #     os.unlink(self.source_tar_file)
        # else:
        #     self.run("tar -xvf {0}".format(self.source_tar_file))
        self.run("tar -xvf {0}".format(self.source_tar_file))
        os.rename(self.source_folder_name, "sources")

    def package(self):
        self.copy("*", dst="include", src="sources/include")

    def package_info(self):
        if self.options.use_extern_rng:
            self.cpp_info.defines.append("ARMA_USE_EXTERN_RNG")

        if self.settings.build_type == "Release":
            self.cpp_info.defines.append("ARMA_NO_DEBUG")

        if self.options.enable_hdf5_support:
            self.cpp_info.defines.append("ARMA_USE_HDF5")

            if self.options.use_system_hdf5:
                if tools.os_info.linux_distro == "ubuntu":
                    # In ubuntu the HDF5 library (both includes and the
                    # compiled library) is located in a non-standard paths
                    self.cpp_info.includedirs.append(
                        "/usr/include/hdf5/serial")
                    self.cpp_info.libdirs.append(
                        "/usr/lib/x86_64-linux-gnu/hdf5/serial")

                self.cpp_info.system_libs.extend(["hdf5"])

        else:
            self.cpp_info.defines.append("ARMA_DONT_USE_HDF5")

        if self.options.use_system_blas:
            if self.options.link_with_mkl:
                self.cpp_info.system_libs.extend(["mkl_rt"])
                self.cpp_info.libdirs.append(str(
                    self.options.mkl_library_path))
            else:
                # This will work in both ubuntu and arch
                self.cpp_info.system_libs.extend(["lapack", "blas"])

    def package_id(self):
        self.info.header_only()
