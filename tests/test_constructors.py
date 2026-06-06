from geomdsl.evaluator import Evaluator
from geomdsl.parser import parse


def env_for(source):
    evaluator = Evaluator()
    evaluator.eval_program(parse(source))
    return evaluator.env


def test_circle_curve_at():
    env = env_for("c = Circle(pt(0,0), 1)\nP = curve_at(c, 0)")
    assert abs(env["P"].x - 1) < 1e-9
    assert abs(env["P"].y) < 1e-9


def test_line_segment_curve_at():
    env = env_for("c = LineSegment(pt(0,0), pt(2,2))\nP = curve_at(c, 0.5)")
    assert abs(env["P"].x - 1) < 1e-9
    assert abs(env["P"].y - 1) < 1e-9


def test_graph_constructs_parametric_function_curve():
    env = env_for("c = graph(sin(x), x = 0..pi)\nP = curve_at(c, pi/2)")
    assert abs(env["P"].x - 0.5 * 3.141592653589793) < 1e-9
    assert abs(env["P"].y - 1) < 1e-9
