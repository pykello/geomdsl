scene(min=(-2.3,-2.05), max=(2.3,2.08), size=(6.2,5.0), grid=false, axes=false)

include "../common/construction_styles.geom"

# Construction goal:
# Given segment AB, construct its perpendicular bisector.
#
# Method:
# Draw two equal-radius circles: cA is centered at A and passes through
# B, while cB is centered at B and passes through A. Their intersections
# are U and D. The line through U and D is the constructed bisector.
#
# Why it works:
# U lies on both equal-radius circles, so UA = UB. D also lies on both
# circles, so DA = DB. Points equidistant from A and B lie on the
# perpendicular bisector of AB. Since both U and D have that property,
# the line UD is exactly the perpendicular bisector. The red point M
# marks the midpoint of AB, confirming that the constructed line passes
# through the midpoint and meets AB at a right angle.

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
draw LineSegment(A, B) @ edge
draw bis @ construction

draw marker(A)
draw marker(B)
draw marker(U)
draw marker(D)
draw marker(M) @ {color: red, size: 26}

draw label(A, "$A$") @ {offset: vec(-0.16, -0.12)}
draw label(B, "$B$") @ {offset: vec(0.16, -0.12)}
draw label(U, "$U$") @ {offset: vec(0.16, 0.1)}
draw label(D, "$D$") @ {offset: vec(0.14, -0.18)}
draw label(M, "$M$") @ {offset: vec(0.14, 0.14)}

draw label(pt(-2.05, -1.82), "perpendicular bisector") @ {anchor: left, font_size: 13}
