scene(min=(-2.45,-1.35), max=(2.6,2.2), size=(7.0,4.9), grid=false, axes=false)

defaults {
  curve: {color: "#1f2933", weight: 1.5, z: 10}
  marker: {color: "#111827", size: 22, z: 20}
  label: {font_size: 13, z: 30}
}

style triangle = {color: "#c7f9cc", opacity: 0.35, z: 1}
style edge = {color: "#1f2933", weight: 2.0, z: 10}
style altitude = {color: blue, weight: 1.4, pattern: dashed, z: 4}

A = pt(-1.65, -0.72)
B = pt(1.9, -0.52)
C = pt(0.08, 1.55)

BC = line_through(B, C)
AC = line_through(A, C)
hA = perpendicular(BC, A)
hB = perpendicular(AC, B)
H = intersect(hA, hB)
tri = polygon(A, B, C)

draw fill(tri) @ triangle
draw tri @ edge
draw hA @ altitude
draw hB @ altitude

draw marker(A)
draw marker(B)
draw marker(C)
draw marker(H) @ {color: red, size: 30}

draw label(A, "$A$") @ {offset: vec(-0.16, -0.14)}
draw label(B, "$B$") @ {offset: vec(0.15, -0.14)}
draw label(C, "$C$") @ {offset: vec(0.08, 0.16)}
draw label(H, "$H$") @ {offset: vec(0.14, 0.12)}

draw label(pt(-2.25, 1.92), "orthocenter from two altitudes") @ {anchor: left, font_size: 14}
