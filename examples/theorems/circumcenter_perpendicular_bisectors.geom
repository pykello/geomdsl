scene(min=(-2.6,-1.35), max=(2.75,2.15), size=(7.0,4.8), grid=false, axes=false)

defaults {
  curve: {color: "#1f2933", weight: 1.5, z: 10}
  marker: {color: "#111827", size: 22, z: 20}
  label: {font_size: 13, z: 30}
}

style triangle = {color: "#8ecae6", opacity: 0.28, z: 1}
style edge = {color: "#1f2933", weight: 2.0, z: 10}
style bisector = {color: blue, weight: 1.3, pattern: dashed, z: 4}
style circle_s = {color: red, weight: 1.4, z: 3}

A = pt(-1.65, -0.75)
B = pt(1.85, -0.55)
C = pt(0.42, 1.48)

ab = perpendicular_bisector(A, B)
ac = perpendicular_bisector(A, C)
O = intersect(ab, ac)
circ = circle_through(O, A)
tri = polygon(A, B, C)

draw fill(tri) @ triangle
draw circ @ circle_s
draw tri @ edge
draw ab @ bisector
draw ac @ bisector

draw marker(A)
draw marker(B)
draw marker(C)
draw marker(O) @ {color: red, size: 30}

draw label(A, "$A$") @ {offset: vec(-0.16, -0.13)}
draw label(B, "$B$") @ {offset: vec(0.15, -0.13)}
draw label(C, "$C$") @ {offset: vec(0.08, 0.16)}
draw label(O, "$O$") @ {offset: vec(0.14, 0.14)}

draw label(pt(-2.35, 1.88), "circumcenter from perpendicular bisectors") @ {anchor: left, font_size: 14}
