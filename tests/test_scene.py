from geomdsl import evaluate
from geomdsl.values import Point


def test_scene_configuration():
    scene = evaluate("scene(min=(-1,-2), max=(3,4), size=(7,5), grid=true, axes=true, frame=false, ticks=false, tick_labels=false)")
    assert scene.min == Point(-1, -2)
    assert scene.max == Point(3, 4)
    assert scene.size == (7, 5)
    assert scene.grid is True
    assert scene.axes is True
    assert scene.frame is False
    assert scene.ticks is False
    assert scene.tick_labels is False


def test_scene_graph_contains_drawables():
    scene = evaluate('P = pt(1, 2)\ndraw marker(P) @ {size: 5}\ndraw label(P, "$P$") @ {offset: vec(0.1, 0.2)}')
    assert len(scene.drawables) == 2
    assert scene.drawables[0].kind == "marker"
    assert scene.drawables[1].kind == "label"
