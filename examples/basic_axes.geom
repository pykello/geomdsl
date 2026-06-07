scene(
  min=(-2,-2), max=(5,5),
  grid=true, axes=true,
  frame=false, ticks=false, tick_labels=false
)

# Minimal coordinate-plane example: the axes and grid provide context,
# while the frame/ticks are hidden to keep attention on the origin.
O = pt(0, 0)
draw marker(O)
draw label(O, "$O$") @ {offset: vec(0.1, 0.1)}
