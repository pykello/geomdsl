# Inspired by LibreTexts/OpenStax discussion of gradients and level curves:
# https://math.libretexts.org/Bookshelves/Calculus/Calculus_%28OpenStax%29/14%253A_Differentiation_of_Functions_of_Several_Variables/14.06%253A_Directional_Derivatives_and_the_Gradient
# Original DSL diagram: level ellipses for f(x,y)=x^2+4y^2 and gradient arrows normal to them.

scene(min=(-3.2,-2.2), max=(3.4,2.4), size=(7,5), grid=true, grid_step=1, axes=true)

style level1 = {color: gray, weight: 1, pattern: dotted, samples: 360, z: 1}
style level2 = {color: gray, weight: 1.4, pattern: dashed, samples: 360, z: 2}
style level3 = {color: black, weight: 1.8, samples: 360, z: 3}
style grad_s = {color: blue, weight: 2, arrow_size: 12, z: 10}
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
draw arrow(pt(1.82, 0.66), vec(0.52, 0.75)) @ grad_s
draw arrow(pt(0.70, 1.07), vec(0.22, 0.95)) @ grad_s
draw arrow(pt(-1.82, 0.66), vec(-0.52, 0.75)) @ grad_s
draw arrow(pt(-0.70, -1.07), vec(-0.22, -0.95)) @ grad_s
draw arrow(pt(1.17, -0.43), vec(0.38, -0.66)) @ grad_s

# Tangent vector at one highlighted point, perpendicular to the gradient direction.
draw marker(P) @ {size: 28, color: black, z: 12}
draw arrow(P, 0.7*T) @ tangent_s
draw label(P, "$P$") @ {offset: vec(0.12, 0.10), z: 20}
draw label(pt(2.36, 1.35), "$\\nabla f$") @ {color: blue, font_size: 13, z: 20}
draw label(P + 0.7*T, "$\\mathbf{T}$") @ {color: red, offset: vec(0.05, -0.12), z: 20}
draw label(pt(-2.85, 1.95), "$f(x,y)=x^2+4y^2$") @ {font_size: 13, z: 20}
