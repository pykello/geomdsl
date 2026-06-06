from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from ..errors import GeomRenderError
from ..values import Circle, Curve, Drawable, Line, Point, PolygonCurve, Ray, Scene, Style, Vector


def render_scene(scene: Scene, *, output: str | None = None, fmt: str | None = None, dpi: int | None = None):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise GeomRenderError("Matplotlib backend is unavailable.") from exc

    dpi = dpi or scene.export.dpi
    fig, ax = plt.subplots(figsize=scene.size, dpi=dpi)
    fig.patch.set_facecolor(scene.background)
    ax.set_facecolor(scene.background)
    ax.set_xlim(scene.min.x - scene.padding, scene.max.x + scene.padding)
    ax.set_ylim(scene.min.y - scene.padding, scene.max.y + scene.padding)
    ax.set_aspect(scene.aspect)
    ax.set_axisbelow(True)

    if scene.grid:
        ax.grid(True, **line_kwargs(scene.grid_style))
        try:
            import matplotlib.ticker as ticker

            ax.xaxis.set_major_locator(ticker.MultipleLocator(scene.grid_step))
            ax.yaxis.set_major_locator(ticker.MultipleLocator(scene.grid_step))
        except Exception:
            pass
    else:
        ax.grid(False)

    if scene.axes:
        kw = line_kwargs(scene.axis_style)
        ax.axhline(0, **kw, zorder=-1)
        ax.axvline(0, **kw, zorder=-1)

    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color("#4a4f55")
        spine.set_visible(scene.frame)

    if not scene.ticks:
        ax.tick_params(axis="both", which="both", length=0)
    if not scene.tick_labels:
        ax.tick_params(axis="both", which="both", labelbottom=False, labeltop=False, labelleft=False, labelright=False)

    for drawable in scene.sorted_drawables():
        if drawable.style.get("visible", True) is False:
            continue
        render_drawable(ax, scene, drawable)

    if output is None:
        return fig
    path = Path(output)
    final_fmt = fmt or scene.export.format or path.suffix.lstrip(".") or None
    fig.savefig(path, format=final_fmt, dpi=dpi, transparent=scene.export.transparent, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def render_drawable(ax: Any, scene: Scene, drawable: Drawable) -> None:
    if drawable.kind == "fill":
        render_fill(ax, scene, drawable.data["curve"], drawable.style)
        return
    if drawable.kind == "curve":
        render_curve(ax, scene, drawable.data["curve"], drawable.style)
        return
    if drawable.kind == "marker":
        p = drawable.data["point"]
        marker = {"dot": "o", "circle": "o", "cross": "x", "none": ""}.get(drawable.style.get("marker", "dot"), "o")
        if marker:
            ax.scatter([p.x], [p.y], s=drawable.style.get("size", 5), marker=marker, color=drawable.style.get("color", "black"), alpha=drawable.style.get("opacity", 1.0), zorder=drawable.style.get("z", 0))
        return
    if drawable.kind == "arrow":
        p = drawable.data["start"]
        v = drawable.data["vector"]
        end = Point(p.x + v.x, p.y + v.y)
        ax.annotate(
            "",
            xy=(end.x, end.y),
            xytext=(p.x, p.y),
            annotation_clip=False,
            arrowprops={
                "arrowstyle": "->" if drawable.style.get("arrow_head", True) else "-",
                "color": drawable.style.get("color", "black"),
                "lw": drawable.style.get("weight", 1.5),
                "alpha": drawable.style.get("opacity", 1.0),
                "mutation_scale": drawable.style.get("arrow_size", 12),
                "linestyle": linestyle(drawable.style),
            },
            zorder=drawable.style.get("z", 0),
        )
        return
    if drawable.kind == "label":
        p = drawable.data["point"]
        off = drawable.style.get("offset", Vector(0.0, 0.0))
        ha, va = anchor(drawable.style.get("anchor", "center"))
        ax.text(
            p.x + off.x,
            p.y + off.y,
            drawable.data["text"],
            color=drawable.style.get("color", "black"),
            fontsize=drawable.style.get("font_size", 12),
            alpha=drawable.style.get("opacity", 1.0),
            ha=ha,
            va=va,
            zorder=drawable.style.get("z", 0),
        )
        return
    raise GeomRenderError(f"Unknown drawable kind '{drawable.kind}'.")


def render_curve(ax: Any, scene: Scene, curve: Curve, style: Style) -> None:
    samples = max(2, int(style.get("samples", 300)))
    points = sample_curve(curve, scene, samples)
    if not points:
        return
    ax.plot([p.x for p in points], [p.y for p in points], **line_kwargs(style), zorder=style.get("z", 0))


def render_fill(ax: Any, scene: Scene, curve: Curve, style: Style) -> None:
    samples = max(3, int(style.get("samples", 300)))
    points = sample_curve(curve, scene, samples)
    if not points:
        return
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    if xs[0] != xs[-1] or ys[0] != ys[-1]:
        xs.append(xs[0])
        ys.append(ys[0])
    ax.fill(
        xs,
        ys,
        color=style.get("color", "black"),
        alpha=style.get("opacity", 1.0),
        linewidth=0,
        zorder=style.get("z", 0),
    )


def sample_curve(curve: Curve, scene: Scene, samples: int) -> list[Point]:
    if isinstance(curve, PolygonCurve):
        if not curve.points:
            return []
        return [*curve.points, curve.points[0]]
    if isinstance(curve, Line):
        return clip_line(curve.a, curve.v, scene, ray=False)
    if isinstance(curve, Ray):
        return clip_line(curve.a, curve.v, scene, ray=True)
    a, b = curve.domain()
    if isinstance(curve, Circle):
        a, b = 0.0, 2.0 * math.pi
    pts: list[Point] = []
    for i in range(samples):
        t = a + (b - a) * i / (samples - 1)
        pts.append(curve.point_at(t, getattr(curve, "_evaluator", None)))
    return pts


def clip_line(p: Point, v: Vector, scene: Scene, *, ray: bool) -> list[Point]:
    t_min = 0.0 if ray else -math.inf
    t_max = math.inf
    eps = 1e-12

    for origin, direction, low, high in (
        (p.x, v.x, scene.min.x, scene.max.x),
        (p.y, v.y, scene.min.y, scene.max.y),
    ):
        if abs(direction) < eps:
            if origin < low - eps or origin > high + eps:
                return []
            continue
        a = (low - origin) / direction
        b = (high - origin) / direction
        enter = min(a, b)
        exit = max(a, b)
        t_min = max(t_min, enter)
        t_max = min(t_max, exit)

    if t_min > t_max + eps or not math.isfinite(t_min) or not math.isfinite(t_max):
        return []

    start = Point(p.x + t_min * v.x, p.y + t_min * v.y)
    end = Point(p.x + t_max * v.x, p.y + t_max * v.y)
    if abs(start.x - end.x) < 1e-9 and abs(start.y - end.y) < 1e-9:
        return [start]
    return [start, end]


def line_kwargs(style: Style) -> dict[str, Any]:
    return {
        "color": style.get("color", "black"),
        "linewidth": style.get("weight", 1.5),
        "linestyle": linestyle(style),
        "alpha": style.get("opacity", 1.0),
    }


def linestyle(style: Style) -> str:
    return {"solid": "-", "dashed": "--", "dotted": ":"}.get(style.get("pattern", "solid"), "-")


def anchor(value: str) -> tuple[str, str]:
    table = {
        "center": ("center", "center"),
        "left": ("left", "center"),
        "right": ("right", "center"),
        "top": ("center", "top"),
        "bottom": ("center", "bottom"),
        "top-left": ("left", "top"),
        "top-right": ("right", "top"),
        "bottom-left": ("left", "bottom"),
        "bottom-right": ("right", "bottom"),
    }
    return table.get(value, ("center", "center"))
