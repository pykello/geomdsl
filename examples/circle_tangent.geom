scene(
  min=(-1.65,-1.45), max=(1.85,1.65), size=(6.4,5.4),
  grid=false, axes=true,
  frame=false, ticks=false, tick_labels=false
)

defaults {
  curve:  {color: black, weight: 2.0, samples: 420}
  marker: {color: black, size: 28, z: 10}
  arrow:  {weight: 2.0, arrow_size: 13, z: 8}
  label:  {font_size: 13, z: 20}
}

style tangent = {color: blue, weight: 2.2, arrow_size: 14}
style normal = {color: red, weight: 2.0, arrow_size: 13}
style radius = {color: gray, weight: 1.2, pattern: dashed, arrow_head: false, z: 4}
style guide = {color: gray, weight: 1.0, pattern: dotted, z: 3, samples: 20}

# A unit circle with tangent and normal vectors at one point.
theta = pi/4
tangent_len = 0.55
normal_len = 0.45
guide_len = 0.70

O = pt(0,0)
c = Circle(O, 1)
P = curve_at(c, theta)
T = unit_tangent(c, theta)
N = normal_left(c, theta)

draw c

draw arrow(O, P - O) @ radius
draw LineSegment(P - guide_len*T, P + guide_len*T) @ guide

draw marker(O) @ {size: 18, color: gray}
draw marker(P) @ {size: 34}

draw arrow(P, tangent_len*T) @ tangent
draw arrow(P, normal_len*N) @ normal

draw label(O, "$O$") @ {offset: vec(-0.16, -0.16), color: gray}
draw label(P, "$\\mathbf{P}$") @ {offset: vec(0.12, 0.10), anchor: left}
draw label(P + tangent_len*T, "$\\mathbf{T}$") @ {offset: vec(-0.22, 0.10), color: blue}
draw label(P + normal_len*N, "$\\mathbf{N}$") @ {offset: vec(0.10, -0.02), color: red, anchor: left}
