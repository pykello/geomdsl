# Inspired by MIT OpenCourseWare linear algebra material on linear transformations:
# https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/
# Original DSL diagram: a square grid and its image under A = [[1.2, 0.6], [0.3, 1.1]].

scene(min=(-0.8,-0.8), max=(5.8,4.6), size=(7,5), grid=false, axes=true)

style original = {color: gray, weight: 1, pattern: dotted, z: 1}
style image = {color: blue, weight: 1.8, z: 5}
style basis = {color: black, weight: 2, arrow_size: 13, z: 10}
style image_basis = {color: red, weight: 2, arrow_size: 13, z: 11}
style label_s = {font_size: 12, z: 20}

O = pt(0,0)
e1 = vec(1,0)
e2 = vec(0,1)
Ae1 = vec(1.2,0.3)
Ae2 = vec(0.6,1.1)

# Original unit grid in dotted gray.
draw LineSegment(pt(0,0), pt(3,0)) @ original
draw LineSegment(pt(0,1), pt(3,1)) @ original
draw LineSegment(pt(0,2), pt(3,2)) @ original
draw LineSegment(pt(0,3), pt(3,3)) @ original
draw LineSegment(pt(0,0), pt(0,3)) @ original
draw LineSegment(pt(1,0), pt(1,3)) @ original
draw LineSegment(pt(2,0), pt(2,3)) @ original
draw LineSegment(pt(3,0), pt(3,3)) @ original

# Image of the grid under A, drawn as a sheared lattice.
draw LineSegment(pt(0,0), pt(3.6,0.9)) @ image
draw LineSegment(pt(0.6,1.1), pt(4.2,2.0)) @ image
draw LineSegment(pt(1.2,2.2), pt(4.8,3.1)) @ image
draw LineSegment(pt(1.8,3.3), pt(5.4,4.2)) @ image

draw LineSegment(pt(0,0), pt(1.8,3.3)) @ image
draw LineSegment(pt(1.2,0.3), pt(3.0,3.6)) @ image
draw LineSegment(pt(2.4,0.6), pt(4.2,3.9)) @ image
draw LineSegment(pt(3.6,0.9), pt(5.4,4.2)) @ image

# Basis vectors and their images.
draw arrow(O, e1) @ basis
draw arrow(O, e2) @ basis
draw arrow(O, Ae1) @ image_basis
draw arrow(O, Ae2) @ image_basis

draw label(pt(0.95,-0.18), "$\\mathbf{e}_1$") @ label_s
draw label(pt(-0.18,0.95), "$\\mathbf{e}_2$") @ label_s
draw label(pt(1.25,0.45), "$A\\mathbf{e}_1$") @ {color: red, z: 20}
draw label(pt(0.72,1.22), "$A\\mathbf{e}_2$") @ {color: red, z: 20}
draw label(pt(2.2,3.15), "A maps a square grid to a lattice") @ {font_size: 13, z: 20}
