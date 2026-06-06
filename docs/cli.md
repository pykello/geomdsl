# CLI guide

Run the CLI from the repository root without installing:

```bash
python3 -m geomdsl.cli input.geom -o output.svg
```

After editable install:

```bash
geomdsl input.geom -o output.svg
```

## Export examples

```bash
python3 -m geomdsl.cli examples/circle_tangent.geom -o /tmp/circle.svg
python3 -m geomdsl.cli examples/circle_tangent.geom -o /tmp/circle.png --dpi 300
python3 -m geomdsl.cli examples/circle_tangent.geom -o /tmp/circle.pdf
```

The export format is inferred from the output extension unless `--format` is provided.

```bash
python3 -m geomdsl.cli examples/circle_tangent.geom -o /tmp/circle.out --format svg
```

Input files may use file-relative includes:

```text
include "../common/construction_styles.geom"
```

CLI render, `--show`, `--dump-ast`, and `--dump-scene` all expand
includes relative to the input file.

## Options

```text
-o, --output PATH     Output image path.
--format FORMAT       Override output format: svg, png, or pdf.
--dpi DPI             Output DPI for raster formats and Matplotlib figure setup.
--show                Display with Matplotlib instead of writing a file.
--dump-ast            Print parsed AST and exit.
--dump-scene          Print evaluated scene and exit.
```

## Diagnostics

Parse, name, type, value, and render errors are reported on stderr with a nonzero exit code.

Example invalid input:

```text
A = pt(0, 0)
B = pt(1, 1)
bad = A + B
```

Expected diagnostic:

```text
TypeError at line 3, column 9:
Cannot add Point and Point.
```
