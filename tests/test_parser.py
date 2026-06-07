import pytest

from geomdsl.errors import GeomParseError
from geomdsl.parser import parse
from geomdsl.ast import Assignment, DrawStmt, FunctionDef, IncludeStmt


def test_parse_assignment_and_draw():
    program = parse("A = pt(1, 2)\ndraw marker(A)")
    assert isinstance(program.statements[0], Assignment)
    assert isinstance(program.statements[1], DrawStmt)


def test_parse_invalid_call_reports_error():
    with pytest.raises(GeomParseError):
        parse("A = pt(1,)")


def test_parse_include_statement():
    program = parse('include "common/styles.geom"\ndraw marker(pt(0,0))')
    assert isinstance(program.statements[0], IncludeStmt)
    assert program.statements[0].path == "common/styles.geom"


def test_parse_expression_function_definition():
    program = parse("def edge(A, B) = LineSegment(A, B)")
    stmt = program.statements[0]
    assert isinstance(stmt, FunctionDef)
    assert stmt.name == "edge"
    assert stmt.params == ["A", "B"]


def test_parse_function_rejects_duplicate_parameters():
    with pytest.raises(GeomParseError):
        parse("def bad(A, A) = A")
