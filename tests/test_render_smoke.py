import matplotlib
matplotlib.use("Agg")

from geomdsl import render


SOURCE = """
scene(min=(-2,-2), max=(2,2), grid=true)
O = pt(0,0)
c = Circle(O, 1)
draw c
draw marker(curve_at(c, 0))
"""


def test_render_returns_figure():
    fig = render(SOURCE)
    assert fig is not None


def test_render_exports_svg(tmp_path):
    out = tmp_path / "out.svg"
    render(SOURCE, output=str(out))
    assert out.exists()
    assert "<svg" in out.read_text(encoding="utf-8", errors="ignore")


def test_render_uses_export_dpi_when_not_overridden():
    fig = render("export(dpi=240)\ndraw marker(pt(0,0))")
    assert fig.dpi == 240
