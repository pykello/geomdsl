scene(min=(-0.7,-0.4), max=(3.5,3.25), size=(6.8,5.2), grid=false, axes=false)

defaults {
  curve: {color: black, weight: 1.6, samples: 16, z: 10}
  label: {font_size: 13, z: 20}
}

style top_fill = {color: "#ffe8a3", opacity: 0.70, z: 1}
style side_fill = {color: "#f4b37b", opacity: 0.58, z: 2}
style front_fill = {color: "#8ecae6", opacity: 0.62, z: 3}
style edge = {color: "#1f2933", weight: 1.8, z: 10}
style hidden = {color: "#7a8691", weight: 1.1, pattern: dashed, z: 9}

# A hand-projected cube in 2D.
A = pt(0, 0)
B = pt(2.2, 0.25)
D = pt(-0.25, 1.85)
C = pt(1.95, 2.10)

depth = vec(0.85, 0.62)
A2 = A + depth
B2 = B + depth
C2 = C + depth
D2 = D + depth

front = quad(A, B, C, D)
right = quad(B, B2, C2, C)
top = quad(D, C, C2, D2)

# Face fills first, outlines second.
draw fill(top) @ top_fill
draw fill(right) @ side_fill
draw fill(front) @ front_fill

draw front @ edge

draw LineSegment(B, B2) @ edge
draw LineSegment(C, C2) @ edge
draw LineSegment(D, D2) @ edge

draw LineSegment(B2, C2) @ edge
draw LineSegment(C2, D2) @ edge

# A few hidden/back edges give the projection context without dominating.
draw LineSegment(A, A2) @ hidden
draw LineSegment(A2, B2) @ hidden
draw LineSegment(A2, D2) @ hidden

draw label(pt(-0.48, 3.02), "filled projected cube") @ {anchor: left, font_size: 14}
