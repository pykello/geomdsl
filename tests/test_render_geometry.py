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
