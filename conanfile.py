from conans import ConanFile, CMake, tools
# from conans.errors import ConanException
import os
import shutil


class ArmadilloConan(ConanFile):
    name = "armadillo"
    version = "8.500.1"
    license = "Apache License 2.0"
    author = "Darlan Cavalcante Moreira (darcamo@gmail.com)"
    url = "https://github.com/darcamo/conan-recipes"
    description = "C++ library for linear algebra & scientific computing"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               # If true the recipe will use blas and lapack from system
               "use_system_libs": [True, False]}
    default_options = "shared=True", "use_system_libs=False"
    generators = "cmake"
    source_folder_name = "armadillo-{0}".format(version)
    source_tar_file = "{0}.tar.xz".format(source_folder_name)

    def requirements(self):
        if self.settings.os == "Windows":
            self.options.use_system_libs = False

        if not self.options.use_system_libs:
            # Note that lapack/3.7.1@darcamo/stable includes openblas
            self.requires("lapack/3.7.1@darcamo/stable")
            # self.requires("lapack/3.7.1@conan/stable")
            self.requires("HDF5/1.10.1@darcamo/stable")

    # def configure(self):
    #     if self.settings.os == "Windows":
    #         self.options["lapack"].visual_studio=True

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

    def config_options(self):
        # Armadillo warns shared lib doesn't work on MSVC
        if self.settings.compiler == "Visual Studio":
            self.options.shared = False

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        # if not self.options.use_system_libs:
        shutil.move("conanbuildinfo.cmake", "sources/")

        # If use_system_libs is false we need to add conan stuff to armadillo
        # CMakeLists.txt file and comment out find_package for HDF5 library.
        #
        # If use_system_libs is true then we don't touch armadillo
        # CMakeLists.txt file and let armadillo find the installed libraries.
        if not self.options.use_system_libs:
            tools.replace_in_file(
                "sources/CMakeLists.txt",
                "project(armadillo CXX C)",
                '''project(armadillo CXX C)
                include(${CMAKE_SOURCE_DIR}/conanbuildinfo.cmake)
                conan_basic_setup()''')

            # tools.replace_in_file(
            #     "sources/CMakeLists.txt",
            #     "set(ARMA_USE_WRAPPER true)",
            #     "set(ARMA_USE_WRAPPER false)")

            tools.replace_in_file(
                "sources/CMakeLists.txt",
                "target_link_libraries( armadillo ${ARMA_LIBS} )",
                "target_link_libraries( armadillo ${CONAN_LIBS} )")

            # tools.replace_in_file(
            #     "sources/CMakeLists.txt",
            #     "find_package(HDF5 QUIET COMPONENTS C)",
            #     "")


        cmake.configure(source_folder="sources", build_folder="sources")
        cmake.build()

        cmake.install()

    def package_info(self):
        self.cpp_info.libdirs = ["lib", "lib64"]
        self.cpp_info.libs = ["armadillo"]

        # self.cpp_info.defines.append("ARMA_DONT_USE_WRAPPER")

        # Note that in case that system libs is set to True then HDF5 will be
        # enabled if HDF5 library is installed. When it is not to true, then
        # HDF5 from conan is used, but since armadillo CMakeLists does not
        # detect this we need to manually enable HDF5 usage.
        if not self.options.use_system_libs:
            # Since we are using a dependency from conan instead of a system
            # dependency, the armadillos cmake won't find the HDF5 library, but
            # we are including it. Let's tell armadillo to actually use it.
            self.cpp_info.defines.append("ARMA_USE_HDF5")

        # In case we are linking with the system HDF5 library and we are in
        # ubuntu, we need to add the folder where the HDF5 library can be
        # found. Note that other distros such as Arch put the HDF5 library in
        # the standard /usr/lib folder.
        distro = tools.os_info.linux_distro
        if distro == "ubuntu" and self.options.use_system_libs:
            self.cpp_info.libdirs.append(
                "/usr/lib/x86_64-linux-gnu/hdf5/serial")

        # For static libraries the wrapper does not seem to really work and
        # we end up having to link with the other libraries anyway
        if not self.options.shared:
            if self.options.use_system_libs:
                self.cpp_info.libs.extend(["hdf5", "lapack", "blas"])
            else:
                # Note that the lapack library from darcamo/stable already
                # links with openblas
                self.cpp_info.libs.extend(["hdf5", "lapack"])
