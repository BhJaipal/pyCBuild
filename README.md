# pyCBuild

> pyCBuild is a C/C++ build system written in Python.
>
> It has support git cloning repos but It is not completely implemented yet

## Example config file

```toml
name = "Example project"
# default values
# builddir = "build"
# lib-dir = "lib"
# bin-dir = "bin"
[main]
language = "c"
src = "main.c"
type = "executable" # | "static_lib" | "shared_lib"
[[main.deps]]
name = "gtk-3.0"
use = "pkg-config" # | "git"
uri = "..." # only used with git
```
