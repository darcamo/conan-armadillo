# conan-armadillo
Conan recipe for the armadillo library.

You can generate a package in your local cache with the command (from the folder with the conanfile.py
```
conan create . youruser/stable
```

Note: I have also created a repository in bintray with some recipes, including
this one. If you don't want to download and build this recipe manually, run the
command below and add `libraryname/version@darcamo/stable` to the conanfile.txt
in in your own project.

`conan remote add darcamo-bintray https://api.bintray.com/conan/darcamo/cppsim`
