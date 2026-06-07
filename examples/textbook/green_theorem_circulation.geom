# Inspired by OpenStax Calculus Volume 3, 6.4 Green's Theorem:
# https://openstax.org/books/calculus-volume-3/pages/6-4-greens-theorem
# Original DSL diagram: positively oriented boundary C with a swirling vector field F = <-y, x>.

scene(
  min=(-2.85,-2.15), max=(2.95,2.25), size=(7,5.2),
  grid=false, axes=false,
  frame=false, ticks=false, tick_labels=false
)

defaults {
  curve:  {color: black, weight: 2.0, samples: 420}
  marker: {color: black, size: 28, z: 12}
  arrow:  {weight: 1.6, arrow_size: 11, z: 8}
  label:  {font_size: 13, z: 20}
}

style boundary = {color: black, weight: 2.3, samples: 520, z: 8}
style field_s = {color: gray, weight: 1.1, arrow_size: 9, opacity: 0.9, z: 2}
style circulation = {color: blue, weight: 2.2, arrow_size: 14, z: 12}
style normal_s = {color: red, weight: 1.8, arrow_size: 12, z: 11}
style label_s = {color: black, font_size: 13, z: 20}

C = ParametricCurve(pt(1.55*cos(t) + 0.30*cos(3*t), 0.96*sin(t) + 0.18*sin(2*t)), t = 0..2*pi)
field_scale = 0.24
outer_field_scale = 0.22

draw C @ boundary

# Swirling vector field samples around the boundary, kept outside the main region.
draw arrow(pt(-2.15,1.25), field_scale*vec(-1.25,-2.15)) @ field_s
draw arrow(pt(-1.20,1.35), field_scale*vec(-1.35,-1.20)) @ field_s
draw arrow(pt(0.35,1.55), field_scale*vec(-1.55,0.35)) @ field_s
draw arrow(pt(1.75,1.25), field_scale*vec(-1.25,1.75)) @ field_s

draw arrow(pt(-2.20,-1.05), field_scale*vec(1.05,-2.20)) @ field_s
draw arrow(pt(-1.05,-1.40), field_scale*vec(1.40,-1.05)) @ field_s
draw arrow(pt(0.50,-1.52), field_scale*vec(1.52,0.50)) @ field_s
draw arrow(pt(1.95,-1.05), field_scale*vec(1.05,1.95)) @ field_s

draw arrow(pt(2.22,0.10), outer_field_scale*vec(-0.10,2.22)) @ field_s
draw arrow(pt(-2.22,0.08), outer_field_scale*vec(-0.08,-2.22)) @ field_s

# Highlight one boundary point with tangent direction and outward normal.
highlight_t = 0.68
tangent_len = 0.55
normal_len = 0.40
P = curve_at(C, highlight_t)
T = unit_tangent(C, highlight_t)
N = normal_left(C, highlight_t)

draw marker(P)
draw arrow(P, tangent_len*T) @ circulation
draw arrow(P, normal_len*N) @ normal_s

draw label(P, "$P$") @ {offset: vec(0.16, -0.20), anchor: left}
draw label(P + tangent_len*T, "$d\\mathbf{r}$") @ {offset: vec(-0.16, 0.14), color: blue}
draw label(P + normal_len*N, "$\\mathbf{n}$") @ {offset: vec(0.05, -0.13), color: red, anchor: left}
draw label(pt(1.88,0.12), "$C$") @ {font_size: 14, anchor: left}

draw label(pt(-2.45,1.92), "$\\oint_C \\mathbf{F}\\cdot d\\mathbf{r}$") @ {font_size: 15, anchor: left}
draw label(pt(-2.45,-1.88), "$\\mathbf{F}=\\langle -y,x\\rangle$") @ {font_size: 12, color: gray, anchor: left}
draw label(pt(-0.58,-1.88), "positive orientation") @ {font_size: 11, color: blue, anchor: left}
