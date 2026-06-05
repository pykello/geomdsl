from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Vector:
    x: float
    y: float


@dataclass
class Style:
    fields: dict[str, Any] = field(default_factory=dict)

    def merged(self, other: "Style | None") -> "Style":
        data = dict(self.fields)
        if other:
            data.update(other.fields)
        return Style(data)

    def get(self, name: str, default: Any = None) -> Any:
        return self.fields.get(name, default)


@dataclass
class Drawable:
    kind: str
    data: dict[str, Any]
    style: Style = field(default_factory=Style)
    order: int = 0


@dataclass
class ExportConfig:
    format: str | None = None
    dpi: int = 150
    transparent: bool = False


DEFAULT_STYLE_FIELDS = {
    "color": "black",
    "weight": 1.5,
    "pattern": "solid",
    "opacity": 1.0,
    "visible": True,
    "size": 5,
    "marker": "dot",
    "arrow_head": True,
    "arrow_size": 12,
    "font_size": 12,
    "offset": Vector(0.0, 0.0),
    "anchor": "center",
    "z": 0,
    "samples": 300,
    "clip": "viewport",
}


@dataclass
class Scene:
    min: Point = field(default_factory=lambda: Point(-5.0, -5.0))
    max: Point = field(default_factory=lambda: Point(5.0, 5.0))
    size: tuple[float, float] = (6.0, 6.0)
    grid: bool = False
    grid_step: float = 1.0
    grid_style: Style = field(default_factory=Style)
    axes: bool = False
    axis_style: Style = field(default_factory=Style)
    aspect: str = "equal"
    background: str = "white"
    padding: float = 0.0
    export: ExportConfig = field(default_factory=ExportConfig)
    defaults: dict[str, Style] = field(default_factory=dict)
    drawables: list[Drawable] = field(default_factory=list)

    def default_style_for(self, kind: str) -> Style:
        base = Style(dict(DEFAULT_STYLE_FIELDS))
        return base.merged(self.defaults.get(kind))

    def append(self, drawable: Drawable) -> None:
        drawable.order = len(self.drawables)
        self.drawables.append(drawable)

    def sorted_drawables(self) -> list[Drawable]:
        return sorted(self.drawables, key=lambda d: (d.style.get("z", 0), d.order))


class Curve:
    kind = "curve"

    def domain(self) -> tuple[float, float]:
        return (0.0, 1.0)

    def point_at(self, t: float, evaluator: Any = None) -> Point:
        raise NotImplementedError


@dataclass
class LineSegment(Curve):
    a: Point
    b: Point
    kind: str = "line_segment"

    def domain(self) -> tuple[float, float]:
        return (0.0, 1.0)

    def point_at(self, t: float, evaluator: Any = None) -> Point:
        return Point(self.a.x + t * (self.b.x - self.a.x), self.a.y + t * (self.b.y - self.a.y))


@dataclass
class Line(Curve):
    a: Point
    v: Vector
    kind: str = "line"

    def domain(self) -> tuple[float, float]:
        return (-10.0, 10.0)

    def point_at(self, t: float, evaluator: Any = None) -> Point:
        return Point(self.a.x + t * self.v.x, self.a.y + t * self.v.y)


@dataclass
class Ray(Curve):
    a: Point
    v: Vector
    kind: str = "ray"

    def domain(self) -> tuple[float, float]:
        return (0.0, 10.0)

    def point_at(self, t: float, evaluator: Any = None) -> Point:
        return Point(self.a.x + t * self.v.x, self.a.y + t * self.v.y)


@dataclass
class Circle(Curve):
    center: Point
    radius: float
    kind: str = "circle"

    def domain(self) -> tuple[float, float]:
        import math

        return (0.0, 2.0 * math.pi)

    def point_at(self, t: float, evaluator: Any = None) -> Point:
        import math

        return Point(self.center.x + self.radius * math.cos(t), self.center.y + self.radius * math.sin(t))


@dataclass
class Arc(Curve):
    center: Point
    radius: float
    theta0: float
    theta1: float
    kind: str = "arc"

    def domain(self) -> tuple[float, float]:
        return (self.theta0, self.theta1)

    def point_at(self, t: float, evaluator: Any = None) -> Point:
        import math

        return Point(self.center.x + self.radius * math.cos(t), self.center.y + self.radius * math.sin(t))


@dataclass
class ParametricCurve(Curve):
    expr: Any
    param: str
    start: float
    end: float
    env: dict[str, Any]
    kind: str = "parametric"

    def domain(self) -> tuple[float, float]:
        return (self.start, self.end)

    def point_at(self, t: float, evaluator: Any = None) -> Point:
        if evaluator is None:
            from .evaluator import Evaluator

            evaluator = Evaluator()
        env = dict(self.env)
        env[self.param] = t
        value = evaluator.eval_expr(self.expr, env)
        if not isinstance(value, Point):
            raise TypeError("ParametricCurve expression did not evaluate to Point")
        return value
