scene(
  min=(-2,-1.5), max=(5.5,4.5), size=(7,5),
  grid=false, axes=false,
  frame=false, ticks=false, tick_labels=false
)

# A parametric path with a vector attached at one sampled point.
start = pt(0.4, 1.8)
span = vec(4, 0.2)
wave = vec(0, 0.9)
sample_t = 0.48
force = vec(0.7, 1.2)

c = ParametricCurve(start + t*span + sin(pi*(t - 0.25))*wave, t = -1..1)
P = curve_at(c, sample_t)

draw c
draw marker(P)
draw arrow(P, force)
draw label(P + force, "$\\mathbf{f}(x,y,z)$") @ {offset: vec(0.1, 0.1)}
