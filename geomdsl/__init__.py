from __future__ import annotations

from pathlib import Path

from .errors import GeomError, GeomNameError, GeomParseError, GeomRenderError, GeomTypeError, GeomValueError
from .evaluator import evaluate
from .parser import parse
from .render import render_scene

__all__ = [
    "GeomError",
    "GeomNameError",
    "GeomParseError",
    "GeomRenderError",
    "GeomTypeError",
    "GeomValueError",
    "evaluate",
    "parse",
    "render",
    "render_file",
]


def render(source: str, *, output: str | None = None, fmt: str | None = None, dpi: int | None = None, backend: str = "matplotlib"):
    if backend != "matplotlib":
        raise GeomRenderError(f"Unknown backend '{backend}'.")
    scene = evaluate(source)
    return render_scene(scene, output=output, fmt=fmt, dpi=dpi)


def render_file(path: str, *, output: str | None = None, fmt: str | None = None, dpi: int | None = None, backend: str = "matplotlib"):
    source = Path(path).read_text(encoding="utf-8")
    return render(source, output=output, fmt=fmt, dpi=dpi, backend=backend)
