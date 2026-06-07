from __future__ import annotations

import math
from dataclasses import dataclass
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
    FunctionDef,
    IndexExpr,
    InlineStyle,
    NumberExpr,
    ParamRange,
    Program,
    ProjectionStmt,
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
from .values import Arc, Box3, Circle, Curve, Drawable, ExportConfig, Line, LineSegment, LineSegment3, ParametricCurve, Point, Point3, Polygon3, PolygonCurve, Projection, Ray, Scene, Style, Vector, Vector3


_IDENTIFIER_STRINGS = {
    "black", "white", "red", "blue", "green", "gray", "solid", "dashed", "dotted",
    "dot", "circle", "cross", "none", "center", "left", "right", "top", "bottom",
    "top-left", "top-right", "bottom-left", "bottom-right", "viewport", "equal", "auto",
    "svg", "png", "pdf",
}


_BUILTIN_FUNCTIONS = {
    "Arc", "Circle", "Line", "LineSegment", "LineSegment3", "ParametricCurve", "Projection", "Ray",
    "abs", "arrow", "arrow_between", "arrow_on", "bottommost", "box3", "box_hidden3", "box_visible3",
    "circle_through", "circle_with_diameter", "cos", "cross", "curve_at", "direction", "distance",
    "dot", "exp", "fill", "graph", "group", "intersect", "intersections", "label", "leftmost",
    "line_through", "log", "marker", "max", "midpoint", "min", "nearest", "norm", "normal_left",
    "normal_line", "normal_right", "parallel", "perpendicular", "perpendicular_bisector", "point_label",
    "polygon", "polygon3", "project", "pt", "pt3", "quad", "quad3", "rightmost", "rotate", "rotate90",
    "secant", "segment3", "segments3", "sidelines", "sin", "speed", "sqrt", "tan", "tangent_line",
    "topmost", "unit", "unit_tangent", "vec", "vec3", "velocity",
}


@dataclass
class UserFunction:
    params: list[str]
    body: Expr


