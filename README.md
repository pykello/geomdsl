# geomdsl

`geomdsl` is a small 2D geometry and vector-calculus diagram DSL for static figures.

It supports three entry points:

- CLI export to SVG, PNG, or PDF.
- Python API rendering with `render` and `render_file`.
- Jupyter `%%geom` cell magic.

The DSL separates mathematical objects from visible output: assignments define geometry, while only `draw` statements render objects.

## Quick start

Run an included example from the repository root:

```bash
python3 -m geomdsl.cli examples/circle_tangent.geom -o /tmp/circle.svg
```

Render to PNG:

```bash
python3 -m geomdsl.cli examples/circle_tangent.geom -o /tmp/circle.png --dpi 300
```

Dump the parsed AST:

```bash
python3 -m geomdsl.cli examples/vector_curve.geom --dump-ast
```

Run the test suite:

```bash
python3 -m pytest -q
```

## Install for command-line use

From the repository root:

```bash
python3 -m pip install -e .
```

Then use the console command:

```bash
geomdsl examples/circle_tangent.geom -o /tmp/circle.svg
```

## Minimal DSL example

```text
scene(min=(-2,-2), max=(2,2), grid=true)

O = pt(0, 0)
c = Circle(O, 1)

P = curve_at(c, pi/4)
T = unit_tangent(c, pi/4)

draw c
draw marker(P)
draw arrow(P, 0.5*T)
draw label(P, "$P$") @ {offset: vec(0.1, 0.1)}
```

## Python API

```python
from geomdsl import render_file

render_file("examples/circle_tangent.geom", output="/tmp/circle.png", dpi=300)
```

Use `render(source)` without an output path to get a Matplotlib figure.

## Jupyter

```python
%load_ext geomdsl.jupyter
```

```text
%%geom --dpi 200 --format svg
scene(min=(-2,-2), max=(2,2), grid=true)
O = pt(0,0)
draw Circle(O, 1)
```

## Textbook-inspired examples

The `examples/textbook/` directory contains original diagrams inspired by OpenStax, LibreTexts, and MIT OpenCourseWare topics:

```bash
python3 -m geomdsl.cli examples/textbook/green_theorem_circulation.geom -o /tmp/green_theorem.svg
python3 -m geomdsl.cli examples/textbook/gradient_level_curves.geom -o /tmp/gradient_levels.svg
python3 -m geomdsl.cli examples/textbook/linear_transformation_grid.geom -o /tmp/linear_grid.svg
python3 -m geomdsl.cli examples/textbook/eigenvectors_invariant_directions.geom -o /tmp/eigenvectors.svg
```

## Documentation

- [Examples guide](docs/examples.md)
- [CLI guide](docs/cli.md)
- [DSL quick reference](docs/dsl.md)
- [Python API guide](docs/python-api.md)
- [Jupyter guide](docs/jupyter.md)
- [Project specification](specs.md)

## Current implementation notes

- The first renderer is Matplotlib.
- The evaluator does not use Python `eval` on raw DSL source.
- Points and vectors are distinct runtime types.
- General curve-curve intersections, symbolic algebra, fields, animation, and 3D geometry are not v0.1 goals.
