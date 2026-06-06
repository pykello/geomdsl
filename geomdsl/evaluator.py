from __future__ import annotations

import math
from typing import Any

from . import ast as astmod
from .ast import (
    Assignment,
    BinaryExpr,
    BooleanExpr,
    CallExpr,
    DefaultsStmt,
    DrawStmt,
    ExportStmt,
    Expr,
    IndexExpr,
    InlineStyle,
    NumberExpr,
    ParamRange,
    Program,
    SceneStmt,
    StringExpr,
    StyleExpr,
    StyleRef,
    StyleStmt,
    TupleExpr,
    UnaryExpr,
    VarExpr,
)
from .errors import GeomNameError, GeomTypeError, GeomValueError
from .loader import load_program
from .values import Arc, Circle, Curve, Drawable, ExportConfig, Line, LineSegment, ParametricCurve, Point, PolygonCurve, Ray, Scene, Style, Vector


_IDENTIFIER_STRINGS = {
    "black", "white", "red", "blue", "green", "gray", "solid", "dashed", "dotted",
    "dot", "circle", "cross", "none", "center", "left", "right", "top", "bottom",
    "top-left", "top-right", "bottom-left", "bottom-right", "viewport", "equal", "auto",
    "svg", "png", "pdf",
}


class Evaluator:
    def __init__(self):
        self.scene = Scene()
        self.env: dict[str, Any] = {"pi": math.pi, "e": math.e}
        self.styles: dict[str, Style] = {}

    def eval_program(self, program: Program) -> Scene:
        for stmt in program.statements:
            self.eval_stmt(stmt)
        return self.scene

    def eval_stmt(self, stmt: astmod.Statement) -> None:
        if isinstance(stmt, Assignment):
            self.env[stmt.name] = self.eval_expr(stmt.expr)
            return
        if isinstance(stmt, SceneStmt):
            self.apply_scene(stmt)
            return
        if isinstance(stmt, ExportStmt):
            self.apply_export(stmt)
            return
        if isinstance(stmt, DefaultsStmt):
            for key, style_expr in stmt.entries.items():
                self.scene.defaults[key] = self.eval_style(style_expr)
            return
        if isinstance(stmt, StyleStmt):
            self.styles[stmt.name] = self.eval_style(stmt.style)
            return
        if isinstance(stmt, DrawStmt):
            self.eval_draw(stmt)
            return
        if isinstance(stmt, astmod.VersionStmt):
            return
        raise GeomValueError(f"Unsupported statement {stmt.__class__.__name__}.", stmt.span.line, stmt.span.column)

    def eval_expr(self, expr: Expr, env: dict[str, Any] | None = None) -> Any:
        old_env = self.env
        if env is not None:
            self.env = env
        try:
            return self._eval_expr(expr)
        finally:
            self.env = old_env

    def _eval_expr(self, expr: Expr) -> Any:
        if isinstance(expr, NumberExpr):
            return expr.value
        if isinstance(expr, StringExpr):
            return expr.value
        if isinstance(expr, BooleanExpr):
            return expr.value
        if isinstance(expr, TupleExpr):
            return tuple(self._eval_expr(x) for x in expr.items)
        if isinstance(expr, VarExpr):
            if expr.name in self.env:
                return self.env[expr.name]
            raise GeomNameError(f"Unknown name '{expr.name}'.", expr.span.line, expr.span.column)
        if isinstance(expr, UnaryExpr):
            value = self._eval_expr(expr.expr)
            if expr.op == "-" and is_number(value):
                return -value
            if expr.op == "-" and isinstance(value, Vector):
                return Vector(-value.x, -value.y)
            raise GeomTypeError(f"Cannot apply unary {expr.op} to {type_name(value)}.", expr.span.line, expr.span.column)
        if isinstance(expr, BinaryExpr):
            return self.eval_binary(expr)
        if isinstance(expr, CallExpr):
            return self.eval_call(expr)
        if isinstance(expr, IndexExpr):
            target = self._eval_expr(expr.target)
            index = self._eval_expr(expr.index)
            if not isinstance(target, list):
                raise GeomTypeError("Indexing expects List target.", expr.span.line, expr.span.column)
            if not is_number(index) or not float(index).is_integer():
                raise GeomTypeError("List index expects integer Number.", expr.span.line, expr.span.column)
            i = int(index)
            if i < 0 or i >= len(target):
                raise GeomValueError("List index is out of bounds.", expr.span.line, expr.span.column)
            return target[i]
        raise GeomValueError(f"Unsupported expression {expr.__class__.__name__}.", expr.span.line, expr.span.column)

    def eval_binary(self, expr: BinaryExpr) -> Any:
        left = self._eval_expr(expr.left)
        right = self._eval_expr(expr.right)
        op = expr.op
        if is_number(left) and is_number(right):
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                if right == 0:
                    raise GeomValueError("Division by zero is undefined.", expr.span.line, expr.span.column)
                return left / right
            if op == "^":
                return safe_power(left, right, expr)
        if isinstance(left, Point) and isinstance(right, Vector):
            if op == "+":
                return Point(left.x + right.x, left.y + right.y)
            if op == "-":
                return Point(left.x - right.x, left.y - right.y)
        if isinstance(left, Point) and isinstance(right, Point) and op == "-":
            return Vector(left.x - right.x, left.y - right.y)
        if isinstance(left, Vector) and isinstance(right, Vector):
            if op == "+":
                return Vector(left.x + right.x, left.y + right.y)
            if op == "-":
                return Vector(left.x - right.x, left.y - right.y)
        if is_number(left) and isinstance(right, Vector) and op == "*":
            return Vector(left * right.x, left * right.y)
        if isinstance(left, Vector) and is_number(right):
            if op == "*":
                return Vector(left.x * right, left.y * right)
            if op == "/":
                if right == 0:
                    raise GeomValueError("Division by zero is undefined.", expr.span.line, expr.span.column)
                return Vector(left.x / right, left.y / right)
        raise GeomTypeError(f"Cannot {op_name(op)} {type_name(left)} and {type_name(right)}.", expr.span.line, expr.span.column)

    def eval_call(self, expr: CallExpr) -> Any:
        name = expr.name
        if name == "ParametricCurve":
            if len(expr.args) != 2 or not isinstance(expr.args[1], ParamRange) or isinstance(expr.args[0], ParamRange):
                raise GeomTypeError("ParametricCurve(PointExpr, t = start..end) expected.", expr.span.line, expr.span.column)
            pr = expr.args[1]
            start = self.eval_number(pr.start)
            end = self.eval_number(pr.end)
            return ParametricCurve(expr.args[0], pr.name, start, end, dict(self.env))
        args = [self.eval_param_arg(a) for a in expr.args]
        return self.call_builtin(name, args, expr)

    def eval_param_arg(self, arg: Expr | ParamRange) -> Any:
        if isinstance(arg, ParamRange):
            raise GeomTypeError("Parameter ranges are only valid in ParametricCurve.", arg.span.line, arg.span.column)
        return self._eval_expr(arg)

    def call_builtin(self, name: str, args: list[Any], expr: CallExpr) -> Any:
        if name == "pt":
            require_len(name, args, 2, expr)
            return Point(require_number(args[0], expr), require_number(args[1], expr))
        if name == "vec":
            require_len(name, args, 2, expr)
            return Vector(require_number(args[0], expr), require_number(args[1], expr))
        if name in {"sin", "cos", "tan", "sqrt", "exp", "log", "abs"}:
            require_len(name, args, 1, expr)
            value = require_number(args[0], expr)
            return safe_math_call(name, value, expr)
        if name in {"min", "max"}:
            require_len(name, args, 2, expr)
            a = require_number(args[0], expr)
            b = require_number(args[1], expr)
            return min(a, b) if name == "min" else max(a, b)
        if name == "dot":
            u, v = require_vectors(name, args, expr)
            return u.x * v.x + u.y * v.y
        if name == "cross":
            u, v = require_vectors(name, args, expr)
            return u.x * v.y - u.y * v.x
        if name == "norm":
            require_len(name, args, 1, expr)
            v = require_vector(args[0], expr)
            return math.sqrt(v.x * v.x + v.y * v.y)
        if name == "unit":
            require_len(name, args, 1, expr)
            v = require_vector(args[0], expr)
            n = math.sqrt(v.x * v.x + v.y * v.y)
            if n == 0:
                raise GeomValueError("unit(vec(0, 0)) is undefined.", expr.span.line, expr.span.column)
            return Vector(v.x / n, v.y / n)
        if name == "rotate":
            require_len(name, args, 2, expr)
            v = require_vector(args[0], expr)
            theta = require_number(args[1], expr)
            return Vector(v.x * math.cos(theta) - v.y * math.sin(theta), v.x * math.sin(theta) + v.y * math.cos(theta))
        if name == "rotate90":
            require_len(name, args, 1, expr)
            v = require_vector(args[0], expr)
            return Vector(-v.y, v.x)
        if name == "distance":
            a, b = require_points(name, args, expr)
            return math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)
        if name == "midpoint":
            a, b = require_points(name, args, expr)
            return Point(a.x + 0.5 * (b.x - a.x), a.y + 0.5 * (b.y - a.y))
        if name == "direction":
            require_len(name, args, 1, expr)
            return line_like_direction(args[0], expr)
        if name == "line_through":
            a, b = require_points(name, args, expr)
            return Line(a, nonzero_vector(Vector(b.x - a.x, b.y - a.y), expr))
        if name == "parallel":
            require_len(name, args, 2, expr)
            p = require_point(args[1], expr)
            return Line(p, line_like_direction(args[0], expr))
        if name == "perpendicular":
            require_len(name, args, 2, expr)
            p = require_point(args[1], expr)
            v = line_like_direction(args[0], expr)
            return Line(p, Vector(-v.y, v.x))
        if name == "perpendicular_bisector":
            a, b = require_points(name, args, expr)
            v = nonzero_vector(Vector(b.x - a.x, b.y - a.y), expr)
            m = Point(a.x + 0.5 * v.x, a.y + 0.5 * v.y)
            return Line(m, Vector(-v.y, v.x))
        if name == "LineSegment":
            a, b = require_points(name, args, expr)
            return LineSegment(a, b)
        if name == "polygon":
            if len(args) < 3:
                raise GeomTypeError("polygon(Point, Point, Point, ...) expected at least 3 points.", expr.span.line, expr.span.column)
            return PolygonCurve([require_point(arg, expr) for arg in args])
        if name == "quad":
            require_len(name, args, 4, expr)
            return PolygonCurve([require_point(arg, expr) for arg in args])
        if name == "Line":
            require_len(name, args, 2, expr)
            return Line(require_point(args[0], expr), require_vector(args[1], expr))
        if name == "Ray":
            require_len(name, args, 2, expr)
            return Ray(require_point(args[0], expr), require_vector(args[1], expr))
        if name == "Circle":
            require_len(name, args, 2, expr)
            return Circle(require_point(args[0], expr), require_radius(args[1], expr))
        if name == "circle_through":
            c, p = require_points(name, args, expr)
            r = distance_between(c, p)
            if r < 1e-12:
                raise GeomValueError("circle_through requires distinct points.", expr.span.line, expr.span.column)
            return Circle(c, r)
        if name == "circle_with_diameter":
            a, b = require_points(name, args, expr)
            r = 0.5 * distance_between(a, b)
            if r < 1e-12:
                raise GeomValueError("circle_with_diameter requires distinct points.", expr.span.line, expr.span.column)
            center = Point(a.x + 0.5 * (b.x - a.x), a.y + 0.5 * (b.y - a.y))
            return Circle(center, r)
        if name == "Arc":
            require_len(name, args, 4, expr)
            return Arc(require_point(args[0], expr), require_radius(args[1], expr), require_number(args[2], expr), require_number(args[3], expr))
        if name == "intersections":
            require_len(name, args, 2, expr)
            return curve_intersections(args[0], args[1], expr)
        if name == "intersect":
            require_len(name, args, 2, expr)
            points = curve_intersections(args[0], args[1], expr)
            if len(points) != 1:
                raise GeomValueError(f"intersect expected exactly one point, got {len(points)}.", expr.span.line, expr.span.column)
            return points[0]
        if name == "nearest":
            require_len(name, args, 2, expr)
            points = require_point_list(name, args[0], expr)
            target = require_point(args[1], expr)
            return min(points, key=lambda p: distance_between(p, target))
        if name == "leftmost":
            require_len(name, args, 1, expr)
            points = require_point_list(name, args[0], expr)
            return min(points, key=lambda p: (p.x, p.y))
        if name == "rightmost":
            require_len(name, args, 1, expr)
            points = require_point_list(name, args[0], expr)
            return max(points, key=lambda p: (p.x, -p.y))
        if name == "topmost":
            require_len(name, args, 1, expr)
            points = require_point_list(name, args[0], expr)
            return max(points, key=lambda p: (p.y, -p.x))
        if name == "bottommost":
            require_len(name, args, 1, expr)
            points = require_point_list(name, args[0], expr)
            return min(points, key=lambda p: (p.y, p.x))
        if name == "curve_at":
            require_len(name, args, 2, expr)
            return curve_point(require_curve(args[0], expr), require_number(args[1], expr), self, expr)
        if name == "velocity":
            require_len(name, args, 2, expr)
            return velocity(require_curve(args[0], expr), require_number(args[1], expr), self, expr)
        if name == "speed":
            require_len(name, args, 2, expr)
            v = velocity(require_curve(args[0], expr), require_number(args[1], expr), self, expr)
            return math.sqrt(v.x * v.x + v.y * v.y)
        if name == "unit_tangent":
            require_len(name, args, 2, expr)
            return unit_vector(velocity(require_curve(args[0], expr), require_number(args[1], expr), self, expr), expr)
        if name == "normal_left":
            require_len(name, args, 2, expr)
            t = unit_vector(velocity(require_curve(args[0], expr), require_number(args[1], expr), self, expr), expr)
            return Vector(-t.y, t.x)
        if name == "normal_right":
            require_len(name, args, 2, expr)
            n = self.call_builtin("normal_left", args, expr)
            return Vector(-n.x, -n.y)
        if name == "tangent_line":
            require_len(name, args, 2, expr)
            c = require_curve(args[0], expr)
            t = require_number(args[1], expr)
            return Line(curve_point(c, t, self, expr), velocity(c, t, self, expr))
        if name == "normal_line":
            require_len(name, args, 2, expr)
            c = require_curve(args[0], expr)
            t = require_number(args[1], expr)
            n = self.call_builtin("normal_left", args, expr)
            return Line(curve_point(c, t, self, expr), n)
        if name == "marker":
            require_len(name, args, 1, expr)
            return Drawable("marker", {"point": require_point(args[0], expr)})
        if name == "arrow":
            require_len(name, args, 2, expr)
            return Drawable("arrow", {"start": require_point(args[0], expr), "vector": require_vector(args[1], expr)})
        if name == "arrow_between":
            a, b = require_points(name, args, expr)
            return Drawable("arrow", {"start": a, "vector": Vector(b.x - a.x, b.y - a.y)})
        if name == "label":
            require_len(name, args, 2, expr)
            if not isinstance(args[1], str):
                raise GeomTypeError("label(Point, String) expected.", expr.span.line, expr.span.column)
            return Drawable("label", {"point": require_point(args[0], expr), "text": args[1]})
        if name == "fill":
            require_len(name, args, 1, expr)
            return Drawable("fill", {"curve": require_fillable_curve(args[0], expr, self)})
        raise GeomNameError(f"Unknown function '{name}'.", expr.span.line, expr.span.column)

    def eval_draw(self, stmt: DrawStmt) -> None:
        value = self.eval_expr(stmt.expr)
        style = self.eval_style(stmt.style) if stmt.style else None
        if isinstance(value, Curve):
            drawable = Drawable("curve", {"curve": value})
        elif isinstance(value, Drawable):
            drawable = value
        else:
            raise GeomTypeError(f"draw expected Curve or Drawable, got {type_name(value)}.", stmt.span.line, stmt.span.column)
        drawable.style = self.scene.default_style_for(drawable.kind).merged(drawable.style).merged(style)
        self.scene.append(drawable)

    def eval_style(self, style_expr: StyleExpr | None) -> Style:
        if style_expr is None:
            return Style()
        if isinstance(style_expr, StyleRef):
            if style_expr.name in self.styles:
                return self.styles[style_expr.name]
            raise GeomNameError(f"Unknown style '{style_expr.name}'.", style_expr.span.line, style_expr.span.column)
        if isinstance(style_expr, InlineStyle):
            return Style({k: self.eval_style_value(k, v) for k, v in style_expr.fields.items()})
        raise GeomTypeError("Invalid style expression.", style_expr.span.line, style_expr.span.column)

    def eval_style_value(self, field: str, expr: Expr) -> Any:
        if isinstance(expr, VarExpr) and expr.name not in self.env:
            value = expr.name
            validate_style_enum(field, value, expr)
            return value
        value = self.eval_expr(expr)
        if field in {"weight", "opacity", "size", "arrow_size", "font_size", "z", "samples"}:
            return require_number(value, expr)
        if field in {"visible", "arrow_head"} and not isinstance(value, bool):
            raise GeomTypeError(f"Style field '{field}' expects Boolean.", expr.span.line, expr.span.column)
        if field == "offset" and not isinstance(value, Vector):
            raise GeomTypeError("Style field 'offset' expects Vector.", expr.span.line, expr.span.column)
        validate_style_enum(field, value, expr)
        return value

    def apply_scene(self, stmt: SceneStmt) -> None:
        for key, expr in stmt.args.items():
            if key in {"min", "max"}:
                setattr(self.scene, key, tuple_point(self.eval_expr(expr), expr))
            elif key == "size":
                self.scene.size = tuple_pair(self.eval_expr(expr), expr)
            elif key in {"grid", "axes"}:
                value = self.eval_expr(expr)
                if not isinstance(value, bool):
                    raise GeomTypeError(f"scene {key} expects Boolean.", expr.span.line, expr.span.column)
                setattr(self.scene, key, value)
            elif key == "grid_step":
                setattr(self.scene, key, self.eval_number(expr))
            elif key == "padding":
                padding = self.eval_number(expr)
                if padding < 0:
                    raise GeomValueError("scene padding must be nonnegative.", expr.span.line, expr.span.column)
                self.scene.padding = padding
            elif key in {"aspect", "background"}:
                setattr(self.scene, key, self.eval_identifier_or_value(expr))
            elif key in {"grid_style", "axis_style"}:
                setattr(self.scene, key, self.eval_style_value_or_ref(expr))
            else:
                raise GeomValueError(f"Unknown scene field '{key}'.", expr.span.line, expr.span.column)

    def apply_export(self, stmt: ExportStmt) -> None:
        data = self.scene.export
        for key, expr in stmt.args.items():
            if key == "format":
                data.format = self.eval_identifier_or_value(expr)
            elif key == "dpi":
                data.dpi = int(self.eval_number(expr))
            elif key == "transparent":
                value = self.eval_expr(expr)
                if not isinstance(value, bool):
                    raise GeomTypeError("export transparent expects Boolean.", expr.span.line, expr.span.column)
                data.transparent = value
            else:
                raise GeomValueError(f"Unknown export field '{key}'.", expr.span.line, expr.span.column)

    def eval_identifier_or_value(self, expr: Expr) -> Any:
        if isinstance(expr, VarExpr) and expr.name not in self.env:
            return expr.name
        return self.eval_expr(expr)

    def eval_style_value_or_ref(self, expr: Expr) -> Style:
        if isinstance(expr, VarExpr):
            if expr.name in self.styles:
                return self.styles[expr.name]
            if expr.name in self.env and isinstance(self.env[expr.name], Style):
                return self.env[expr.name]
        value = self.eval_expr(expr)
        if isinstance(value, Style):
            return value
        raise GeomTypeError("Expected style value.", expr.span.line, expr.span.column)

    def eval_number(self, expr: Expr) -> float:
        return require_number(self.eval_expr(expr), expr)