class Evaluator:
    def __init__(self):
        self.scene = Scene()
        self.env: dict[str, Any] = {"pi": math.pi, "e": math.e}
        self.styles: dict[str, Style] = {}
        self.functions: dict[str, UserFunction] = {}

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
        if isinstance(stmt, ProjectionStmt):
            self.apply_projection(stmt)
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
        if isinstance(stmt, FunctionDef):
            if stmt.name in _BUILTIN_FUNCTIONS or stmt.name in self.env:
                raise GeomValueError(f"Cannot redefine built-in name '{stmt.name}'.", stmt.span.line, stmt.span.column)
            self.functions[stmt.name] = UserFunction(stmt.params, stmt.body)
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
            if expr.op == "-" and isinstance(value, Vector3):
                return Vector3(-value.x, -value.y, -value.z)
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
        if isinstance(left, Point3) and isinstance(right, Vector3):
            if op == "+":
                return Point3(left.x + right.x, left.y + right.y, left.z + right.z)
            if op == "-":
                return Point3(left.x - right.x, left.y - right.y, left.z - right.z)
        if isinstance(left, Point3) and isinstance(right, Point3) and op == "-":
            return Vector3(left.x - right.x, left.y - right.y, left.z - right.z)
        if isinstance(left, Vector) and isinstance(right, Vector):
            if op == "+":
                return Vector(left.x + right.x, left.y + right.y)
            if op == "-":
                return Vector(left.x - right.x, left.y - right.y)
        if isinstance(left, Vector3) and isinstance(right, Vector3):
            if op == "+":
                return Vector3(left.x + right.x, left.y + right.y, left.z + right.z)
            if op == "-":
                return Vector3(left.x - right.x, left.y - right.y, left.z - right.z)
        if is_number(left) and isinstance(right, Vector) and op == "*":
            return Vector(left * right.x, left * right.y)
        if is_number(left) and isinstance(right, Vector3) and op == "*":
            return Vector3(left * right.x, left * right.y, left * right.z)
        if isinstance(left, Vector) and is_number(right):
            if op == "*":
                return Vector(left.x * right, left.y * right)
            if op == "/":
                if right == 0:
                    raise GeomValueError("Division by zero is undefined.", expr.span.line, expr.span.column)
                return Vector(left.x / right, left.y / right)
        if isinstance(left, Vector3) and is_number(right):
            if op == "*":
                return Vector3(left.x * right, left.y * right, left.z * right)
            if op == "/":
                if right == 0:
                    raise GeomValueError("Division by zero is undefined.", expr.span.line, expr.span.column)
                return Vector3(left.x / right, left.y / right, left.z / right)
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
        if name == "graph":
            if len(expr.args) != 2 or not isinstance(expr.args[1], ParamRange) or isinstance(expr.args[0], ParamRange):
                raise GeomTypeError("graph(Expr, x = start..end) expected.", expr.span.line, expr.span.column)
            pr = expr.args[1]
            start = self.eval_number(pr.start)
            end = self.eval_number(pr.end)
            point_expr = CallExpr(expr.span, "pt", [VarExpr(pr.span, pr.name), expr.args[0]])
            return ParametricCurve(point_expr, pr.name, start, end, dict(self.env))
        if name in self.functions:
            args = [self.eval_param_arg(a) for a in expr.args]
            return self.call_user_function(name, args, expr)
        args = [self.eval_param_arg(a) for a in expr.args]
        return self.call_builtin(name, args, expr)

    def eval_param_arg(self, arg: Expr | ParamRange) -> Any:
        if isinstance(arg, ParamRange):
            raise GeomTypeError("Parameter ranges are only valid in ParametricCurve.", arg.span.line, arg.span.column)
        return self._eval_expr(arg)

    def call_user_function(self, name: str, args: list[Any], expr: CallExpr) -> Any:
        function = self.functions[name]
        expected = len(function.params)
        if len(args) != expected:
            raise GeomTypeError(f"{name} expected {expected} arguments, got {len(args)}.", expr.span.line, expr.span.column)
        env = dict(self.env)
        env.update(zip(function.params, args))
        return self.eval_expr(function.body, env)

    def call_builtin(self, name: str, args: list[Any], expr: CallExpr) -> Any:
        if name == "pt":
            require_len(name, args, 2, expr)
            return Point(require_number(args[0], expr), require_number(args[1], expr))
        if name == "vec":
            require_len(name, args, 2, expr)
            return Vector(require_number(args[0], expr), require_number(args[1], expr))
        if name == "pt3":
            require_len(name, args, 3, expr)
            return Point3(require_number(args[0], expr), require_number(args[1], expr), require_number(args[2], expr))
        if name == "vec3":
            require_len(name, args, 3, expr)
            return Vector3(require_number(args[0], expr), require_number(args[1], expr), require_number(args[2], expr))
        if name == "group":
            return flatten_values(args)
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
        if name == "secant":
            require_len(name, args, 3, expr)
            c = require_curve(args[0], expr)
            p1 = curve_point(c, require_number(args[1], expr), self, expr)
            p2 = curve_point(c, require_number(args[2], expr), self, expr)
            return Line(p1, nonzero_vector(Vector(p2.x - p1.x, p2.y - p1.y), expr))
        if name == "sidelines":
            require_len(name, args, 3, expr)
            a = require_point(args[0], expr)
            b = require_point(args[1], expr)
            c = require_point(args[2], expr)
            return [
                Line(a, nonzero_vector(Vector(b.x - a.x, b.y - a.y), expr)),
                Line(b, nonzero_vector(Vector(c.x - b.x, c.y - b.y), expr)),
                Line(c, nonzero_vector(Vector(a.x - c.x, a.y - c.y), expr)),
            ]
        if name == "LineSegment":
            a, b = require_points(name, args, expr)
            return LineSegment(a, b)
        if name in {"LineSegment3", "segment3"}:
            a, b = require_points3(name, args, expr)
            return LineSegment3(a, b)
        if name == "segments3":
            if len(args) < 2 or len(args) % 2 != 0:
                raise GeomTypeError("segments3(Point3, Point3, ...) expected point pairs.", expr.span.line, expr.span.column)
            return [LineSegment3(require_point3(args[i], expr), require_point3(args[i + 1], expr)) for i in range(0, len(args), 2)]
        if name == "box3":
            require_len(name, args, 2, expr)
            return Box3(require_point3(args[0], expr), require_vector3(args[1], expr))
        if name == "box_hidden3":
            require_len(name, args, 1, expr)
            return box_hidden3(require_box3(args[0], expr))
        if name == "box_visible3":
            if len(args) not in {1, 2}:
                raise GeomTypeError(f"box_visible3 expected 1 or 2 arguments, got {len(args)}.", expr.span.line, expr.span.column)
            z_floor = require_number(args[1], expr) if len(args) == 2 else 0.0
            return box_visible3(require_box3(args[0], expr), z_floor)
        if name == "polygon":
            if len(args) < 3:
                raise GeomTypeError("polygon(Point, Point, Point, ...) expected at least 3 points.", expr.span.line, expr.span.column)
            return PolygonCurve([require_point(arg, expr) for arg in args])
        if name == "quad":
            require_len(name, args, 4, expr)
            return PolygonCurve([require_point(arg, expr) for arg in args])
        if name == "polygon3":
            if len(args) < 3:
                raise GeomTypeError("polygon3(Point3, Point3, Point3, ...) expected at least 3 points.", expr.span.line, expr.span.column)
            return Polygon3([require_point3(arg, expr) for arg in args])
        if name == "quad3":
            require_len(name, args, 4, expr)
            return Polygon3([require_point3(arg, expr) for arg in args])
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
        if name == "Projection":
            require_len(name, args, 5, expr)
            return Projection(require_point(args[0], expr), require_vector(args[1], expr), require_vector(args[2], expr), require_vector(args[3], expr), require_number(args[4], expr))
        if name == "project":
            if len(args) == 1:
                return project_value(args[0], self.scene.projection, expr)
            if len(args) == 2:
                return project_value(args[0], require_projection(args[1], expr), expr)
            raise GeomTypeError(f"project expected 1 or 2 arguments, got {len(args)}.", expr.span.line, expr.span.column)
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
        if name == "arrow_on":
            if len(args) not in {1, 2, 3}:
                raise GeomTypeError(f"arrow_on expected 1 to 3 arguments, got {len(args)}.", expr.span.line, expr.span.column)
            segment = args[0]
            if isinstance(segment, LineSegment3):
                segment = project_value(segment, self.scene.projection, expr)
            if not isinstance(segment, LineSegment):
                raise GeomTypeError(f"arrow_on expects LineSegment or LineSegment3, got {type_name(segment)}.", expr.span.line, expr.span.column)
            at = require_number(args[1], expr) if len(args) >= 2 else 0.5
            length = require_number(args[2], expr) if len(args) == 3 else 0.25
            if at < 0 or at > 1:
                raise GeomValueError("arrow_on at must be between 0 and 1.", expr.span.line, expr.span.column)
            if length <= 0:
                raise GeomValueError("arrow_on length must be positive.", expr.span.line, expr.span.column)
            dx = segment.b.x - segment.a.x
            dy = segment.b.y - segment.a.y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 1e-12:
                raise GeomValueError("arrow_on requires a nonzero segment.", expr.span.line, expr.span.column)
            half_t = 0.5 * length / distance
            if at - half_t < -1e-12 or at + half_t > 1 + 1e-12:
                raise GeomValueError("arrow_on length must fit inside the segment at the requested parameter.", expr.span.line, expr.span.column)
            start_t = max(0.0, at - half_t)
            end_t = min(1.0, at + half_t)
            start = segment.point_at(start_t)
            end = segment.point_at(end_t)
            return Drawable("arrow", {"start": start, "vector": Vector(end.x - start.x, end.y - start.y)})
        if name == "label":
            require_len(name, args, 2, expr)
            if not isinstance(args[1], str):
                raise GeomTypeError("label(Point, String) expected.", expr.span.line, expr.span.column)
            return Drawable("label", {"point": require_point(args[0], expr), "text": args[1]})
        if name == "point_label":
            require_len(name, args, 2, expr)
            if not isinstance(args[1], str):
                raise GeomTypeError("point_label(Point, String) expected.", expr.span.line, expr.span.column)
            return Drawable(
                "label",
                {"point": require_point(args[0], expr), "text": args[1]},
                Style({"offset": Vector(0.12, 0.12), "anchor": "bottom-left"}),
            )
        if name == "fill":
            require_len(name, args, 1, expr)
            return Drawable("fill", {"curve": require_fillable_curve(args[0], expr, self)})
        raise GeomNameError(f"Unknown function '{name}'.", expr.span.line, expr.span.column)

    def eval_draw(self, stmt: DrawStmt) -> None:
        value = self.eval_expr(stmt.expr)
        style = self.eval_style(stmt.style) if stmt.style else None
        for drawable in self.drawables_for_value(value, stmt):
            drawable.style = self.scene.default_style_for(drawable.kind).merged(drawable.style).merged(style)
            self.scene.append(drawable)

    def drawables_for_value(self, value: Any, stmt: DrawStmt) -> list[Drawable]:
        if isinstance(value, list):
            drawables: list[Drawable] = []
            for item in value:
                drawables.extend(self.drawables_for_value(item, stmt))
            return drawables
        if isinstance(value, Curve):
            return [Drawable("curve", {"curve": value})]
        if isinstance(value, Drawable):
            return [value]
        raise GeomTypeError(f"draw expected Curve or Drawable, got {type_name(value)}.", stmt.span.line, stmt.span.column)

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
            elif key in {"grid", "axes", "frame", "ticks", "tick_labels"}:
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

    def apply_projection(self, stmt: ProjectionStmt) -> None:
        current = self.scene.projection
        origin = current.origin
        x_axis = current.x
        y_axis = current.y
        z_axis = current.z
        scale = current.scale
        for key, expr in stmt.args.items():
            if key == "origin":
                origin = require_point(self.eval_expr(expr), expr)
            elif key == "x":
                x_axis = require_vector(self.eval_expr(expr), expr)
            elif key == "y":
                y_axis = require_vector(self.eval_expr(expr), expr)
            elif key == "z":
                z_axis = require_vector(self.eval_expr(expr), expr)
            elif key == "scale":
                scale = self.eval_number(expr)
            else:
                raise GeomValueError(f"Unknown projection field '{key}'.", expr.span.line, expr.span.column)
        self.scene.projection = Projection(origin, x_axis, y_axis, z_axis, scale)

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


