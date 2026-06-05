import pytest

from geomdsl.errors import GeomParseError
from geomdsl.parser import parse
from geomdsl.ast import Assignment, DrawStmt


def test_parse_assignment_and_draw():
    program = parse("A = pt(1, 2)\ndraw marker(A)")
    assert isinstance(program.statements[0], Assignment)
    assert isinstance(program.statements[1], DrawStmt)


def test_parse_invalid_call_reports_error():
    with pytest.raises(GeomParseError):
        parse("A = pt(1,)")
