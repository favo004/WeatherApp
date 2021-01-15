import os, sys

# Gets absolute path to resource. This will work for development as well as within the EXE from PyInstaller
def resource_path(path):
    try:
        base_path = sys._MEIPASS
    except Exception as e:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, path)
