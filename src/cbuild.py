import os
import sys
import numpy
import toml
from typing import Any, Union

class OutputDependencies:
    depName: str
    use: str
    uri: Union[str, None] = None
    def __str__(self):
        return f"depName: {self.depName}, use: {self.use}"+ f", uri: {self.uri}" if self.uri != None else ""


class OutputType:
    language: str
    out_type: str
    name: str
    srcs: list[str]
    deps: list[OutputDependencies]

    def __getitem__(self, key: str):
        if key == "language":
            return self.language
        elif key == "type":
            return self.out_type
        elif key == "srcs":
            return self.srcs
        else:
            return self.deps
    def __contains__(self, key: str):
        if key == "language":
            return self.language
        elif key == "name":
            return self.name
        elif key == "type":
            return self.out_type
        elif key == "srcs":
            return self.srcs
        elif key == "deps":
            return self.deps



class ConfigFile:
    """
    # Example config file

    ```toml
    name = "Example project"
    [main]
    language = "c"
    src = "main.c"
    type = "executable" # | "static_lib" | "shared_lib"
    [[main.deps]]
    name = "gtk-3.0"
    use = "pkg-config" # | "git"
    uri = "..." # only used with git
    ```
    """

    projectName: str
    buildDir: str
    ExecDir: str
    LibDir: str
    buildOutputs: list[OutputType] = []

    def __getitem__(self, name: str):
        if name == "name":
            return self.projectName
        elif name == "builddir":
            return self.buildDir
        elif name == "bin-dir":
            return self.ExecDir
        elif name == "lib-dir":
            return self.LibDir
        else:
            return self.buildOutputs
    def __contains__(self, name: str):
        if name == "name":
            return self.projectName
        elif name == "builddir":
            return self.buildDir
        elif name == "bin-dir":
            return self.ExecDir
        elif name == "lib-dir":
            return self.LibDir
        else:
            return self.buildOutputs

def outputValidate(output: OutputType):
    try:
        if "name" not in output:
            raise KeyError("name must be in output")
        if "type" not in output:
            raise KeyError("type must be in output")
        if "language" not in output:
            raise KeyError("language must be in required in file output")
        if (["c", "cpp"]).index(output["language"]) == -1:
            raise KeyError("language must be c (C) or cpp (C++)")
        if type(output.name) != str:
            raise TypeError("outputType must be a string")
        if "deps" in output:
            if type(output["deps"]) != list:
                raise TypeError("deps must be a list")
    except TypeError as e:
        print(f"\033[1;31mTypeError: \033[0m {e}")
        exit(1)
    except KeyError as e:
        print(f"\033[1;31mKeyError: \033[0m {e}")
        exit(1)

def jsonToConfig(data: dict[str, Any]):
    config = ConfigFile()
    if "name" not in data:
        raise ValueError("Configuration must contain a name")
    else:
        config.projectName = data["name"]
    if "builddir" in data:
        config.buildDir = data["builddir"] or "build/"
    if "lib-dir" in data:
        config.LibDir = data["lib-dir"] or "lib/"
    if "bin-dir" in data:
        config.ExecDir = data["bin-dir"] or "bin/"
    config_keys = numpy.array(["name", "builddir", "lib-dir", "bin-dir"], dtype= str)
    for key in data:
        if key in config_keys:
            continue
        out = OutputType()
        out.name = key
        out.language = data[key]["language"]
        out.deps = []
        out.out_type = data[key]["type"]
        out.srcs = data[key]["src"]
        out.deps = []
        if "deps" in data[key]:
            for dep in data[key]["deps"]:
                depObj = OutputDependencies()
                depObj.depName = dep["name"]
                depObj.use = dep["use"]
                if "uri" in dep:
                    depObj.uri = dep["uri"]
                out.deps.append(depObj)
        config.buildOutputs.append(out)
    return config



