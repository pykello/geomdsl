import subprocess
import sys

import pytest

from geomdsl import evaluate, render_file
from geomdsl.errors import GeomParseError


def test_evaluate_resolves_file_relative_include(tmp_path):
    common = tmp_path / "common.geom"
    main = tmp_path / "main.geom"
    common.write_text(
        "style hot = {color: red}\nP = pt(1, 2)\n",
        encoding="utf-8",
    )
    main.write_text(
        'include "common.geom"\ndraw marker(P) @ hot\n',
        encoding="utf-8",
    )

    scene = evaluate(main.read_text(encoding="utf-8"), base_path=main)

    assert scene.drawables[0].data["point"].x == 1
    assert scene.drawables[0].style.get("color") == "red"


def test_evaluate_include_requires_base_path():
    with pytest.raises(GeomParseError, match="base_path"):
        evaluate('include "common.geom"')


def test_include_cycle_reports_error(tmp_path):
    a = tmp_path / "a.geom"
    b = tmp_path / "b.geom"
    a.write_text('include "b.geom"\n', encoding="utf-8")
    b.write_text('include "a.geom"\n', encoding="utf-8")

    with pytest.raises(GeomParseError, match="cycle"):
        evaluate(a.read_text(encoding="utf-8"), base_path=a)


def test_render_file_resolves_include(tmp_path):
    common = tmp_path / "common.geom"
    main = tmp_path / "main.geom"
    out = tmp_path / "out.svg"
    common.write_text("P = pt(0, 0)\n", encoding="utf-8")
    main.write_text('include "common.geom"\ndraw marker(P)\n', encoding="utf-8")

    render_file(str(main), output=str(out))

    assert out.exists()
    assert out.stat().st_size > 0


def test_cli_dump_scene_resolves_include(tmp_path):
    common = tmp_path / "common.geom"
    main = tmp_path / "main.geom"
    common.write_text("P = pt(1, 2)\n", encoding="utf-8")
    main.write_text('include "common.geom"\ndraw marker(P)\n', encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "geomdsl.cli", str(main), "--dump-scene"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "drawables" in result.stdout
    assert "IncludeStmt" not in result.stdout