def evaluate(source: str, *, base_path: str | None = None) -> Scene:
    return Evaluator().eval_program(load_program(source, base_path=base_path))


def curve_point(curve: Curve, t: float, evaluator: Evaluator, expr: CallExpr) -> Point:
    try:
        return curve.point_at(t, evaluator)
    except GeomValueError:
        raise
    except Exception as exc:
        raise GeomValueError(str(exc), expr.span.line, expr.span.column) from exc


def velocity(curve: Curve, t: float, evaluator: Evaluator, expr: CallExpr) -> Vector:
    h = 1e-5
    p1 = curve_point(curve, t + h, evaluator, expr)
    p0 = curve_point(curve, t - h, evaluator, expr)
    return Vector((p1.x - p0.x) / (2.0 * h), (p1.y - p0.y) / (2.0 * h))


def unit_vector(v: Vector, expr: CallExpr) -> Vector:
    n = math.sqrt(v.x * v.x + v.y * v.y)
    if n == 0:
        raise GeomValueError("unit tangent is undefined for zero velocity.", expr.span.line, expr.span.column)
    return Vector(v.x / n, v.y / n)


def distance_between(a: Point, b: Point) -> float:
    return math.hypot(b.x - a.x, b.y - a.y)


def safe_power(left: float, right: float, expr: Expr) -> float:
    try:
        result = left ** right
    except (OverflowError, ValueError, ZeroDivisionError) as exc:
        raise GeomValueError("Exponentiation is undefined for these values.", expr.span.line, expr.span.column) from exc
    if not is_number(result):
        raise GeomValueError("Exponentiation result is not a real number.", expr.span.line, expr.span.column)
    return float(result)


