from geomdsl import evaluate
from geomdsl.errors import GeomTypeError
from geomdsl.values import Vector


def test_named_style_applies_to_drawable():
    scene = evaluate("""
style redline = {color: red, weight: 2, pattern: dashed, z: 5}
draw LineSegment(pt(0,0), pt(1,1)) @ redline
""")
    d = scene.drawables[0]
    assert d.style.get("color") == "red"
    assert d.style.get("weight") == 2
    assert d.style.get("pattern") == "dashed"
    assert d.style.get("z") == 5


def test_defaults_apply_to_marker():
    scene = evaluate("""
defaults {
  marker: {color: red, size: 9}
}
P = pt(1, 2)
draw marker(P)
""")
    d = scene.drawables[0]
    assert d.style.get("color") == "red"
    assert d.style.get("size") == 9


def test_inline_label_offset():
    scene = evaluate('P = pt(1,2)\ndraw label(P, "$P$") @ {offset: vec(0.1, 0.2)}')
    assert scene.drawables[0].style.get("offset") == Vector(0.1, 0.2)


def test_point_label_uses_default_readable_offset():
    scene = evaluate('P = pt(1,2)\ndraw point_label(P, "$P$")')
    label = scene.drawables[0]
    assert label.kind == "label"
    assert label.data["point"].x == 1
    assert label.data["text"] == "$P$"
    assert label.style.get("offset") == Vector(0.12, 0.12)
    assert label.style.get("anchor") == "bottom-left"


def test_point_label_offset_can_be_overridden():
    scene = evaluate('P = pt(1,2)\ndraw point_label(P, "$P$") @ {offset: vec(-0.1, 0)}')
    assert scene.drawables[0].style.get("offset") == Vector(-0.1, 0)


def test_invalid_style_enum_is_rejected():
    try:
        evaluate("draw LineSegment(pt(0,0), pt(1,1)) @ {pattern: dahsed}")
    except GeomTypeError as exc:
        assert "pattern" in str(exc)
    else:
        raise AssertionError("expected GeomTypeError")
