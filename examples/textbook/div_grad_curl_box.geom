scene(
  min=(-1.55,-1.45), max=(4.15,3.10), size=(4.5,3.7),
  frame=false, ticks=false, tick_labels=false,
  axes=false, grid=false
)

# Oblique projection only: z goes up, y goes right, x goes down-left.
projection(
  origin=pt(0,0),
  x=vec(-0.70,-0.78), y=vec(1,0), z=vec(0,1),
  scale=1
)

defaults {
  curve:  {color: "#202020", weight: 1.55, z: 5}
  marker: {color: "#202020", size: 78, z: 20}
  label:  {color: "#202020", font_size: 16, z: 30}
  arrow:  {color: "#202020", weight: 1.55, arrow_size: 12, z: 18}
}

style hidden = {color: "#202020", weight: 1.35, pattern: dashed, z: 4}

O = pt3(0, 0, 0)

# Coordinate axes in projected 3D.
draw project(segments3(
  O, pt3(1.75,0,0),
  O, pt3(0,4.35,0),
  O, pt3(0,0,2.85)
))

draw group(
  label(project(pt3(1.92,0,0)), "$x$"),
  label(project(pt3(0,4.55,0)), "$y$"),
  label(project(pt3(0,0,3.02)), "$z$")
)

# The volume element. Build all top-face points from one base corner.
box_base = pt3(0.35,1.30,0)
box_x = vec3(1.00,0,0)
box_y = vec3(0,2.45,0)
box_z = vec3(0,0,2.02)

box = box3(box_base, box_x + box_y + box_z)

top_front_left = box_base + box_x + box_z
top_front_right = top_front_left + box_y
top_back_right = box_base + box_y + box_z
top_back_left = box_base + box_z

draw project(box_hidden3(box)) @ hidden
draw project(box_visible3(box, 0.25))

# Counterclockwise circulation arrows, one centered on each top edge.
draw group(
  arrow_on(segment3(top_front_left, top_front_right), 0.42, 0.35),
  arrow_on(segment3(top_front_right, top_back_right), 0.50, 0.30),
  arrow_on(segment3(top_back_right, top_back_left), 0.50, 0.35),
  arrow_on(segment3(top_back_left, top_front_left), 0.38, 0.28),
  label(project(top_back_left + 0.47*box_x - 0.16*box_y + 0.09*box_z), "$\\Delta x$"),
  label(project(top_front_left + 0.36*box_y - 0.10*box_z), "$\\Delta y$")
) @ {arrow_size: 9}

# Mark the representative point (x,y,z) on the top face and add a leader.
P = top_back_left + 0.47*box_x + 0.49*box_y

draw group(
  marker(project(P)),
  label(project(P - 0.54*box_x + 0.32*box_z), "$(x,y,z)$"),
  project(segment3(P - 0.48*box_x + 0.19*box_z, P))
)