def safe_math_call(name: str, value: float, expr: Expr) -> float:
    try:
        result = abs(value) if name == "abs" else getattr(math, name)(value)
    except (OverflowError, ValueError, ZeroDivisionError) as exc:
        raise GeomValueError(f"{name} is undefined for this value.", expr.span.line, expr.span.column) from exc
    if not is_number(result):
        raise GeomValueError(f"{name} result is not a real number.", expr.span.line, expr.span.column)
    return float(result)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def type_name(value: Any) -> str:
    if is_number(value):
        return "Number"
    if isinstance(value, bool):
        return "Boolean"
    if isinstance(value, str):
        return "String"
    return value.__class__.__name__


def op_name(op: str) -> str:
    return {"+": "add", "-": "subtract", "*": "multiply", "/": "divide", "^": "exponentiate"}.get(op, op)


def require_len(name: str, args: list[Any], n: int, expr: CallExpr) -> None:
    if len(args) != n:
        raise GeomTypeError(f"{name} expected {n} arguments, got {len(args)}.", expr.span.line, expr.span.column)


def require_number(value: Any, expr: Expr) -> float:
    if not is_number(value):
        raise GeomTypeError(f"Expected Number, got {type_name(value)}.", expr.span.line, expr.span.column)
    return float(value)


def require_radius(value: Any, expr: Expr) -> float:
    radius = require_number(value, expr)
    if radius < 0:
        raise GeomValueError("Radius must be nonnegative.", expr.span.line, expr.span.column)
    return radius


