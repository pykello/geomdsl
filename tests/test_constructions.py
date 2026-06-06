from geomdsl.evaluator import Evaluator
from geomdsl.errors import GeomTypeError, GeomValueError
from geomdsl.parser import parse


def env_for(source):
    evaluator = Evaluator()
    evaluator.eval_program(parse(source))
    return evaluator.env


def test_line_construction_helpers():
    env = env_for("""
A = pt(0, 0)
B = pt(2, 0)
base = line_through(A, B)
L = parallel(base, pt(0, 1))
N = perpendicular(base, pt(1, 0))
M = perpendicular_bisector(A, B)
d = direction(LineSegment(A, B))
""")
    assert env["base"].a.x == 0
    assert env["base"].v.x == 2
    assert env["L"].a.y == 1
    assert env["L"].v.x == 2
    assert env["N"].v.x == 0
    assert env["N"].v.y == 2
    assert env["M"].a.x == 1
    assert env["M"].v.y == 2
    assert env["d"].x == 2
    assert env["d"].y == 0


def test_line_through_rejects_duplicate_points():
    try:
        env_for("L = line_through(pt(0,0), pt(0,0))")
    except GeomValueError as exc:
        assert "nonzero direction" in str(exc)
    else:
        raise AssertionError("expected GeomValueError")


def test_parallel_expects_line_like_curve():
    try:
        env_for("L = parallel(Circle(pt(0,0), 1), pt(1,0))")
    except GeomTypeError as exc:
        assert "line-like" in str(exc)
    else:
        raise AssertionError("expected GeomTypeError")
