scene(min=(-2,-2), max=(2,2), grid=true)

O = pt(0,0)
c = Circle(O, 1)
P = curve_at(c, pi/4)
T = unit_tangent(c, pi/4)
N = normal_left(c, pi/4)

draw c
draw marker(P)
draw arrow(P, 0.5*T) @ {color: blue}
draw arrow(P, 0.5*N) @ {color: red}
draw label(P, "$P$") @ {offset: vec(0.1, 0.1)}