def flatten_values(values: list[Any]) -> list[Any]:
    flattened: list[Any] = []
    for value in values:
        if isinstance(value, list):
            flattened.extend(flatten_values(value))
        else:
            flattened.append(value)
    return flattened


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


def require_point3(value: Any, expr: Expr) -> Point3:
    if not isinstance(value, Point3):
        raise GeomTypeError(f"Expected Point3, got {type_name(value)}.", expr.span.line, expr.span.column)
    return value


def require_vector3(value: Any, expr: Expr) -> Vector3:
    if not isinstance(value, Vector3):
        raise GeomTypeError(f"Expected Vector3, got {type_name(value)}.", expr.span.line, expr.span.column)
    return value


def require_projection(value: Any, expr: Expr) -> Projection:
    if not isinstance(value, Projection):
        raise GeomTypeError(f"Expected Projection, got {type_name(value)}.", expr.span.line, expr.span.column)
    return value


def require_box3(value: Any, expr: Expr) -> Box3:
    if not isinstance(value, Box3):
        raise GeomTypeError(f"Expected Box3, got {type_name(value)}.", expr.span.line, expr.span.column)
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


def project_point3(p: Point3, projection: Projection) -> Point:
    x = projection.origin.x + projection.scale * (p.x * projection.x.x + p.y * projection.y.x + p.z * projection.z.x)
    y = projection.origin.y + projection.scale * (p.x * projection.x.y + p.y * projection.y.y + p.z * projection.z.y)
    return Point(x, y)