if len(sys.argv) == 2:
    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print(
            (" " * 15) + "CBuild - A C/C++ Build system written in Python" + (" " * 15)
        )
        print("Options:")
        print("  -h, --help: Show this help message")
        print("  -B, --build: Build the project")
        print("  -I --init: Create a new project config file")
        exit(0)
    elif sys.argv[1] == "-I" or sys.argv[1] == "--init":
        toml.dump(
            {
                "name": "CBuild",
            },
            open("config.toml", "w"),
        )
        with open(".gitignore", "w") as f:
            f.write("bin/\nlib/\n*.exe\nbuild/\n*.a\n*.so\n_deps/")
        exit(0)
    elif sys.argv[1] == "-B" or sys.argv[1] == "--build":
        config: ConfigFile = jsonToConfig(toml.load("config.toml"))

        if "projectName" not in config:
            print(f"\033[1;31mKeyError: \033[0mMissing projectName in config.toml")
            exit(1)
        print(f"\033[1;32mBuilding Project {config.projectName}\033[0m")

        outputs = []
        if "outputs" not in config:
            print(f"\033[1;31mKeyError: \033[0mMissing outputs in config.toml")
            exit(1)
        outputs = config.buildOutputs

        try:
            if type(outputs) != list:
                raise TypeError("outputs must be a list")
            elif len(outputs) == 0:
                raise ValueError("outputs must not be empty")
        except TypeError as e:
            print(f"\033[1;31mTypeError: \033[0m {e}")
            exit(1)
        except ValueError as e:
            print(f"\033[1;31mValueError: \033[0m {e}")
            exit(1)
        for output in outputs:
            outputValidate(output)

        for output in outputs:
            print(f"\033[1;32mBuilding {output.name}\033[0m")
            print(
                f"\033[1;34mSetting Up compiler options for {output.name}\033[0m"
            )
            if output.out_type == "static_lib":
                src = " ".join(output.srcs)
                objectFiles = " ".join([f"{config.buildDir}/{s.split('.')[0]}.o" for s in output.srcs])
                compiler = ""
                if output.language == "c":
                    compiler = "gcc"
                else:
                    compiler = "g++"
                print(f"\033[1;34m\t{compiler} selected as compiler\033[0m")
                print("\033[1;32mCreating object files\033[0m")

                outputName = output.name
                libs = "$(pkg-config --libs"
                includes = "$(pkg-config --cflags"
                sysLibs = False
                gitDeps = False
                for dep in output.deps:
                    if dep.use == "pkg-config":
                        libs += " " + dep.depName
                        includes += " " + dep.depName
                        sysLibs = True
                    if dep.use == "git":
                        gitDeps = True
                libs += ")"
                includes += ")"
                if not sysLibs:
                    libs = ""
                    includes = ""

                for file in output.srcs:
                    if not os.path.exists("build"):
                        os.mkdir("build")
                    print(
                        f"\033[0;33m\tⵙ Compiling {file} to {file.split('.c')[0]}.o\033[0m",
                        end="",
                    )
                    res = os.system(
                        f"{compiler} -c {file} {includes} {libs} -Wall -Werror -fpic -o build/{file.split('.')[0]}.o"
                    )
                    if bool(res):
                        exit(res)
                    print(
                        f"\r\033[0;32m\t Compiled {file} to {file.split('.')[0]}.o \033[0m",
                    )

                if not os.path.exists(config.ExecDir):
                    os.mkdir(config.ExecDir)
                if gitDeps and not os.path.exists("_deps"):
                    os.mkdir("_deps")
                print(
                    f"\033[0;33mⵙ Creating static library lib{outputName}.a\033[0m",
                    end="",
                )
                filesPresent = os.listdir(os.getcwd() + "/"+ config.LibDir)
                if "lib"+outputName+ ".a" in filesPresent:
                    os.remove(f"{os.getcwd()}/{config.LibDir}/lib{outputName}.a")
                os.system(f"ar rcs {config.LibDir}/lib{outputName}.a {objectFiles}")
                print(
                    f"\r\033[1;32m Successfully created static library lib{outputName}.a\033[0m\n"
                )

            elif output.out_type == "shared_lib":
                src = " ".join(output.srcs)
                compiler = ""
                if output.language == "c":
                    compiler = "gcc"
                else:
                    compiler = "g++"
                print(f"\033[1;34m\t{compiler} selected as compiler\033[0m")
                print("\033[1;32mCreating object files\033[0m")

                outputName = output.name
                libs = "$(pkg-config --libs"
                includes = "$(pkg-config --cflags"
                sysLibs = False
                gitDeps = False
                for dep in output.deps:
                    if dep.use == "pkg-config":
                        libs += " " + dep.depName
                        includes += " " + dep.depName
                        sysLibs = True
                    if dep.use == "git":
                        gitDeps = True
                libs += ")"
                includes += ")"
                if not sysLibs:
                    libs = ""
                    includes = ""

                for file in output.srcs:
                    if not os.path.exists(config.buildDir):
                        os.mkdir(config.buildDir)
                    print(
                        f"\033[0;33m\tⵙ Compiling {file} to {file.split('.')[0]}.o\033[0m",
                        end="",
                    )
                    res = os.system(
                        f"{compiler} -c {file} {includes} {libs} -Wall -Werror -fpic -o {config.buildDir}/{file.split('.')[0]}.o"
                    )
                    if bool(res):
                        exit(res)
                    print(
                        f"\r\033[0;32m\t Compiled {file} to {file.split('.')[0]}.o \033[0m",
                    )

                if not os.path.exists(config.ExecDir):
                    os.mkdir(config.ExecDir)
                if gitDeps and not os.path.exists("_deps"):
                    os.mkdir("_deps")
                print(
                    f"\033[0;33mⵙ Creating shared library lib{outputName}.so\033[0m",
                    end="",
                )
                os.system(f"{compiler} -shared -o {config.LibDir}/lib{outputName}.so {src}")
                print(
                    f"\r\033[1;32m Successfully created shared library lib{outputName}.so\033[0m\n"
                )

            elif output.out_type == "executable":
                src = " ".join(output.srcs)
                compiler = ""
                if output.language == "c":
                    compiler = "gcc"
                else:
                    compiler = "g++"
                print(f"\033[1;34m\t{compiler} selected as compiler\033[0m")
                print("\033[1;32mCreating object files\033[0m")

                outputName = output.name
                libs = "$(pkg-config --libs"
                includes = "$(pkg-config --cflags"
                sysLibs = False
                gitDeps = False
                for dep in output.deps:
                    if dep.use == "pkg-config":
                        libs += " " + dep.depName
                        includes += " " + dep.depName
                        sysLibs = True
                    if dep.use == "git":
                        gitDeps = True
                libs += ")"
                includes += ")"
                if not sysLibs:
                    libs = ""
                    includes = ""

                for file in output.srcs:
                    if not os.path.exists(config.buildDir):
                        os.mkdir(config.buildDir)
                    print(
                        f"\033[0;33m\tⵙ Compiling {file} to {file.split('.')[0]}.o\033[0m",
                        end="",
                    )
                    res = os.system(
                        f"{compiler} -c {file} {includes} {libs} -Wall -Werror -fpic -o {config.buildDir}/{file.split('.')[0]}.o"
                    )
                    if bool(res):
                        exit(res)
                    print(
                        f"\r\033[0;32m\t Compiled {file} to {file.split('.')[0]}.o \033[0m",
                    )

                if not os.path.exists(config.ExecDir):
                    os.mkdir(config.ExecDir)
                if gitDeps and not os.path.exists("_deps"):
                    os.mkdir("_deps")

                print(
                    f"\033[0;33mⵙ Creating executable {outputName}.exe\033[0m", end=""
                )
                os.system(
                    f"{compiler} -o {config.ExecDir}/{outputName}.exe " + " ".join([f"{config.buildDir}/{file.split('.')[0]}.o" for file in output.srcs]) + f" {libs} {includes}"
                )
                print(
                    f"\r\033[1;32m Successfully created executable {outputName}.exe\033[0m\n"
                )
        print(f"\033[1;32m{config.projectName} built successfully\033[0m")

if __name__ == "__main__":
    pass