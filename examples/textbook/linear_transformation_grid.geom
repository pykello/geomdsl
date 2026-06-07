# Inspired by MIT OpenCourseWare linear algebra material on linear transformations:
# https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/
# Original DSL diagram: a square grid and its image under A = [[1.2, 0.6], [0.3, 1.1]].

scene(
  min=(-3.6,-0.9), max=(5.9,4.5), size=(8,5),
  grid=false, axes=false,
  frame=false, ticks=false, tick_labels=false
)

style original = {color: gray, weight: 0.9, pattern: dotted, z: 1}
style image = {color: blue, weight: 1.8, z: 5}
style basis = {color: black, weight: 1.8, arrow_size: 12, z: 10}
style image_basis = {color: red, weight: 2, arrow_size: 13, z: 11}
style connector = {color: gray, weight: 1.1, pattern: dashed, arrow_size: 10, z: 3}
style label_s = {font_size: 12, z: 20}

# Left panel: original grid with origin O.
O = pt(-3.0,0)
e1 = vec(1,0)
e2 = vec(0,1)

# The domain grid is a 2-by-2 square lattice based at O.
draw group(
  LineSegment(O, O + 2*e1),
  LineSegment(O + e2, O + 2*e1 + e2),
  LineSegment(O + 2*e2, O + 2*e1 + 2*e2),
  LineSegment(O, O + 2*e2),
  LineSegment(O + e1, O + e1 + 2*e2),
  LineSegment(O + 2*e1, O + 2*e1 + 2*e2)
) @ original

draw arrow(O, e1) @ basis
draw arrow(O, e2) @ basis
draw label(pt(-2.03,-0.20), "$\\mathbf{e}_1$") @ label_s
draw label(pt(-3.28,0.95), "$\\mathbf{e}_2$") @ label_s
draw label(pt(-3.22,2.25), "domain grid") @ {font_size: 12, color: gray, z: 20}

# Transformation arrow between panels.
draw arrow(pt(-0.45,1.05), vec(1.1,0)) @ connector
draw label(pt(-0.18,1.28), "$A$") @ {font_size: 14, z: 20}

# Right panel: image lattice based at O2.
O2 = pt(1.2,0)
Ae1 = vec(1.2,0.3)
Ae2 = vec(0.6,1.1)

# The image lattice is the same 2-by-2 grid after applying A to
# each basis direction.
draw group(
  LineSegment(O2, O2 + 2*Ae1),
  LineSegment(O2 + Ae2, O2 + 2*Ae1 + Ae2),
  LineSegment(O2 + 2*Ae2, O2 + 2*Ae1 + 2*Ae2),
  LineSegment(O2, O2 + 2*Ae2),
  LineSegment(O2 + Ae1, O2 + Ae1 + 2*Ae2),
  LineSegment(O2 + 2*Ae1, O2 + 2*Ae1 + 2*Ae2)
) @ image

draw arrow(O2, Ae1) @ image_basis
draw arrow(O2, Ae2) @ image_basis
draw label(pt(2.35,0.48), "$A\\mathbf{e}_1$") @ {color: red, z: 20}
draw label(pt(1.88,1.24), "$A\\mathbf{e}_2$") @ {color: red, z: 20}
draw label(pt(2.55,3.24), "image lattice") @ {font_size: 12, color: blue, z: 20}
draw label(pt(-3.25,3.95), "$A$ maps basis vectors and the whole grid") @ {font_size: 14, anchor: left, z: 20}
