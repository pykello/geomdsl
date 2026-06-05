# Inspired by OpenStax Calculus Volume 3, 6.4 Green's Theorem:
# https://openstax.org/books/calculus-volume-3/pages/6-4-greens-theorem
# Original DSL diagram: positively oriented boundary C with a swirling vector field F = <-y, x>.

scene(min=(-3,-2.4), max=(3.4,2.7), size=(7,5), grid=true, grid_step=1, axes=true)

style boundary = {color: black, weight: 2.2, samples: 420, z: 5}
style field_s = {color: gray, weight: 1, arrow_size: 8, z: 1}
style tangent_s = {color: blue, weight: 2, arrow_size: 12, z: 8}
style normal_s = {color: red, weight: 1.5, pattern: dashed, arrow_size: 10, z: 7}
style point_s = {color: black, size: 24, z: 10}
style label_s = {color: black, font_size: 12, z: 20}

C = ParametricCurve(pt(1.8*cos(t) + 0.35*cos(3*t), 1.15*sin(t) + 0.25*sin(2*t)), t = 0..2*pi)

draw C @ boundary

# Sample vector field arrows, manually placed to keep the DSL v0.1 explicit.
draw arrow(pt(-2,-1), 0.28*vec(1,-2)) @ field_s
draw arrow(pt(-1,-1), 0.28*vec(1,-1)) @ field_s
draw arrow(pt(0,-1), 0.28*vec(1,0)) @ field_s
draw arrow(pt(1,-1), 0.28*vec(1,1)) @ field_s
draw arrow(pt(2,-1), 0.28*vec(1,2)) @ field_s

draw arrow(pt(-2,0), 0.28*vec(0,-2)) @ field_s
draw arrow(pt(-1,0), 0.28*vec(0,-1)) @ field_s
draw arrow(pt(1,0), 0.28*vec(0,1)) @ field_s
draw arrow(pt(2,0), 0.28*vec(0,2)) @ field_s

draw arrow(pt(-2,1), 0.28*vec(-1,-2)) @ field_s
draw arrow(pt(-1,1), 0.28*vec(-1,-1)) @ field_s
draw arrow(pt(0,1), 0.28*vec(-1,0)) @ field_s
draw arrow(pt(1,1), 0.28*vec(-1,1)) @ field_s
draw arrow(pt(2,1), 0.28*vec(-1,2)) @ field_s

P = curve_at(C, 0.70)
T = unit_tangent(C, 0.70)
N = normal_left(C, 0.70)

draw marker(P) @ point_s
draw arrow(P, 0.65*T) @ tangent_s
draw arrow(P, 0.45*N) @ normal_s
draw label(P, "$C$") @ {offset: vec(0.18, -0.18)}
draw label(P + 0.65*T, "$d\\mathbf{r}$") @ {offset: vec(0.10, 0.10), color: blue}
draw label(P + 0.45*N, "$\\mathbf{n}$") @ {offset: vec(0.08, 0.08), color: red}
draw label(pt(-2.6, 2.25), "$\\oint_C \\mathbf{F}\\cdot d\\mathbf{r}$") @ label_s
