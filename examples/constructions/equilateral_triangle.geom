scene(min=(-0.7,-0.55), max=(2.7,2.15), size=(6.4,4.8), grid=false, axes=false)

include "../common/construction_styles.geom"

style face = {color: "#f9d976", opacity: 0.36, z: 1}

A = pt(0, 0)
B = pt(2, 0)

cA = circle_through(A, B)
cB = circle_through(B, A)
Xs = intersections(cA, cB)
C = topmost(Xs)

tri = polygon(A, B, C)

draw fill(tri) @ face
draw cA @ compass
draw cB @ compass
draw tri @ edge

draw marker(A)
draw marker(B)
draw marker(C)
draw label(A, "$A$") @ {offset: vec(-0.12, -0.15)}
draw label(B, "$B$") @ {offset: vec(0.12, -0.15)}
draw label(C, "$C$") @ {offset: vec(0, 0.16)}

draw label(pt(-0.52, -0.38), "equilateral triangle by two circles") @ {anchor: left, font_size: 14}
