# DSL quick reference

## Program structure

A `.geom` file is a sequence of statements.

```text
version "0.1"

scene(min=(-2,-2), max=(2,2), grid=true)
export(format=svg, dpi=300)

style tangent = {color: blue, pattern: dashed}

O = pt(0, 0)
c = Circle(O, 1)

draw c
draw marker(O)
draw label(O, "$O$") @ {offset: vec(0.1, 0.1)}
```

Comments start with `#`.

Scene decoration can be controlled independently:

```text
scene(frame=false, ticks=false, tick_labels=false)
```

`frame` controls the outer box, `ticks` controls tick marks, and
`tick_labels` controls numeric tick text. These options do not affect
geometry, grid lines, or axes.

## Includes

Use `include` to share common styles, defaults, and construction
definitions across files.

```text
include "../common/construction_styles.geom"

A = pt(0, 0)
B = pt(2, 0)
draw LineSegment(A, B) @ edge
```

Include paths are relative to the file that contains the include. The
included file is evaluated before the remaining statements in the
current file, using the same namespace for variables, styles, defaults,
scene settings, and export settings.

Cycles are errors. Raw source strings with includes must be evaluated
with a base path:

```python
evaluate(source, base_path="examples/constructions/main.geom")
```

## Geometry versus drawing

Assignments create mathematical values but do not draw anything.

```text
A = pt(0, 0)
B = pt(1, 1)
segment = LineSegment(A, B)
```

Only `draw` statements create visible scene objects.

```text
draw segment
draw marker(A)
draw label(B, "$B$")
```

## Core values

```text
Number      1, -2.5, 3.14
Boolean     true, false
String      "text", "$x$"
Point       pt(x, y)
Vector      vec(x, y)
Curve       Circle(...), LineSegment(...), ParametricCurve(...)
Drawable    marker(...), arrow(...), label(...)
Style       {color: red, weight: 2}
Scene       produced by evaluation
```

## Point and vector arithmetic

Valid examples:

```text
A = pt(1, 2)
B = pt(4, 6)
v = B - A
C = A + v
M = A + 0.5*v
```

Invalid examples:

```text
bad1 = A + B
bad2 = A * 2
bad3 = 1 + v
```

## Expressions

```text
1 + 2*3
2^3
-sin(pi/4)
A + 0.5*(B - A)
```

Operator precedence, highest to lowest:

```text
unary -
^
* /
+ -
```

## Scalar functions

```text
sin(x)
cos(x)
tan(x)
sqrt(x)
exp(x)
log(x)
abs(x)
min(a, b)
max(a, b)
```

Constants:

```text
pi
e
```

## Vector functions

```text
dot(u, v)
cross(u, v)
norm(v)
unit(v)
rotate(v, theta)
rotate90(v)
distance(A, B)
midpoint(A, B)
```

`unit(vec(0,0))` is an error.

## Construction helpers

Line-like helpers accept `Line`, `Ray`, and `LineSegment`.

```text
L = line_through(A, B)
d = direction(L)
P = midpoint(A, B)

L2 = parallel(L, P)
N = perpendicular(L, P)
B = perpendicular_bisector(A, B)

S = secant(curve, t1, t2)
sides = sidelines(A, B, C)
AB = sides[0]
BC = sides[1]
CA = sides[2]

c1 = circle_through(A, B)
c2 = circle_with_diameter(A, B)
```

`line_through(A, A)` and zero-length line-like directions are errors.
`secant(curve, t1, t2)` draws the full line through
`curve_at(curve, t1)` and `curve_at(curve, t2)`.
`sidelines(A, B, C)` returns `[AB, BC, CA]` as full lines.
The circle construction helpers require distinct defining points.

## Intersections

Use `intersections(a, b)` when a construction can produce zero, one,
or multiple points. Use `intersect(a, b)` only when exactly one point is
expected.

```text
L1 = line_through(A, B)
L2 = perpendicular(L1, P)
Q = intersect(L1, L2)

c = circle_through(A, B)
Ps = intersections(c, L1)
P0 = Ps[0]
P1 = Ps[1]

P = nearest(Ps, Q)
A = leftmost(Ps)
B = rightmost(Ps)
C = topmost(Ps)
D = bottommost(Ps)
```

Supported pairs are line-like curves with line-like curves, line-like
curves with circles, and circles with circles. Coincident or overlapping
inputs are errors because they have infinitely many intersections.
Point selectors require a non-empty `List[Point]`.

## Curves

```text
LineSegment(A, B)
Line(A, v)
Ray(A, v)
Circle(C, r)
Arc(C, r, theta0, theta1)
ParametricCurve(pt(cos(t), sin(t)), t = 0..2*pi)
graph(sin(x), x = -2*pi..2*pi)
```

Curves are directly drawable:

```text
draw Circle(pt(0,0), 1)
```

## Curve calculus

```text
curve_at(c, t)
velocity(c, t)
speed(c, t)
unit_tangent(c, t)
normal_left(c, t)
normal_right(c, t)
tangent_line(c, t)
normal_line(c, t)
```

Current calculus helpers use numerical differentiation.

## Drawables

```text
marker(P)
arrow(P, v)
arrow_between(A, B)
label(P, "$P$")
point_label(P, "$P$")
```

`point_label(P, text)` is a label with a small default offset and
bottom-left anchor for common point annotations. Inline style can still
override the offset or anchor.


## Filled regions

Use `fill(curve)` to fill a closed curve. Draw the outline separately when you want independent stroke styling.

```text
c = Circle(pt(0,0), 1)

draw fill(c) @ {color: "#87ceeb", opacity: 0.35, z: 1}
draw c       @ {color: blue, weight: 2, z: 2}
```

`fill(curve)` requires a closed curve. It accepts circles, full arcs, closed parametric curves, and polygonal curves.

For polygonal regions, use `polygon(...)` or `quad(...)`:

```text
A = pt(0,0)
B = pt(2,0)
C = pt(2,1)
D = pt(0,1)

face = quad(A, B, C, D)

draw fill(face) @ {color: "#ffeeaa", opacity: 0.45, z: 1}
draw face       @ {color: black, weight: 1.5, z: 2}
```

Fill defaults can be configured with the `fill` category:

```text
defaults {
  fill: {color: "#87ceeb", opacity: 0.3, z: 1}
}
```

## Styles

Named style:

```text
style axis = {color: black, weight: 1.5}
draw Line(pt(0,0), vec(1,0)) @ axis
```

Inline style:

```text
draw marker(P) @ {color: red, size: 9, z: 10}
```

Defaults:

```text
defaults {
  curve:  {color: black, weight: 1.5, samples: 300}
  marker: {color: black, size: 5}
  label:  {color: black, font_size: 12}
  arrow:  {color: black, weight: 1.5, arrow_size: 12}
}
```

Common style fields:

```text
color, weight, pattern, opacity, visible, size, marker,
arrow_head, arrow_size, font_size, offset, anchor, z, samples, clip
```

Rendering order is by `z`, then source order.

## Scene configuration

```text
scene(
  min=(-3, -2),
  max=(6, 5),
  size=(7, 5),
  grid=true,
  grid_step=1,
  axes=true,
  aspect=equal,
  background=white
)
```

Defaults:

```text
min=(-5, -5)
max=(5, 5)
size=(6, 6)
grid=false
grid_step=1
axes=false
aspect=equal
background=white
```
