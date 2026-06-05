scene(min=(-2,-1.5), max=(5.5,4.5), size=(7,5), grid=false, axes=false)

O = pt(0, 0)
c = ParametricCurve(pt(0.4 + 4*t, 1.8 + 0.9*sin(pi*(t - 0.25)) + 0.2*t), t = -1..1)
P = curve_at(c, 0.48)
v = vec(0.7, 1.2)

draw c
draw marker(P)
draw arrow(P, v)
draw label(P + v, "$\\mathbf{f}(x,y,z)$") @ {offset: vec(0.1, 0.1)}
