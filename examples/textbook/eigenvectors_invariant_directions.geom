# Inspired by MIT OpenCourseWare 18.06SC eigenvectors and eigenvalues:
# https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/least-squares-determinants-and-eigenvalues/eigenvalues-and-eigenvectors/
# Original DSL diagram: most vectors turn under A, while eigenvectors keep their direction.

scene(min=(-3,-2.4), max=(3.6,2.6), size=(7,5), grid=true, grid_step=1, axes=true)

style vector_s = {color: gray, weight: 1.5, arrow_size: 10, z: 3}
style image_s = {color: blue, weight: 2, arrow_size: 12, z: 5}
style eigen_s = {color: red, weight: 2.4, arrow_size: 14, z: 10}
style line_s = {color: red, weight: 1.2, pattern: dashed, z: 1}

O = pt(0,0)

# Invariant eigendirections for a diagonal stretch in a rotated coordinate picture.
draw Line(pt(0,0), vec(1,0.55)) @ line_s
draw Line(pt(0,0), vec(-0.55,1)) @ {color: red, weight: 1.2, pattern: dotted, z: 1}

# Eigenvectors and their images: same line, scaled.
draw arrow(O, vec(1.2,0.66)) @ eigen_s
draw arrow(O, vec(2.2,1.21)) @ {color: red, weight: 1.5, arrow_size: 10, z: 9}
draw arrow(O, vec(-0.55,1.0)) @ eigen_s
draw arrow(O, vec(-0.28,0.50)) @ {color: red, weight: 1.5, arrow_size: 10, z: 9}

# Non-eigenvectors and images: direction changes.
draw arrow(O, vec(1.1,1.4)) @ vector_s
draw arrow(O, vec(1.9,0.9)) @ image_s
draw arrow(O, vec(-1.4,0.6)) @ vector_s
draw arrow(O, vec(-0.55,1.35)) @ image_s
draw arrow(O, vec(0.6,-1.4)) @ vector_s
draw arrow(O, vec(1.15,-0.55)) @ image_s

draw label(pt(2.25,1.35), "$A\\mathbf{v}=\\lambda\\mathbf{v}$") @ {color: red, font_size: 13, z: 20}
draw label(pt(1.95,0.78), "$A\\mathbf{x}$") @ {color: blue, z: 20}
draw label(pt(1.02,1.50), "$\\mathbf{x}$") @ {color: gray, z: 20}
draw label(pt(-2.75,-2.05), "eigenvectors keep direction; other vectors rotate") @ {font_size: 12, z: 20}
