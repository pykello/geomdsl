# Python API guide

Import the public API from `geomdsl`:

```python
from geomdsl import parse, load_program, load_file, evaluate, render, render_file
```

## Parse source

```python
from geomdsl import parse

program = parse("draw marker(pt(0,0))")
```

`parse` returns an AST program and raises `GeomParseError` on syntax errors.

## Evaluate source

```python
from geomdsl import evaluate

scene = evaluate("""
scene(min=(-2,-2), max=(2,2), grid=true)
draw Circle(pt(0,0), 1)
""")
```

`evaluate` returns a backend-independent `Scene` and raises `GeomError` subclasses for normal DSL mistakes.

For source strings that use `include`, pass the path that should anchor
relative include resolution:

```python
scene = evaluate(source, base_path="examples/constructions/main.geom")
```

## Render source

```python
from geomdsl import render

fig = render("draw marker(pt(0,0))")
```

When `output` is omitted, the Matplotlib backend returns a Matplotlib figure.

```python
render("draw marker(pt(0,0))", output="/tmp/point.svg")
```

When `output` is provided, `render` saves the image and returns the output path.
`render` also accepts `base_path` for source strings that use includes.

## Render a file

```python
from geomdsl import render_file

render_file("examples/circle_tangent.geom", output="/tmp/circle.png", dpi=300)
```

## API signatures

```python
parse(source: str) -> Program

load_program(source: str, *, base_path: str | Path | None = None) -> Program

load_file(path: str | Path) -> Program

evaluate(source: str, *, base_path: str | Path | None = None) -> Scene

render(
    source: str,
    *,
    output: str | None = None,
    fmt: str | None = None,
    dpi: int | None = None,
    backend: str = "matplotlib",
    base_path: str | Path | None = None,
)

render_file(
    path: str,
    *,
    output: str | None = None,
    fmt: str | None = None,
    dpi: int | None = None,
    backend: str = "matplotlib",
)
```

## Error handling

```python
from geomdsl import evaluate
from geomdsl.errors import GeomError

try:
    evaluate("A = pt(0,0)\nB = pt(1,1)\nbad = A + B")
except GeomError as exc:
    print(exc)
```

Expected output:

```text
TypeError at line 3, column 9:
Cannot add Point and Point.
```

Error classes:

```python
GeomError
GeomParseError
GeomNameError
GeomTypeError
GeomValueError
GeomRenderError
```
