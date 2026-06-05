from geomdsl.evaluator import Evaluator
from geomdsl.parser import parse


def env_for(source):
    evaluator = Evaluator()
    evaluator.eval_program(parse(source))
    return evaluator.env


def test_numeric_arithmetic_and_functions():
    env = env_for("a = 1 + 2*3\nb = 2^3\nc = sin(pi/2)")
    assert env["a"] == 7
    assert env["b"] == 8
    assert abs(env["c"] - 1) < 1e-9