def require_point(value: Any, expr: Expr) -> Point:
    if not isinstance(value, Point):
        raise GeomTypeError(f"Expected Point, got {type_name(value)}.", expr.span.line, expr.span.column)
    return value


def require_vector(value: Any, expr: Expr) -> Vector:
    if not isinstance(value, Vector):
        raise GeomTypeError(f"Expected Vector, got {type_name(value)}.", expr.span.line, expr.span.column)
    return value


def require_curve(value: Any, expr: Expr) -> Curve:
    if not isinstance(value, Curve):
        raise GeomTypeError(f"Expected Curve, got {type_name(value)}.", expr.span.line, expr.span.column)
    return value


def require_point_list(name: str, value: Any, expr: Expr) -> list[Point]:
    if not isinstance(value, list) or not all(isinstance(p, Point) for p in value):
        raise GeomTypeError(f"{name} expects List[Point].", expr.span.line, expr.span.column)
    if not value:
        raise GeomValueError(f"{name} requires at least one point.", expr.span.line, expr.span.column)
    return value


def require_fillable_curve(value: Any, expr: Expr, evaluator: Evaluator) -> Curve:
    curve = require_curve(value, expr)
    if isinstance(curve, Circle):
        return curve
    if isinstance(curve, PolygonCurve):
        return curve
    if isinstance(curve, Arc) and abs(abs(curve.theta1 - curve.theta0) - 2.0 * math.pi) < 1e-9:
        return curve
    if isinstance(curve, ParametricCurve):
        start, end = curve.domain()
        p0 = curve.point_at(start, evaluator)
        p1 = curve.point_at(end, evaluator)
        if math.hypot(p1.x - p0.x, p1.y - p0.y) < 1e-6:
            return curve
    raise GeomTypeError("fill(Curve) requires a closed curve.", expr.span.line, expr.span.column)


