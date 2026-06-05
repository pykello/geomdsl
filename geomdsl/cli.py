from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import evaluate, render_file
from .ast import as_plain
from .errors import GeomError
from .parser import dumps_ast, parse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="geomdsl")
    parser.add_argument("input", help="Input .geom file")
    parser.add_argument("-o", "--output")
    parser.add_argument("--format", dest="fmt")
    parser.add_argument("--dpi", type=int, default=150)
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--dump-ast", action="store_true")
    parser.add_argument("--dump-scene", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        source = Path(args.input).read_text(encoding="utf-8")
        if args.dump_ast:
            print(dumps_ast(parse(source)))
            return 0
        if args.dump_scene:
            print(as_plain(evaluate(source)))
            return 0
        if args.show:
            from matplotlib import pyplot as plt
            from . import render

            render(source, fmt=args.fmt, dpi=args.dpi)
            plt.show()
            return 0
        if not args.output:
            raise GeomError("Output path is required unless --show, --dump-ast, or --dump-scene is used.")
        render_file(args.input, output=args.output, fmt=args.fmt, dpi=args.dpi)
        return 0
    except GeomError as exc:
        print(exc, file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"IOError: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
