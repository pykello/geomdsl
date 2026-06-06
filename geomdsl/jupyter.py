from __future__ import annotations

import argparse

from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.display import display

from . import render


@magics_class
class GeomMagics(Magics):
    @cell_magic
    def geom(self, line: str, cell: str):
        parser = argparse.ArgumentParser(prog="%%geom", add_help=False)
        parser.add_argument("--dpi", type=int, default=None)
        parser.add_argument("--format", dest="fmt")
        args = parser.parse_args(line.split())
        fig = render(cell, dpi=args.dpi, fmt=args.fmt)
        display(fig)
        return fig


def load_ipython_extension(ipython):
    ipython.register_magics(GeomMagics)