def nonzero_vector(v: Vector, expr: Expr) -> Vector:
    if math.hypot(v.x, v.y) < 1e-12:
        raise GeomValueError("Expected nonzero direction vector.", expr.span.line, expr.span.column)
    return v


def line_like_direction(value: Any, expr: Expr) -> Vector:
    if isinstance(value, Line):
        return nonzero_vector(value.v, expr)
    if isinstance(value, Ray):
        return nonzero_vector(value.v, expr)
    if isinstance(value, LineSegment):
        return nonzero_vector(Vector(value.b.x - value.a.x, value.b.y - value.a.y), expr)
    raise GeomTypeError(f"Expected line-like Curve, got {type_name(value)}.", expr.span.line, expr.span.column)


def curve_intersections(a: Any, b: Any, expr: Expr) -> list[Point]:
    if is_line_like(a) and is_line_like(b):
        return line_line_intersections(a, b, expr)
    if is_line_like(a) and isinstance(b, Circle):
        return line_circle_intersections(a, b, expr)
    if isinstance(a, Circle) and is_line_like(b):
        return line_circle_intersections(b, a, expr)
    if isinstance(a, Circle) and isinstance(b, Circle):
        return circle_circle_intersections(a, b, expr)
    raise GeomTypeError("intersections supports line-like curves and circles.", expr.span.line, expr.span.column)


