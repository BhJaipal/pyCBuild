import sys
import toml
from build_out import *
from cbuild_utils import *


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
            build(output, config)
        print(f"\033[1;32m{config.projectName} built successfully\033[0m")