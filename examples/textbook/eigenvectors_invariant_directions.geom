# Inspired by MIT OpenCourseWare 18.06SC eigenvectors and eigenvalues:
# https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/least-squares-determinants-and-eigenvalues/eigenvalues-and-eigenvectors/
# Original DSL diagram: most vectors turn under A, while eigenvectors keep their direction.

scene(
  min=(-2.9,-2.2), max=(3.3,2.55), size=(7,5),
  grid=false, axes=true,
  frame=false, ticks=false, tick_labels=false
)

style vector_s = {color: gray, weight: 1.25, arrow_size: 9, z: 3}
style image_s = {color: blue, weight: 1.9, arrow_size: 11, z: 5}
style eigen_s = {color: red, weight: 2.3, arrow_size: 13, z: 10}
style line_s = {color: red, weight: 1.0, pattern: dashed, z: 1}
style label_s = {font_size: 12, z: 20}

O = pt(0,0)
v1 = vec(1.15,0.63)
Av1 = vec(2.05,1.13)
v2 = vec(-0.55,1.0)
Av2 = vec(-0.28,0.50)
x1 = vec(0.95,1.35)
Ax1 = vec(1.70,0.82)
x2 = vec(-1.35,0.58)
Ax2 = vec(-0.58,1.22)
x3 = vec(0.55,-1.28)
Ax3 = vec(1.05,-0.53)

# Invariant eigendirections.
draw Line(pt(0,0), vec(1,0.55)) @ line_s
draw Line(pt(0,0), vec(-0.55,1)) @ {color: red, weight: 1.0, pattern: dotted, z: 1}

# Eigenvectors and their images: same line, scaled.
draw arrow(O, v1) @ eigen_s
draw arrow(O, Av1) @ {color: red, weight: 1.45, arrow_size: 10, z: 9}
draw arrow(O, v2) @ eigen_s
draw arrow(O, Av2) @ {color: red, weight: 1.45, arrow_size: 10, z: 9}

# Non-eigenvectors and images: direction changes.
draw arrow(O, x1) @ vector_s
draw arrow(O, Ax1) @ image_s
draw arrow(O, x2) @ vector_s
draw arrow(O, Ax2) @ image_s
draw arrow(O, x3) @ vector_s
draw arrow(O, Ax3) @ image_s

draw label(pt(2.04,1.20), "$A\\mathbf{v}=\\lambda\\mathbf{v}$") @ {color: red, font_size: 13, z: 20}
draw label(pt(1.72,0.72), "$A\\mathbf{x}$") @ {color: blue, z: 20}
draw label(pt(0.82,1.45), "$\\mathbf{x}$") @ {color: gray, z: 20}
draw label(pt(-2.55,-1.72), "eigenvectors keep direction") @ {font_size: 12, anchor: left, z: 20}
draw label(pt(-2.55,-1.94), "other vectors rotate") @ {font_size: 12, color: gray, anchor: left, z: 20}
