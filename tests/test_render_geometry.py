import matplotlib
matplotlib.use("Agg")

from matplotlib import pyplot as plt

from geomdsl import render
from geomdsl.errors import GeomValueError
from geomdsl.render.matplotlib_backend import sample_curve
from geomdsl.values import Point, Ray, Scene, Vector


def test_ray_clips_to_viewport_when_origin_is_outside():
    scene = Scene(min=Point(0, 0), max=Point(1, 1))
    points = sample_curve(Ray(Point(-1, 0.5), Vector(1, 0)), scene, 2)

    assert len(points) == 2
    assert abs(points[0].x - 0) < 1e-9
    assert abs(points[0].y - 0.5) < 1e-9
    assert abs(points[1].x - 1) < 1e-9
    assert abs(points[1].y - 0.5) < 1e-9


def test_scene_padding_expands_render_limits():
    fig = render("scene(min=(0,0), max=(1,1), padding=0.25)\ndraw marker(pt(0,0))")
    try:
        ax = fig.axes[0]
        assert ax.get_xlim() == (-0.25, 1.25)
        assert ax.get_ylim() == (-0.25, 1.25)
    finally:
        plt.close(fig)


def test_scene_padding_rejects_negative_values():
    try:
        render("scene(padding=-0.1)\ndraw marker(pt(0,0))")
    except GeomValueError as exc:
        assert "padding" in str(exc)
    else:
        raise AssertionError("expected GeomValueError")
