import pytest

from geomdsl import evaluate
from geomdsl.errors import GeomValueError


@pytest.mark.parametrize(
    "source",
    [
        "bad = 1 / 0",
        "bad = vec(1, 2) / 0",
        "bad = 0 ^ -1",
        "bad = sqrt(-1)",
        "bad = log(-1)",
    ],
)
def test_invalid_math_reports_geom_value_error(source):
    with pytest.raises(GeomValueError):
        evaluate(source)
