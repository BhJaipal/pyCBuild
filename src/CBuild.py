#!/bin/python3
import json
import os
import sys
from typing import List, Union, Dict

SysDepsT = Dict[str, List[str]]
BuildDepsT = Dict[str, Union[str, List[str], List[str]]]
OutputT = Dict[str, Union[str, str, SysDepsT, List[BuildDepsT]]]
CBuildConfig = Dict[str, Union[str, OutputT]]


def outputValidate(output: OutputT) -> None:
    try:
        if type(output) != dict:
            raise TypeError("output must be a dict")
        if "outputName" not in output:
            raise KeyError("outputName must be in output")
        if "outputType" not in output:
            raise KeyError("outputType must be in output")
        if "language" not in output:
            raise KeyError("language must be in required in file output")
        if (["c", "cpp"]).index(output["language"]) == -1:
            raise KeyError("language must be c (C) or cpp (C++)")
        if type(output["outputName"]) != str:
            raise TypeError("outputName must be a string")
        if type(output["outputType"]) != str:
            raise TypeError("outputType must be a string")
        if "system_deps" in output:
            if type(output["system_deps"]) != dict:
                raise TypeError("system_deps must be a dict")
            if (
                "include" in output["system_deps"]
                and type(output["system_deps"]["include"]) != list
            ):
                raise TypeError("include must be a list")
            if (
                "libs" in output["system_deps"]
                and type(output["system_deps"]["libs"]) != list
            ):
                raise TypeError("libs must be a list")
    except TypeError as e:
        print(f"\033[1;31mTypeError: \033[0m {e}")
        exit(1)
    except KeyError as e:
        print(f"\033[1;31mKeyError: \033[0m {e}")
        exit(1)


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
        json.dump(
            {
                "projectName": "CBuild",
                "$schema": os.getcwd() + "/src/CBuild.schema.json",
            },
            open("c-build.json", "w"),
        )
        with open(".gitignore", "w") as f:
            f.write("bin/\nlib/\n*.exe\nbuild/\n*.a\n*.so\n_deps/")
        exit(0)
    elif sys.argv[1] == "-B" or sys.argv[1] == "--build":
        config: CBuildConfig = json.load(open("c-build.json"))

        if "projectName" not in config:
            print(f"\033[1;31mKeyError: \033[0mMissing projectName in c-build.json")
            exit(1)
        print(f"\033[1;32mBuilding Project {config['projectName']}\033[0m")

        outputs = []
        if "outputs" not in config:
            print(f"\033[1;31mKeyError: \033[0mMissing outputs in c-build.json")
            exit(1)
        outputs = config["outputs"]

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
        print()

        for output in outputs:
            print(f"\033[1;32mBuilding {output['outputName']}\033[0m")
            print(
                f"\033[1;34mSetting Up compiler options for {output['outputName']}\033[0m"
            )
            if output["outputType"] == "static_lib":
                src = ""
                compiler = ""
                if output["language"] == "c":
                    compiler = "gcc"
                else:
                    compiler = "g++"
                for file in output["src"]:
                    src += f" {file}"
                print(f"\033[1;34m\t{compiler} selected as compiler\033[0m")
                print("\033[1;32mCreating object files\033[0m")

                for file in output["src"]:
                    if not os.path.exists("build"):
                        os.mkdir("build")
                    src += f" build/{file.split('.')[0]}.o"
                    print(
                        f"\033[0;33m\tⵙ Compiling {file} to {file.split('.')[0]}.o\033[0m",
                        end="",
                    )
                    os.system(
                        f"{compiler} -c {file} -Wall -Werror -o build/{file.split('.')[0]}.o"
                    )
                    print(
                        f"\r\033[0;32m\t Compiled {file} to {file.split('.')[0]}.o\033[0m"
                    )
                outputName = output["outputName"]
                if not os.path.exists("lib"):
                    os.mkdir("lib")
                print(
                    f"\033[0;33mⵙ Creating static library lib{outputName}.a\033[0m",
                    end="",
                )
                os.system(f"ar rcs lib/lib{outputName}.a {src}")
                print(
                    f"\r\033[1;32m Successfully created shared library lib{outputName}.so\033[0m\n"
                )

            elif output["outputType"] == "shared_lib":
                src = ""
                compiler = ""
                if output["language"] == "c":
                    compiler = "gcc"
                else:
                    compiler = "g++"
                print(f"\033[1;34m\t{compiler} selected as compiler\033[0m")
                print("\033[1;32mCreating object files\033[0m")

                for file in output["src"]:
                    if not os.path.exists("build"):
                        os.mkdir("build")
                    src += f" build/{file.split('.')[0]}.o"
                    print(
                        f"\033[0;33m\tⵙ Compiling {file} to {file.split('.')[0]}.o\033[0m",
                        end="",
                    )
                    os.system(
                        f"{compiler} -c {file} -Wall -Werror -fpic -o build/{file.split('.')[0]}.o"
                    )
                    print(
                        f"\r\033[0;32m\t Compiled {file} to {file.split('.')[0]}.o \033[0m"
                    )
                outputName = output["outputName"]
                if not os.path.exists("lib"):
                    os.mkdir("lib")
                if os.path.exists(f"lib/lib{outputName}.so"):
                    os.system(f"rm lib/lib{outputName}.so")
                    os.system(f"touch lib/lib{outputName}.so")
                else:
                    os.system(f"touch lib/lib{outputName}.so")
                print(
                    f"\033[0;33mⵙ Creating shared library lib{outputName}.so\033[0m",
                    end="",
                )
                os.system(f"{compiler} -shared -o lib/lib{outputName}.so {src}")
                print(
                    f"\r\033[1;32m Successfully created shared library lib{outputName}.so\033[0m\n"
                )

            elif output["outputType"] == "executable":
                src = ""
                compiler = ""
                if output["language"] == "c":
                    compiler = "gcc"
                else:
                    compiler = "g++"
                for file in output["src"]:
                    src += f" {file}"
                print(f"\033[1;34m\t{compiler} selected as compiler\033[0m")
                print("\033[1;32mCreating object files\033[0m")

                for file in output["src"]:
                    if not os.path.exists("build"):
                        os.mkdir("build")
                    print(
                        f"\033[0;33m\tⵙ Compiling {file} to {file.split('.')[0]}.o\033[0m",
                        end="",
                    )
                    os.system(
                        f"{compiler} -c {file} -Wall -Werror -fpic -o build/{file.split('.')[0]}.o"
                    )
                    print(
                        f"\r\033[0;32m\t Compiled {file} to {file.split('.')[0]}.o \033[0m",
                    )

                outputName = output["outputName"]
                libs = "$(pkg-config --libs"
                includes = "$(pkg-config --cflags"
                if "system_deps" in output:
                    if (
                        "include" in output["system_deps"]
                        and len(output["system_deps"]["include"]) != 0
                    ):
                        for inc in output["system_deps"]["include"]:
                            includes += f" {inc}"
                        includes += ")"
                    else:
                        includes = ""
                    useLibs = False
                    buildLibs = [
                        (out["outputName"] if out["outputType"] == "shared_lib" else "")
                        for out in outputs
                    ]
                    staticLibs = [
                        (out["outputName"] if out["outputType"] == "static_lib" else "")
                        for out in outputs
                    ]
                    if (
                        "libs" in output["system_deps"]
                        and len(output["system_deps"]["libs"]) != 0
                    ):
                        for lib in output["system_deps"]["libs"]:
                            if lib not in buildLibs and lib not in staticLibs:
                                libs += f" {lib}"
                        libs += ")"
                        if libs == "$(pkg-config --libs)":
                            libs = ""
                        for lib in output["system_deps"]["libs"]:
                            if lib in buildLibs:
                                useLibs = True
                                libs += " -L" + os.getcwd() + "/lib"
                                libs += f" lib/lib{lib}.so"
                            if lib in staticLibs:
                                libs += f" lib/lib{lib}.a"
                    else:
                        libs = ""
                if not os.path.exists("bin"):
                    os.mkdir("bin")
                if not os.path.exists("_deps"):
                    os.mkdir("_deps")
                if "build_deps" in output:
                    for dep in output["build_deps"]:
                        depName: str = ""
                        if "git" in dep and "repo" in dep and type(dep["repo"]) == str:
                            depName = dep["repo"]
                            if depName.endswith("/"):
                                depName = depName[:-1]
                            elif depName.endswith(".git"):
                                depName = depName[:-4]
                            depName = depName.split("/")[-1]
                            if not dep["repo"].startswith("https://"):
                                dep["name"] = "https://" + dep["name"]
                            os.system(f"git clone {dep['repo']} _deps/{depName}")
                        elif "path" in dep and "depName" not in dep:
                            print(
                                "\033[1;31mKeyError: \033[0mdepName is required with path"
                            )
                            exit(1)
                        elif "path" in dep and type(dep["depName"]) != str:
                            print("\033[1;31mKeyError: \033[0mdepName must be a string")
                        else:
                            os.system(f"curl {dep['path']} > _deps/{dep['depName']}")

                print(
                    f"\033[0;33mⵙ Creating executable {outputName}.exe\033[0m", end=""
                )
                os.system(
                    f"{'LD_LIBRARY_PATH=' + os.getcwd() + '/lib ' if useLibs else ''}{compiler} -o bin/{outputName}.exe {src} {libs} {includes}"
                )
                print(
                    f"\r\033[1;32m Successfully created executable {outputName}.exe\033[0m\n"
                )
        print(f"\033[1;32m{config['projectName']} built successfully\033[0m")
