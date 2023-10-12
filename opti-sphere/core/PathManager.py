import os
import sys


def get_path(relative_path):
    if getattr(sys, "frozen", False) and hasattr(sys, '_MEIPASS'):
        print(sys._MEIPASS)
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return relative_path
