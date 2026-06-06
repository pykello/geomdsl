scene(min=(-2.3,-1.85), max=(2.3,1.95), size=(6.2,5.0), grid=false, axes=false)

defaults {
  curve: {color: "#1f2933", weight: 1.6, z: 10}
  marker: {color: "#111827", size: 20, z: 20}
  label: {font_size: 13, z: 30}
}

style compass = {color: "#7a8691", weight: 1.1, pattern: dashed, z: 2}
style base = {color: "#1f2933", weight: 2.0, z: 10}
style construction = {color: blue, weight: 1.8, z: 12}

A = pt(-1, 0)
B = pt(1, 0)

cA = circle_through(A, B)
cB = circle_through(B, A)
Xs = intersections(cA, cB)
U = topmost(Xs)
D = bottommost(Xs)
M = midpoint(A, B)
bis = line_through(U, D)

draw cA @ compass
draw cB @ compass
draw LineSegment(A, B) @ base
draw bis @ construction

draw marker(A)
draw marker(B)
draw marker(U)
draw marker(D)
draw marker(M) @ {color: red, size: 26}

draw label(A, "$A$") @ {offset: vec(-0.16, -0.12)}
draw label(B, "$B$") @ {offset: vec(0.16, -0.12)}
draw label(U, "$U$") @ {offset: vec(0.12, 0.12)}
draw label(D, "$D$") @ {offset: vec(0.12, -0.12)}
draw label(M, "$M$") @ {offset: vec(0.14, 0.14)}

draw label(pt(-2.05, 1.62), "perpendicular bisector construction") @ {anchor: left, font_size: 14}
