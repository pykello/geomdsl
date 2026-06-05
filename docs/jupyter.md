# Jupyter guide

Install the package in the same Python environment used by Jupyter:

```bash
python3 -m pip install -e .
```

Load the extension:

```python
%load_ext geomdsl.jupyter
```

Use the `%%geom` cell magic:

```text
%%geom
scene(min=(-2,-2), max=(2,2), grid=true)
O = pt(0,0)
draw Circle(O, 1)
draw marker(O)
draw label(O, "$O$") @ {offset: vec(0.1, 0.1)}
```

## Options

```text
%%geom --dpi 200 --format svg
```

Supported options:

```text
--dpi DPI        Figure DPI.
--format FORMAT  Requested output/display format hint.
```

The Jupyter magic uses the same parser, evaluator, and Matplotlib renderer as the CLI and Python API.

## Troubleshooting

If `%load_ext geomdsl.jupyter` fails, check that the package was installed into the notebook kernel environment, not only into a shell environment.

If Matplotlib reports that its default config directory is not writable, set `MPLCONFIGDIR` to a writable directory before launching Jupyter:

```bash
mkdir -p /tmp/mplconfig
MPLCONFIGDIR=/tmp/mplconfig jupyter lab
```
