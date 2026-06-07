from geomdsl.evaluator import Evaluator
from geomdsl.parser import parse
from geomdsl.values import LineSegment, Point, PolygonCurve, Vector


def env_for(source):
    evaluator = Evaluator()
    evaluator.eval_program(parse(source))
    return evaluator.env


def test_projection_statement_projects_point_and_vector():
    env = env_for("""
projection(
  origin=pt(0, 0),
  x=vec(-1, 0),
  y=vec(1, 0),
  z=vec(0, 1),
  scale=2
)
P = project(pt3(1, 2, 3))
v = project(vec3(1, 2, 3))
""")
    assert env["P"] == Point(2, 6)
    assert env["v"] == Vector(2, 6)


def test_project_lowers_3d_segment_to_2d_segment():
    env = env_for("""
s = project(segment3(pt3(0, 0, 0), pt3(0, 2, 0)))
""")
    assert isinstance(env["s"], LineSegment)
    assert env["s"].a == Point(0, 0)
    assert env["s"].b == Point(2, 0)


def test_project_lowers_3d_segment_groups():
    env = env_for("""
segs = project(segments3(
  pt3(0, 0, 0), pt3(0, 1, 0),
  pt3(0, 0, 0), pt3(0, 0, 1)
))
""")
    assert len(env["segs"]) == 2
    assert isinstance(env["segs"][0], LineSegment)
    assert env["segs"][0].b == Point(1, 0)
    assert env["segs"][1].b == Point(0, 1)


def test_project_lowers_3d_quad_to_polygon_curve():
    env = env_for("""
face = project(quad3(
  pt3(0, 0, 0),
  pt3(0, 1, 0),
  pt3(0, 1, 1),
  pt3(0, 0, 1)
))
""")
    assert isinstance(env["face"], PolygonCurve)
    assert len(env["face"].points) == 4
    assert env["face"].points[0] == Point(0, 0)
    assert env["face"].points[2] == Point(1, 1)


def test_project_lowers_box_edge_groups():
    env = env_for("""
box = box3(pt3(0, 0, 0), vec3(1, 2, 3))
hidden = project(box_hidden3(box))
visible = project(box_visible3(box, 0.25))
""")
    assert len(env["hidden"]) == 5
    assert isinstance(env["hidden"][0], PolygonCurve)
    assert len(env["visible"]) == 2
    assert isinstance(env["visible"][0], PolygonCurve)
    assert isinstance(env["visible"][1], LineSegment)


def test_3d_point_and_vector_arithmetic_stays_separate():
    env = env_for("""
P = pt3(1, 2, 3)
v = vec3(4, 5, 6)
Q = P + v
w = Q - P
""")
    assert env["Q"].x == 5
    assert env["Q"].y == 7
    assert env["Q"].z == 9
    assert env["w"].x == 4
    assert env["w"].y == 5
    assert env["w"].z == 6


def test_draw_accepts_grouped_projected_values():
    evaluator = Evaluator()
    scene = evaluator.eval_program(parse("""
draw group(
  project(segment3(pt3(0, 0, 0), pt3(0, 1, 0))),
  marker(project(pt3(0, 0, 1)))
)
"""))
    assert len(scene.drawables) == 2
    assert scene.drawables[0].kind == "curve"
    assert scene.drawables[1].kind == "marker"


def test_arrow_on_centers_arrow_on_2d_segment():
    env = env_for("""
a = arrow_on(LineSegment(pt(0, 0), pt(4, 0)), 0.5, 1)
""")
    arrow = env["a"]
    assert arrow.kind == "arrow"
    assert arrow.data["start"] == Point(1.5, 0)
    assert arrow.data["vector"] == Vector(1, 0)


def test_arrow_on_projects_3d_segment_before_placing_arrow():
    env = env_for("""
a = arrow_on(segment3(pt3(0, 0, 0), pt3(0, 2, 0)), 0.5, 0.8)
""")
    arrow = env["a"]
    assert arrow.kind == "arrow"
    assert arrow.data["start"] == Point(0.6, 0)
    assert abs(arrow.data["vector"].x - 0.8) < 1e-12
    assert arrow.data["vector"].y == 0
