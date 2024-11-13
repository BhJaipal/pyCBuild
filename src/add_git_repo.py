from config import *
import os

def add_git_repo(dep: OutputDependencies, config: ConfigFile):
	os.system(f"git clone {dep.uri} _deps/{dep.depName} --depth=1")