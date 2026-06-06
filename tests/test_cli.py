import subprocess
import sys


def test_cli_dump_ast(tmp_path):
    src = tmp_path / "a.geom"
    src.write_text("draw marker(pt(0,0))", encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "geomdsl.cli", str(src), "--dump-ast"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "DrawStmt" in result.stdout


def test_cli_dump_ast_expands_include(tmp_path):
    common = tmp_path / "common.geom"
    src = tmp_path / "a.geom"
    common.write_text("A = pt(0,0)", encoding="utf-8")
    src.write_text('include "common.geom"\ndraw marker(A)', encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "geomdsl.cli", str(src), "--dump-ast"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "IncludeStmt" not in result.stdout
    assert "Assignment" in result.stdout


def test_cli_bad_input(tmp_path):
    src = tmp_path / "bad.geom"
    src.write_text("A = pt(1,)", encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "geomdsl.cli", str(src), "--dump-ast"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "line" in result.stderr
