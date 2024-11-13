from typing import Any
import numpy
from config import *


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
        config.buildDir = data["builddir"]
    if "lib-dir" in data:
        config.LibDir = data["lib-dir"]
    if "bin-dir" in data:
        config.ExecDir = data["bin-dir"]
    print(config.buildDir)
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
        if "include" in data[key]:
            out.include = data[key]["include"]
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
