import matplotlib
matplotlib.use("Agg")


def test_jupyter_extension_loads():
    pytest = __import__("pytest")
    ipython_mod = pytest.importorskip("IPython")
    from IPython.terminal.interactiveshell import TerminalInteractiveShell

    ip = TerminalInteractiveShell.instance()
    ip.run_line_magic("load_ext", "geomdsl.jupyter")
    result = ip.run_cell_magic("geom", "", "draw marker(pt(0,0))")
    assert result is not None
