# Inspired by MIT OpenCourseWare 18.06SC eigenvectors and eigenvalues:
# https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/least-squares-determinants-and-eigenvalues/eigenvalues-and-eigenvectors/
# Original DSL diagram: most vectors turn under A, while eigenvectors keep their direction.

scene(min=(-2.9,-2.2), max=(3.3,2.55), size=(7,5), grid=true, grid_step=1, axes=true)

style vector_s = {color: gray, weight: 1.25, arrow_size: 9, z: 3}
style image_s = {color: blue, weight: 1.9, arrow_size: 11, z: 5}
style eigen_s = {color: red, weight: 2.3, arrow_size: 13, z: 10}
style line_s = {color: red, weight: 1.0, pattern: dashed, z: 1}
style label_s = {font_size: 12, z: 20}

O = pt(0,0)

# Invariant eigendirections.
draw Line(pt(0,0), vec(1,0.55)) @ line_s
draw Line(pt(0,0), vec(-0.55,1)) @ {color: red, weight: 1.0, pattern: dotted, z: 1}

# Eigenvectors and their images: same line, scaled.
draw arrow(O, vec(1.15,0.63)) @ eigen_s
draw arrow(O, vec(2.05,1.13)) @ {color: red, weight: 1.45, arrow_size: 10, z: 9}
draw arrow(O, vec(-0.55,1.0)) @ eigen_s
draw arrow(O, vec(-0.28,0.50)) @ {color: red, weight: 1.45, arrow_size: 10, z: 9}

# Non-eigenvectors and images: direction changes.
draw arrow(O, vec(0.95,1.35)) @ vector_s
draw arrow(O, vec(1.70,0.82)) @ image_s
draw arrow(O, vec(-1.35,0.58)) @ vector_s
draw arrow(O, vec(-0.58,1.22)) @ image_s
draw arrow(O, vec(0.55,-1.28)) @ vector_s
draw arrow(O, vec(1.05,-0.53)) @ image_s

draw label(pt(2.04,1.20), "$A\\mathbf{v}=\\lambda\\mathbf{v}$") @ {color: red, font_size: 13, z: 20}
draw label(pt(1.72,0.72), "$A\\mathbf{x}$") @ {color: blue, z: 20}
draw label(pt(0.82,1.45), "$\\mathbf{x}$") @ {color: gray, z: 20}
draw label(pt(-2.55,-1.72), "eigenvectors keep direction") @ {font_size: 12, anchor: left, z: 20}
draw label(pt(-2.55,-1.94), "other vectors rotate") @ {font_size: 12, color: gray, anchor: left, z: 20}
