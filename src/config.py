from typing import Union

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
    include: str = ""
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

    .. code-block:: toml

        name = "Example project"
        [main]
        language = "c"
        src = "main.c"
        include = "include" # not default
        type = "executable" # | "static_lib" | "shared_lib"
        [[main.deps]]
        name = "gtk-3.0"
        use = "pkg-config" # | "git"
        uri = "..." # only used with git
    """

    projectName: str
    buildDir: str = "build/"
    ExecDir: str = "bin/"
    LibDir: str = "lib/"
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

    def __str__(self):
        return f"projectName: {self.projectName}, buildDir: {self.buildDir}, ExecDir: {self.ExecDir}, LibDir: {self.LibDir}, buildOutputs: {self.buildOutputs}"