def project_vector3(v: Vector3, projection: Projection) -> Vector:
    x = projection.scale * (v.x * projection.x.x + v.y * projection.y.x + v.z * projection.z.x)
    y = projection.scale * (v.x * projection.x.y + v.y * projection.y.y + v.z * projection.z.y)
    return Vector(x, y)


def project_value(value: Any, projection: Projection, expr: Expr) -> Any:
    if isinstance(value, Point3):
        return project_point3(value, projection)
    if isinstance(value, Vector3):
        return project_vector3(value, projection)
    if isinstance(value, LineSegment3):
        return LineSegment(project_point3(value.a, projection), project_point3(value.b, projection))
    if isinstance(value, Polygon3):
        return PolygonCurve([project_point3(p, projection) for p in value.points])
    if isinstance(value, list):
        return [project_value(item, projection, expr) for item in value]
    raise GeomTypeError(f"Cannot project {type_name(value)}.", expr.span.line, expr.span.column)


def box_corner(box: Box3, x: float, y: float, z: float) -> Point3:
    return Point3(
        box.origin.x + x * box.size.x,
        box.origin.y + y * box.size.y,
        box.origin.z + z * box.size.z,
    )


def box_hidden3(box: Box3) -> list[Any]:
    a = box_corner(box, 0, 0, 0)
    b = box_corner(box, 0, 1, 0)
    c = box_corner(box, 0, 1, 1)
    d = box_corner(box, 0, 0, 1)
    e = box_corner(box, 1, 0, 0)
    f = box_corner(box, 1, 1, 0)
    g = box_corner(box, 1, 1, 1)
    h = box_corner(box, 1, 0, 1)
    return [
        Polygon3([e, f, b, a]),
        LineSegment3(a, d),
        LineSegment3(b, c),
        LineSegment3(e, h),
        LineSegment3(f, g),
    ]


def box_visible3(box: Box3, z_floor: float) -> list[Any]:
    c = box_corner(box, 0, 1, 1)
    d = box_corner(box, 0, 0, 1)
    g = box_corner(box, 1, 1, 1)
    h = box_corner(box, 1, 0, 1)
    drop = box_corner(box, 1, 1, z_floor)
    return [Polygon3([h, g, c, d]), LineSegment3(g, drop)]


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


def require_points3(name: str, args: list[Any], expr: CallExpr) -> tuple[Point3, Point3]:
    require_len(name, args, 2, expr)
    return require_point3(args[0], expr), require_point3(args[1], expr)


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
