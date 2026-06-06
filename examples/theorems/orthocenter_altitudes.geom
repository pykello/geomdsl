scene(min=(-2.45,-1.35), max=(2.6,2.2), size=(7.0,4.9), grid=false, axes=false)

include "../common/construction_styles.geom"

# Theorem illustrated:
# The altitudes of a triangle are concurrent. Their common intersection
# is the orthocenter.
#
# Construction in the diagram:
# BC is the line through side BC, and AC is the line through side AC.
# hA is the line through vertex A perpendicular to BC, so hA is the
# altitude from A. hB is the line through vertex B perpendicular to AC,
# so hB is the altitude from B. Their intersection is H.
#
# Why this proves the claim visually:
# An altitude is defined as a line through a vertex perpendicular to the
# opposite side. The two dashed blue lines are therefore genuine
# altitudes by construction. In Euclidean geometry, the third altitude
# also passes through the same point H; this concurrency point is called
# the orthocenter. The diagram highlights H as the intersection
# determined by two altitudes.

style triangle = {color: "#c7f9cc", opacity: 0.35, z: 1}

A = pt(-1.65, -0.72)
B = pt(1.9, -0.52)
C = pt(0.08, 1.55)

BC = line_through(B, C)
AC = line_through(A, C)
hA = perpendicular(BC, A)
hB = perpendicular(AC, B)
H = intersect(hA, hB)
tri = polygon(A, B, C)

draw fill(tri) @ triangle
draw tri @ edge
draw hA @ construction
draw hB @ construction

draw marker(A)
draw marker(B)
draw marker(C)
draw marker(H) @ {color: red, size: 30}

draw label(A, "$A$") @ {offset: vec(-0.16, -0.14)}
draw label(B, "$B$") @ {offset: vec(0.15, -0.14)}
draw label(C, "$C$") @ {offset: vec(0.08, 0.16)}
draw label(H, "$H$") @ {offset: vec(0.14, 0.12)}

draw label(pt(-2.25, -1.12), "orthocenter theorem") @ {anchor: left, font_size: 13}
