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


def test_circle_construction_helpers():
    env = env_for("""
A = pt(0, 0)
B = pt(3, 4)
c1 = circle_through(A, B)
c2 = circle_with_diameter(A, B)
""")
    assert env["c1"].center.x == 0
    assert env["c1"].radius == 5
    assert env["c2"].center.x == 1.5
    assert env["c2"].center.y == 2
    assert env["c2"].radius == 2.5


def test_circle_through_rejects_duplicate_points():
    try:
        env_for("c = circle_through(pt(0,0), pt(0,0))")
    except GeomValueError as exc:
        assert "distinct points" in str(exc)
    else:
        raise AssertionError("expected GeomValueError")


def test_intersect_returns_single_point():
    env = env_for("""
L1 = line_through(pt(0, 0), pt(2, 0))
L2 = perpendicular(L1, pt(1, 0))
P = intersect(L1, L2)
""")
    assert abs(env["P"].x - 1) < 1e-9
    assert abs(env["P"].y) < 1e-9


def test_intersections_returns_circle_line_points():
    env = env_for("""
c = Circle(pt(0, 0), 1)
L = Line(pt(0, 0), vec(1, 0))
Ps = intersections(c, L)
A = Ps[0]
B = Ps[1]
""")
    assert len(env["Ps"]) == 2
    assert abs(env["A"].x + 1) < 1e-9
    assert abs(env["A"].y) < 1e-9
    assert abs(env["B"].x - 1) < 1e-9
    assert abs(env["B"].y) < 1e-9


def test_intersections_respects_line_segment_bounds():
    env = env_for("""
seg = LineSegment(pt(0, 0), pt(1, 0))
c = Circle(pt(0, 0), 2)
Ps = intersections(seg, c)
""")
    assert env["Ps"] == []


def test_intersect_rejects_multiple_points():
    try:
        env_for("P = intersect(Circle(pt(0,0), 1), Line(pt(0,0), vec(1,0)))")
    except GeomValueError as exc:
        assert "exactly one point" in str(exc)
    else:
        raise AssertionError("expected GeomValueError")


def test_intersections_rejects_coincident_lines():
    try:
        env_for("""
L1 = Line(pt(0, 0), vec(1, 0))
L2 = Line(pt(1, 0), vec(2, 0))
Ps = intersections(L1, L2)
""")
    except GeomValueError as exc:
        assert "infinitely many" in str(exc)
    else:
        raise AssertionError("expected GeomValueError")


def test_point_selection_helpers():
    env = env_for("""
c1 = Circle(pt(0, 0), 1)
c2 = Circle(pt(1, 0), 1)
Ps = intersections(c1, c2)
T = topmost(Ps)
B = bottommost(Ps)
N = nearest(Ps, pt(0.5, 1))
""")
    assert len(env["Ps"]) == 2
    assert env["T"].y > 0
    assert env["B"].y < 0
    assert env["N"] == env["T"]


def test_point_selection_rejects_empty_list():
    try:
        env_for("""
c1 = Circle(pt(0, 0), 1)
c2 = Circle(pt(5, 0), 1)
P = topmost(intersections(c1, c2))
""")
    except GeomValueError as exc:
        assert "at least one point" in str(exc)
    else:
        raise AssertionError("expected GeomValueError")
