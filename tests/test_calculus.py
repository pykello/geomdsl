from geomdsl.evaluator import Evaluator
from geomdsl.parser import parse


def env_for(source):
    evaluator = Evaluator()
    evaluator.eval_program(parse(source))
    return evaluator.env


def test_circle_calculus_at_zero():
    env = env_for("""
c = Circle(pt(0,0), 1)
P = curve_at(c, 0)
v = velocity(c, 0)
T = unit_tangent(c, 0)
NL = normal_left(c, 0)
NR = normal_right(c, 0)
""")
    assert abs(env["P"].x - 1) < 1e-9
    assert abs(env["P"].y) < 1e-9
    assert abs(env["v"].x) < 1e-5
    assert abs(env["v"].y - 1) < 1e-5
    assert abs(env["T"].x) < 1e-5
    assert abs(env["T"].y - 1) < 1e-5
    assert abs(env["NL"].x + 1) < 1e-5
    assert abs(env["NR"].x - 1) < 1e-5
