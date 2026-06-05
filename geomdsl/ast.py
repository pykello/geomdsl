from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceSpan:
    line: int
    column: int
    index: int = 0


@dataclass
class Node:
    span: SourceSpan


@dataclass
class Program(Node):
    statements: list[Statement] = field(default_factory=list)


class Statement(Node):
    pass


@dataclass
class VersionStmt(Statement):
    version: str


@dataclass
class SceneStmt(Statement):
    args: dict[str, Expr]


@dataclass
class ExportStmt(Statement):
    args: dict[str, Expr]


@dataclass
class DefaultsStmt(Statement):
    entries: dict[str, StyleExpr]


@dataclass
class StyleStmt(Statement):
    name: str
    style: StyleExpr


@dataclass
class Assignment(Statement):
    name: str
    expr: Expr


@dataclass
class DrawStmt(Statement):
    expr: Expr
    style: StyleExpr | None = None


class Expr(Node):
    pass


@dataclass
class NumberExpr(Expr):
    value: float


@dataclass
class StringExpr(Expr):
    value: str


@dataclass
class BooleanExpr(Expr):
    value: bool


@dataclass
class VarExpr(Expr):
    name: str


@dataclass
class TupleExpr(Expr):
    items: list[Expr]


@dataclass
class UnaryExpr(Expr):
    op: str
    expr: Expr


@dataclass
class BinaryExpr(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class CallExpr(Expr):
    name: str
    args: list[Expr | ParamRange]


@dataclass
class IndexExpr(Expr):
    target: Expr
    index: Expr


@dataclass
class ParamRange(Node):
    name: str
    start: Expr
    end: Expr


class StyleExpr(Node):
    pass


@dataclass
class StyleRef(StyleExpr):
    name: str


@dataclass
class InlineStyle(StyleExpr):
    fields: dict[str, Expr]


def as_plain(obj: Any) -> Any:
    if isinstance(obj, SourceSpan):
        return {"line": obj.line, "column": obj.column}
    if isinstance(obj, list):
        return [as_plain(x) for x in obj]
    if isinstance(obj, dict):
        return {k: as_plain(v) for k, v in obj.items()}
    if hasattr(obj, "__dataclass_fields__"):
        data = {k: as_plain(v) for k, v in obj.__dict__.items()}
        data["type"] = obj.__class__.__name__
        return data
    return obj