def is_line_like(value: Any) -> bool:
    return isinstance(value, (Line, Ray, LineSegment))


def line_like_point(value: Any, expr: Expr) -> Point:
    if isinstance(value, (Line, Ray, LineSegment)):
        return value.a
    raise GeomTypeError(f"Expected line-like Curve, got {type_name(value)}.", expr.span.line, expr.span.column)


def line_like_contains(value: Any, p: Point, expr: Expr) -> bool:
    a = line_like_point(value, expr)
    v = line_like_direction(value, expr)
    w = Vector(p.x - a.x, p.y - a.y)
    if abs(cross_vectors(w, v)) > 1e-7:
        return False
    if isinstance(value, Line):
        return True
    dot = dot_vectors(w, v)
    if isinstance(value, Ray):
        return dot >= -1e-9
    return -1e-9 <= dot <= dot_vectors(v, v) + 1e-9


def line_line_intersections(a: Any, b: Any, expr: Expr) -> list[Point]:
    p = line_like_point(a, expr)
    r = line_like_direction(a, expr)
    q = line_like_point(b, expr)
    s = line_like_direction(b, expr)
    qp = Vector(q.x - p.x, q.y - p.y)
    denom = cross_vectors(r, s)
    if abs(denom) < 1e-12:
        if abs(cross_vectors(qp, r)) < 1e-9:
            raise GeomValueError("intersections has infinitely many points.", expr.span.line, expr.span.column)
        return []
    t = cross_vectors(qp, s) / denom
    point = Point(p.x + t * r.x, p.y + t * r.y)
    if line_like_contains(a, point, expr) and line_like_contains(b, point, expr):
        return [point]
    return []


