scene(
  min=(-2.6,-1.35), max=(2.75,2.15), size=(7.0,4.8),
  grid=false, axes=false,
  frame=false, ticks=false, tick_labels=false
)

include "../common/construction_styles.geom"

# Theorem illustrated:
# The perpendicular bisectors of a triangle's sides meet at the
# circumcenter, the center of the unique circle through all three
# vertices.
#
# Construction in the diagram:
# For triangle ABC, ab is the perpendicular bisector of side AB and ac
# is the perpendicular bisector of side AC. Their intersection is O.
# The red circle is then drawn with center O through A.
#
# Why this proves the claim:
# Since O lies on the perpendicular bisector of AB, it is equidistant
# from A and B, so OA = OB. Since O lies on the perpendicular bisector
# of AC, it is equidistant from A and C, so OA = OC. Therefore
# OA = OB = OC, which means one circle centered at O passes through all
# three vertices. That point O is the circumcenter.

style triangle = {color: "#8ecae6", opacity: 0.28, z: 1}
style circle_s = {color: red, weight: 1.4, z: 3}

A = pt(-1.65, -0.75)
B = pt(1.85, -0.55)
C = pt(0.42, 1.48)

ab = perpendicular_bisector(A, B)
ac = perpendicular_bisector(A, C)
O = intersect(ab, ac)
circ = circle_through(O, A)
tri = polygon(A, B, C)

draw fill(tri) @ triangle
draw circ @ circle_s
draw tri @ edge
draw ab @ construction
draw ac @ construction

draw marker(A)
draw marker(B)
draw marker(C)
draw marker(O) @ {color: red, size: 30}

draw label(A, "$A$") @ {offset: vec(-0.16, -0.13)}
draw label(B, "$B$") @ {offset: vec(0.15, -0.13)}
draw label(C, "$C$") @ {offset: vec(0.08, 0.16)}
draw label(O, "$O$") @ {offset: vec(0.14, 0.14)}
