scene(min=(-0.7,-0.55), max=(2.7,2.15), size=(6.4,4.8), grid=false, axes=false)

include "../common/construction_styles.geom"

# Construction goal:
# Given the base segment AB, construct an equilateral triangle on AB
# using only compass-style circles.
#
# Method:
# Draw cA, the circle centered at A through B, and cB, the circle
# centered at B through A. Both circles have radius AB. Their two
# intersections are the possible third vertices of equilateral
# triangles on AB; this example chooses the upper one with topmost(...).
#
# Why it works:
# Because C lies on cA, AC = AB. Because C also lies on cB, BC = AB.
# Therefore AB = AC = BC, so triangle ABC is equilateral. The dashed
# circles show the compass construction, and the filled polygon is the
# final constructed triangle.

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
