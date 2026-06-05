# Inspired by MIT OpenCourseWare linear algebra material on linear transformations:
# https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/
# Original DSL diagram: a square grid and its image under A = [[1.2, 0.6], [0.3, 1.1]].

scene(min=(-3.6,-0.9), max=(5.9,4.5), size=(8,5), grid=false, axes=false)

style original = {color: gray, weight: 0.9, pattern: dotted, z: 1}
style image = {color: blue, weight: 1.8, z: 5}
style basis = {color: black, weight: 1.8, arrow_size: 12, z: 10}
style image_basis = {color: red, weight: 2, arrow_size: 13, z: 11}
style connector = {color: gray, weight: 1.1, pattern: dashed, arrow_size: 10, z: 3}
style label_s = {font_size: 12, z: 20}

# Left panel: original grid with origin O.
O = pt(-3.0,0)

draw LineSegment(pt(-3,0), pt(-1,0)) @ original
draw LineSegment(pt(-3,1), pt(-1,1)) @ original
draw LineSegment(pt(-3,2), pt(-1,2)) @ original
draw LineSegment(pt(-3,0), pt(-3,2)) @ original
draw LineSegment(pt(-2,0), pt(-2,2)) @ original
draw LineSegment(pt(-1,0), pt(-1,2)) @ original

draw arrow(O, vec(1,0)) @ basis
draw arrow(O, vec(0,1)) @ basis
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

# Parallelogram lattice rows.
draw LineSegment(pt(1.2,0), pt(3.6,0.6)) @ image
draw LineSegment(pt(1.8,1.1), pt(4.2,1.7)) @ image
draw LineSegment(pt(2.4,2.2), pt(4.8,2.8)) @ image

draw LineSegment(pt(1.2,0), pt(2.4,2.2)) @ image
draw LineSegment(pt(2.4,0.3), pt(3.6,2.5)) @ image
draw LineSegment(pt(3.6,0.6), pt(4.8,2.8)) @ image

draw arrow(O2, Ae1) @ image_basis
draw arrow(O2, Ae2) @ image_basis
draw label(pt(2.35,0.48), "$A\\mathbf{e}_1$") @ {color: red, z: 20}
draw label(pt(1.88,1.24), "$A\\mathbf{e}_2$") @ {color: red, z: 20}
draw label(pt(2.55,3.24), "image lattice") @ {font_size: 12, color: blue, z: 20}
draw label(pt(-3.25,3.95), "$A$ maps basis vectors and the whole grid") @ {font_size: 14, anchor: left, z: 20}
