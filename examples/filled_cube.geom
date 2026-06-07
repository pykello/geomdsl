scene(
  min=(-0.7,-0.4), max=(3.5,3.25), size=(6.8,5.2),
  grid=false, axes=false,
  frame=false, ticks=false, tick_labels=false
)

defaults {
  curve: {color: black, weight: 1.6, samples: 16, z: 10}
  label: {font_size: 13, z: 20}
}

style top_fill = {color: "#ffe8a3", opacity: 0.70, z: 1}
style side_fill = {color: "#f4b37b", opacity: 0.58, z: 2}
style front_fill = {color: "#8ecae6", opacity: 0.62, z: 3}
style edge = {color: "#1f2933", weight: 1.8, z: 10}
style hidden = {color: "#7a8691", weight: 1.1, pattern: dashed, z: 9}

# A hand-projected cube in 2D. The three edge vectors define the view,
# so the eight cube vertices can be read as A plus combinations of
# right/up/depth instead of unrelated screen coordinates.
A = pt(0, 0)
right = vec(2.2, 0.25)
up = vec(-0.25, 1.85)
depth = vec(0.85, 0.62)

B = A + right
D = A + up
C = A + right + up
A2 = A + depth
B2 = B + depth
C2 = C + depth
D2 = D + depth

front = quad(A, B, C, D)
right = quad(B, B2, C2, C)
top = quad(D, C, C2, D2)

# Face fills first, outlines second.
draw fill(top) @ top_fill
draw fill(right) @ side_fill
draw fill(front) @ front_fill

draw front @ edge

draw group(
  LineSegment(B, B2),
  LineSegment(C, C2),
  LineSegment(D, D2),
  LineSegment(B2, C2),
  LineSegment(C2, D2)
) @ edge

# A few hidden/back edges give the projection context without dominating.
draw group(
  LineSegment(A, A2),
  LineSegment(A2, B2),
  LineSegment(A2, D2)
) @ hidden