def line_circle_intersections(line: Any, circle: Circle, expr: Expr) -> list[Point]:
    p = line_like_point(line, expr)
    v = line_like_direction(line, expr)
    f = Vector(p.x - circle.center.x, p.y - circle.center.y)
    a = dot_vectors(v, v)
    b = 2.0 * dot_vectors(f, v)
    c = dot_vectors(f, f) - circle.radius * circle.radius
    disc = b * b - 4.0 * a * c
    if disc < -1e-9:
        return []
    if abs(disc) <= 1e-9:
        roots = [-b / (2.0 * a)]
    else:
        root = math.sqrt(max(0.0, disc))
        roots = [(-b - root) / (2.0 * a), (-b + root) / (2.0 * a)]
    points = [Point(p.x + t * v.x, p.y + t * v.y) for t in roots]
    return unique_points([q for q in points if line_like_contains(line, q, expr)])


def circle_circle_intersections(a: Circle, b: Circle, expr: Expr) -> list[Point]:
    dx = b.center.x - a.center.x
    dy = b.center.y - a.center.y
    d = math.hypot(dx, dy)
    if d < 1e-12:
        if abs(a.radius - b.radius) < 1e-9:
            raise GeomValueError("intersections has infinitely many points.", expr.span.line, expr.span.column)
        return []
    if d > a.radius + b.radius + 1e-9:
        return []
    if d < abs(a.radius - b.radius) - 1e-9:
        return []
    along = (a.radius * a.radius - b.radius * b.radius + d * d) / (2.0 * d)
    h2 = a.radius * a.radius - along * along
    if h2 < -1e-9:
        return []
    ux = dx / d
    uy = dy / d
    base = Point(a.center.x + along * ux, a.center.y + along * uy)
    if abs(h2) <= 1e-9:
        return [base]
    h = math.sqrt(max(0.0, h2))
    return [
        Point(base.x - h * uy, base.y + h * ux),
        Point(base.x + h * uy, base.y - h * ux),
    ]


