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
    if sys.argv[1] == "-B" or sys.argv[1] == "--build":
        config: CBuildConfig = json.load(open("c-build.json"))

        if "projectName" not in config:
            print(f"\033[1;31mKeyError: \033[0mMissing projectName in c-build.json")
            exit(1)

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

        for output in outputs:
            if output["outputType"] == "static_lib":
                src = ""
                compiler = ""
                if output["language"] == "c":
                    compiler = "gcc"
                else:
                    compiler = "g++"
                for file in output["src"]:
                    src += f" {file}"
                print("\033[1;32mSetting Up Compiler\033[0m")
                print(f"\033[1;32m\t{compiler} selected as compiler\033[0m\n")
                print("\033[1;32mCreating object files\033[0m")

                for file in output["src"]:
                    if not os.path.exists("build"):
                        os.mkdir("build")
                    src += f" build/{file.split('.')[0]}.o"
                    os.system(
                        f"{compiler} -c {file} -Wall -Werror -o build/{file.split('.')[0]}.o"
                    )
                outputName = output["outputName"]
                if not os.path.exists("lib"):
                    os.mkdir("lib")
                print(f"\033[1;32mCreating static library lib{outputName}.so\033[0m")
                os.system(f"ar rcs lib/lib{outputName}.a {src}")
                print()

            if output["outputType"] == "shared_lib":
                src = ""
                compiler = ""
                if output["language"] == "c":
                    compiler = "gcc"
                else:
                    compiler = "g++"
                print("\033[1;32mSetting Up Compiler\033[0m")
                print(f"\033[1;32m\t{compiler} selected as compiler\033[0m\n")
                print("\033[1;32mCreating object files\033[0m")

                for file in output["src"]:
                    if not os.path.exists("build"):
                        os.mkdir("build")
                    src += f" build/{file.split('.')[0]}.o"
                    print(
                        f"\033[1;32m\tCompiling {file} to {file.split('.')[0]}.o\033[0m"
                    )
                    os.system(
                        f"{compiler} -c {file} -Wall -Werror -fpic -o build/{file.split('.')[0]}.o"
                    )
                outputName = output["outputName"]
                if not os.path.exists("lib"):
                    os.mkdir("lib")
                if os.path.exists(f"lib/lib{outputName}.so"):
                    os.system(f"rm lib/lib{outputName}.so")
                    os.system(f"touch lib/lib{outputName}.so")
                else:
                    os.system(f"touch lib/lib{outputName}.so")
                print(f"\033[1;32mCreating shared library lib{outputName}.so\033[0m")
                os.system(f"{compiler} -shared -o lib/lib{outputName}.so {src}")
                print()

            elif output["outputType"] == "executable":
                src = ""
                compiler = ""
                if output["language"] == "c":
                    compiler = "gcc"
                else:
                    compiler = "g++"
                for file in output["src"]:
                    src += f" {file}"
                print("\033[1;32mSetting Up Compiler\033[0m")
                print(f"\033[1;32m\t{compiler} selected as compiler\033[0m\n")
                print("\033[1;32mCreating object files\033[0m")

                for file in output["src"]:
                    if not os.path.exists("build"):
                        os.mkdir("build")
                    print(
                        f"\033[1;32m\tCompiling {file} to {file.split('.')[0]}.o\033[0m"
                    )
                    os.system(
                        f"{compiler} -c {file} -Wall -Werror -fpic -o build/{file.split('.')[0]}.o"
                    )
                print()

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
                        (
                            out["outputName"]
                            if out["outputType"] == "shared_lib"
                            or out["outputType"] == "static_lib"
                            else ""
                        )
                        for out in outputs
                    ]
                    if (
                        "libs" in output["system_deps"]
                        and len(output["system_deps"]["libs"]) != 0
                    ):
                        for lib in output["system_deps"]["libs"]:
                            if lib not in buildLibs:
                                libs += f" {lib}"
                        libs += ")"
                        if libs == "$(pkg-config --libs)":
                            libs = ""
                        for lib in output["system_deps"]["libs"]:
                            if lib in buildLibs:
                                useLibs = True
                                libs += " -L" + os.getcwd() + "/lib"
                                libs += f" -l{lib}"
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

                print(f"\033[1;32mCreating executable {outputName}.exe\033[0m")
                os.system(
                    f"{'LD_LIBRARY_PATH=lib ' if useLibs else ''}{compiler} -o bin/{outputName}.exe {src} {libs} {includes}"
                )
