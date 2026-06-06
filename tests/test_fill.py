import matplotlib
matplotlib.use("Agg")

from geomdsl import evaluate, render
from geomdsl.errors import GeomTypeError


FILL_SOURCE = """
scene(min=(-2,-2), max=(2,2))
c = Circle(pt(0,0), 1)
draw fill(c) @ {color: red, opacity: 0.25, z: 1}
draw c @ {color: red, weight: 2, z: 2}
"""


def test_fill_curve_drawable_style():
    scene = evaluate(FILL_SOURCE)
    fill = scene.drawables[0]
    assert fill.kind == "fill"
    assert fill.data["curve"].kind == "circle"
    assert fill.style.get("color") == "red"
    assert fill.style.get("opacity") == 0.25
    assert fill.style.get("z") == 1


def test_fill_rejects_open_curve():
    try:
        evaluate("draw fill(LineSegment(pt(0,0), pt(1,1)))")
    except GeomTypeError as exc:
        assert "closed curve" in str(exc)
    else:
        raise AssertionError("expected GeomTypeError")


def test_fill_polygon_constructor():
    scene = evaluate("draw fill(polygon(pt(0,0), pt(1,0), pt(0,1))) @ {color: blue, opacity: 0.3}")
    fill = scene.drawables[0]
    assert fill.kind == "fill"
    assert fill.data["curve"].kind == "polygon"
    assert fill.style.get("color") == "blue"


def test_quad_constructor_draws_outline():
    scene = evaluate("draw quad(pt(0,0), pt(1,0), pt(1,1), pt(0,1))")
    assert scene.drawables[0].kind == "curve"
    assert scene.drawables[0].data["curve"].kind == "polygon"


def test_fill_curve_exports_svg(tmp_path):
    out = tmp_path / "filled.svg"
    render(FILL_SOURCE, output=str(out))
    assert out.exists()
    text = out.read_text(encoding="utf-8", errors="ignore")
    assert "<svg" in text
    assert out.stat().st_size > 0


def test_cli_exports_filled_cube(tmp_path):
    import subprocess
    import sys

    out = tmp_path / "filled_cube.svg"
    result = subprocess.run(
        [sys.executable, "-m", "geomdsl.cli", "examples/filled_cube.geom", "-o", str(out)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert out.exists()
    assert out.stat().st_size > 0
