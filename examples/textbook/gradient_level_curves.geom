# Inspired by LibreTexts/OpenStax discussion of gradients and level curves:
# https://math.libretexts.org/Bookshelves/Calculus/Calculus_%28OpenStax%29/14%253A_Differentiation_of_Functions_of_Several_Variables/14.06%253A_Directional_Derivatives_and_the_Gradient
# Original DSL diagram: level ellipses for f(x,y)=x^2+4y^2 and gradient arrows normal to them.

scene(min=(-3.35,-2.25), max=(3.35,2.35), size=(7,5), grid=true, grid_step=1, axes=true)

style level1 = {color: gray, weight: 0.9, pattern: dotted, samples: 360, z: 2}
style level2 = {color: gray, weight: 1.2, pattern: dashed, samples: 360, z: 3}
style level3 = {color: black, weight: 1.8, samples: 360, z: 4}
style grad_s = {color: blue, weight: 1.9, arrow_size: 12, z: 10}
style tangent_s = {color: red, weight: 1.4, pattern: dashed, arrow_size: 9, z: 9}

L1 = ParametricCurve(pt(0.75*cos(t), 0.375*sin(t)), t = 0..2*pi)
L2 = ParametricCurve(pt(1.45*cos(t), 0.725*sin(t)), t = 0..2*pi)
L3 = ParametricCurve(pt(2.25*cos(t), 1.125*sin(t)), t = 0..2*pi)

draw L1 @ level1
draw L2 @ level2
draw L3 @ level3

P = curve_at(L3, pi/5)
T = unit_tangent(L3, pi/5)

# Manual gradient vectors for f=x^2+4y^2 at selected points on level curves.
draw arrow(pt(1.82, 0.66), vec(0.48, 0.70)) @ grad_s
draw arrow(pt(0.70, 1.07), vec(0.20, 0.78)) @ grad_s
draw arrow(pt(-1.82, 0.66), vec(-0.48, 0.70)) @ grad_s
draw arrow(pt(-0.70, -1.07), vec(-0.20, -0.78)) @ grad_s
draw arrow(pt(1.17, -0.43), vec(0.34, -0.58)) @ grad_s

# Tangent vector at one highlighted point, perpendicular to the gradient direction.
draw marker(P) @ {size: 28, color: black, z: 12}
draw arrow(P, 0.62*T) @ tangent_s
draw label(P, "$P$") @ {offset: vec(0.12, 0.08), z: 20}
draw label(pt(2.28, 1.34), "$\\nabla f$") @ {color: blue, font_size: 13, z: 20}
draw label(P + 0.62*T, "$\\mathbf{T}$") @ {color: red, offset: vec(0.05, -0.12), z: 20}
draw label(pt(-3.02, 1.92), "$f(x,y)=x^2+4y^2$") @ {font_size: 13, anchor: left, z: 20}
