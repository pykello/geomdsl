import pytest

from geomdsl import evaluate
from geomdsl.evaluator import Evaluator
from geomdsl.errors import GeomTypeError
from geomdsl.parser import parse
from geomdsl.values import Point, Vector


def env_for(source):
    evaluator = Evaluator()
    evaluator.eval_program(parse(source))
    return evaluator.env


def test_point_vector_arithmetic():
    env = env_for("A = pt(1, 2)\nB = pt(4, 6)\nv = B - A\nC = A + v")
    assert env["v"] == Vector(3, 4)
    assert env["C"] == Point(4, 6)


def test_point_plus_point_is_invalid():
    with pytest.raises(GeomTypeError):
        evaluate("A = pt(1, 2)\nB = pt(4, 6)\nbad = A + B")
