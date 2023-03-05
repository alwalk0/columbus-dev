import importlib
import importlib.machinery
from pathlib import Path
import os


def import_from_file(file_name:str, object:str) -> any:

    file_path = os.path.abspath(file_name)
    modulename = importlib.machinery.SourceFileLoader(file_name.removesuffix('.py'), file_path).load_module()

    return getattr(modulename, object)

