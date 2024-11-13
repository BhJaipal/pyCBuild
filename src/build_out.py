from config import *
import os
from add_git_repo import add_git_repo

def build(output: OutputType, config: ConfigFile):
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
    includeDir = ("-I" + output.include) if output.include != "" else ""
    for dep in output.deps:
        if dep.use == "pkg-config":
            libs += " " + dep.depName
            includes += " " + dep.depName
            sysLibs = True
        if dep.use == "git":
            gitDeps = True
            add_git_repo(dep, config)
            if os.path.exists("_deps/" + dep.depName + "/include"):
                includeDir += " -I_deps/" + dep.depName + "/include"
            else: includeDir += " -I_deps/" + dep.depName
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
            f"{compiler} -c {file} {includes} {libs} {includeDir} -Wall -Werror -fpic -o build/{file.split('.')[0]}.o"
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
    if output.out_type == "static_lib":
        print(
            f"\033[0;33mⵙ Creating static library lib{outputName}.a\033[0m",
            end="",
        )
        filesPresent = os.listdir(os.getcwd() + "/"+ config.LibDir)
        if "lib"+ outputName+ ".a" in filesPresent:
            os.remove(f"{os.getcwd()}/{config.LibDir}/lib{outputName}.a")
        os.system(f"ar rcs {config.LibDir}/lib{outputName}.a {objectFiles}")
        print(
            f"\r\033[1;32m Successfully created static library lib{outputName}.a\033[0m\n"
        )
    elif output.out_type == "shared_lib":
        print(
            f"\033[0;33mⵙ Creating shared library lib{outputName}.so\033[0m",
            end="",
        )
        os.system(f"{compiler} -shared -o {config.LibDir}/lib{outputName}.so {src}")
        print(
            f"\r\033[1;32m Successfully created shared library lib{outputName}.so\033[0m\n"
        )
    elif output.out_type == "executable":
        print(
            f"\033[0;33mⵙ Creating executable {outputName}.exe\033[0m", end=""
        )
        os.system(
            f"{compiler} -o {config.ExecDir}/{outputName}.exe " + " ".join([f"{config.buildDir}/{file.split('.')[0]}.o" for file in output.srcs]) + f" {libs} {includes}"
        )
        print(
            f"\r\033[1;32m Successfully created executable {outputName}.exe\033[0m\n"
        )