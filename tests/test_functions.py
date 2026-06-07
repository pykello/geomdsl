import pytest

from geomdsl.evaluator import Evaluator
from geomdsl.errors import GeomTypeError, GeomValueError
from geomdsl.parser import parse
from geomdsl.values import Drawable, LineSegment, Point, PolygonCurve, Vector


def env_for(source):
    evaluator = Evaluator()
    evaluator.eval_program(parse(source))
    return evaluator.env


def scene_for(source):
    evaluator = Evaluator()
    return evaluator.eval_program(parse(source))


def test_expression_function_returns_geometry_value():
    env = env_for("""
def edge(A, B) = LineSegment(A, B)

A = pt(0, 0)
B = pt(2, 1)
e = edge(A, B)
""")

    assert isinstance(env["e"], LineSegment)
    assert env["e"].a == Point(0, 0)
    assert env["e"].b == Point(2, 1)


def test_expression_function_can_return_grouped_drawables():
    scene = scene_for("""
def labeled_point(P, text) = group(marker(P), label(P, text))

draw labeled_point(pt(0, 0), "$O$")
""")

    assert len(scene.drawables) == 2
    assert isinstance(scene.drawables[0], Drawable)
    assert scene.drawables[0].kind == "marker"
    assert scene.drawables[1].kind == "label"


def test_function_parameters_are_local():
    env = env_for("""
def shift(P, v) = P + v

P = pt(0, 0)
Q = shift(P, vec(1, 2))
""")

    assert env["Q"] == Point(1, 2)
    assert "v" not in env


def test_function_uses_current_call_environment():
    env = env_for("""
def scaled(v) = scale*v

scale = 2
a = scaled(vec(1, 0))
scale = 3
b = scaled(vec(1, 0))
""")

    assert env["a"] == Vector(2, 0)
    assert env["b"] == Vector(3, 0)


def test_function_can_compose_existing_helpers():
    env = env_for("""
def tri(A, B, C) = polygon(A, B, C)

face = tri(pt(0, 0), pt(2, 0), pt(1, 1))
""")

    assert isinstance(env["face"], PolygonCurve)
    assert len(env["face"].points) == 3


def test_function_checks_arity():
    with pytest.raises(GeomTypeError):
        env_for("""
def edge(A, B) = LineSegment(A, B)
bad = edge(pt(0, 0))
""")


def test_function_cannot_redefine_builtin():
    with pytest.raises(GeomValueError):
        env_for("def pt(x, y) = vec(x, y)")
