# Inspired by OpenStax Calculus Volume 3, 6.4 Green's Theorem:
# https://openstax.org/books/calculus-volume-3/pages/6-4-greens-theorem
# Original DSL diagram: positively oriented boundary C with a swirling vector field F = <-y, x>.

scene(min=(-3.2,-2.4), max=(3.4,2.6), size=(7,5), grid=true, grid_step=1, axes=true)

style boundary = {color: black, weight: 2.1, samples: 420, z: 6}
style field_s = {color: gray, weight: 0.9, arrow_size: 7, z: 2}
style tangent_s = {color: blue, weight: 2, arrow_size: 12, z: 9}
style normal_s = {color: red, weight: 1.4, pattern: dashed, arrow_size: 10, z: 8}
style point_s = {color: black, size: 24, z: 10}
style label_s = {color: black, font_size: 12, z: 20}

C = ParametricCurve(pt(1.75*cos(t) + 0.32*cos(3*t), 1.08*sin(t) + 0.22*sin(2*t)), t = 0..2*pi)

draw C @ boundary

# Rotational vector field samples around the region.
draw arrow(pt(-2.2,-1.2), 0.24*vec(1.2,-2.2)) @ field_s
draw arrow(pt(-1.1,-1.2), 0.24*vec(1.2,-1.1)) @ field_s
draw arrow(pt(0,-1.2), 0.24*vec(1.2,0)) @ field_s
draw arrow(pt(1.1,-1.2), 0.24*vec(1.2,1.1)) @ field_s
draw arrow(pt(2.2,-1.2), 0.24*vec(1.2,2.2)) @ field_s

draw arrow(pt(-2.2,0), 0.24*vec(0,-2.2)) @ field_s
draw arrow(pt(-1.1,0), 0.24*vec(0,-1.1)) @ field_s
draw arrow(pt(1.1,0), 0.24*vec(0,1.1)) @ field_s
draw arrow(pt(2.2,0), 0.24*vec(0,2.2)) @ field_s

draw arrow(pt(-2.2,1.2), 0.24*vec(-1.2,-2.2)) @ field_s
draw arrow(pt(-1.1,1.2), 0.24*vec(-1.2,-1.1)) @ field_s
draw arrow(pt(0,1.2), 0.24*vec(-1.2,0)) @ field_s
draw arrow(pt(1.1,1.2), 0.24*vec(-1.2,1.1)) @ field_s
draw arrow(pt(2.2,1.2), 0.24*vec(-1.2,2.2)) @ field_s

P = curve_at(C, 0.72)
T = unit_tangent(C, 0.72)
N = normal_left(C, 0.72)

draw marker(P) @ point_s
draw arrow(P, 0.60*T) @ tangent_s
draw arrow(P, 0.42*N) @ normal_s
draw label(P, "$C$") @ {offset: vec(0.15, -0.22)}
draw label(P + 0.60*T, "$d\\mathbf{r}$") @ {offset: vec(0.08, 0.08), color: blue}
draw label(P + 0.42*N, "$\\mathbf{n}$") @ {offset: vec(0.06, 0.08), color: red}
draw label(pt(-2.65, 2.18), "$\\oint_C \\mathbf{F}\\cdot d\\mathbf{r}$") @ label_s
draw label(pt(-2.62, -2.05), "$\\mathbf{F}=\\langle -y,x\\rangle$") @ {font_size: 11, color: gray, z: 20}