def dot_vectors(a: Vector, b: Vector) -> float:
    return a.x * b.x + a.y * b.y


def cross_vectors(a: Vector, b: Vector) -> float:
    return a.x * b.y - a.y * b.x


def unique_points(points: list[Point]) -> list[Point]:
    unique: list[Point] = []
    for p in points:
        if not any(distance_between(p, q) < 1e-9 for q in unique):
            unique.append(p)
    return unique


def require_points(name: str, args: list[Any], expr: CallExpr) -> tuple[Point, Point]:
    require_len(name, args, 2, expr)
    return require_point(args[0], expr), require_point(args[1], expr)


def require_vectors(name: str, args: list[Any], expr: CallExpr) -> tuple[Vector, Vector]:
    require_len(name, args, 2, expr)
    return require_vector(args[0], expr), require_vector(args[1], expr)


def tuple_pair(value: Any, expr: Expr) -> tuple[float, float]:
    if not isinstance(value, tuple) or len(value) != 2:
        raise GeomTypeError("Expected tuple pair.", expr.span.line, expr.span.column)
    return require_number(value[0], expr), require_number(value[1], expr)


def tuple_point(value: Any, expr: Expr) -> Point:
    x, y = tuple_pair(value, expr)
    return Point(x, y)


def validate_style_enum(field: str, value: Any, expr: Expr) -> None:
    choices = {
        "pattern": {"solid", "dashed", "dotted"},
        "marker": {"dot", "circle", "cross", "none"},
        "anchor": {"center", "left", "right", "top", "bottom", "top-left", "top-right", "bottom-left", "bottom-right"},
        "clip": {"viewport", "none"},
    }
    if field == "color":
        if isinstance(value, str) and (value in {"black", "white", "red", "blue", "green", "gray"} or value.startswith("#")):
            return
        raise GeomTypeError("Style field 'color' expects a named color or hex color string.", expr.span.line, expr.span.column)
    if field not in choices:
        return
    if not isinstance(value, str) or value not in choices[field]:
        allowed = ", ".join(sorted(choices[field]))
        raise GeomTypeError(f"Style field '{field}' expects one of: {allowed}.", expr.span.line, expr.span.column)
