from IPython.core.debugger import Pdb
import sys


def set_trace():
    Pdb(color_scheme='Linux').set_trace(sys._getframe().f_back)


def debug(f, *args, **kwargs):
    pdb = Pdb(color_scheme='Linux')
    return pdb.runcall(f, *args, **kwargs)
