scene(
  min=(-1,-1), max=(4,3),
  grid=true, axes=true,
  frame=false, ticks=false, tick_labels=false
)

# Smallest complete drawing: a segment and its labeled endpoints.
A = pt(0, 0)
B = pt(3, 1)

draw LineSegment(A, B)
draw marker(A)
draw marker(B)
draw label(A, "$A$") @ {offset: vec(-0.2, -0.2)}
draw label(B, "$B$") @ {offset: vec(0.1, 0.1)}
