"""The rules docs/source/conventions.rst states for every awesIO file, checked on every
schema's example."""

import math
import re
import warnings
from pathlib import Path

import pytest

from awesio.validator import validate
from awesio.yaml import load_yaml

EXAMPLES = Path(__file__).parent.parent / "examples"
CONVENTIONS = Path(__file__).parent.parent / "docs/source/conventions.rst"
STATED_VECTOR = r"``(o|Q_KA2ENU|p_ENU|p_KA) = \[([^\]]+)\]``"
OPERATIONAL_CONSTRAINTS = (
    "ground_gen/soft_kite_pumping_ground_gen_operational_constraints.yml"
)
EXAMPLE_FILES = [
    "system_config/soft_kite_pumping_ground_gen_system.yml",
    "structure/v3_beam_structure.yml",
    "structure/v3_psm_structure.yml",
    "wind_resource.yml",
    "ground_gen/soft_kite_pumping_ground_gen_power_curves.yml",
    OPERATIONAL_CONSTRAINTS,
]


@pytest.fixture(params=EXAMPLE_FILES)
def example(request):
    return load_yaml(EXAMPLES / request.param)


def validation_warnings(data):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        validate(data)
    return [str(warning.message) for warning in caught]


def test_example_conforms(example):
    assert validation_warnings(example) == []


def test_a_tool_may_add_top_level_blocks_of_any_shape(example):
    example["my_tool"] = {"solver": "rk4", "tolerances": [1e-6, 1e-8]}
    example["my_tool_notes"] = ["free", "form"]
    assert validation_warnings(example) == []


@pytest.mark.parametrize("reference", ["azimuth_reference", "reference_point"])
def test_terrain_zones_reject_a_reference_other_than_the_enu_origin(reference):
    constraints = load_yaml(EXAMPLES / OPERATIONAL_CONSTRAINTS)
    constraints["terrain_constraints"][reference] = "magnetic north"
    [warning] = validation_warnings(constraints)
    assert reference in warning


def test_wind_directions_are_bearings_in_degrees():
    wind_resource = load_yaml(EXAMPLES / "wind_resource.yml")
    wind_resource["wind_direction_bins"]["bin_edges"][-1] = 361.0
    [warning] = validation_warnings(wind_resource)
    assert "361.0 is greater than the maximum of 360" in warning


def test_terrain_zones_are_bearings_in_degrees():
    constraints = load_yaml(EXAMPLES / OPERATIONAL_CONSTRAINTS)
    constraints["terrain_constraints"]["azimuth_zones"][-1]["azimuth_range"][1] = 361.0
    [warning] = validation_warnings(constraints)
    assert "361.0 is greater than the maximum of 360" in warning


def rotation_matrix(quaternion):
    """The matrix of a unit quaternion `[w, x, y, z]`, as `v_to = R v_from`."""
    w, x, y, z = quaternion
    return [
        [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
        [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
        [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
    ]


def to_wing_frame(pos_ENU, origin, Q_KA2ENU):
    """`p_KA = Rᵀ (p_ENU − o)`, as the conventions page defines it."""
    offset = [p - o for p, o in zip(pos_ENU, origin)]
    columns = zip(*rotation_matrix(Q_KA2ENU))
    return [sum(r * d for r, d in zip(column, offset)) for column in columns]


def test_the_worked_example_lands_where_the_page_says():
    page = CONVENTIONS.read_text()
    stated = {
        name: [float(x) for x in value.split(",")]
        for name, value in re.findall(STATED_VECTOR, page)
    }
    assert set(stated) == {"o", "Q_KA2ENU", "p_ENU", "p_KA"}
    pos_KA = to_wing_frame(stated["p_ENU"], stated["o"], stated["Q_KA2ENU"])
    assert all(math.isclose(a, b, abs_tol=1e-12) for a, b in zip(pos_KA, stated["p_KA"]))


@pytest.mark.parametrize(
    "path, anchor",
    [("v3_beam_structure.yml", "ground_anchor"), ("v3_psm_structure.yml", "39")],
)
def test_the_v3_tether_hangs_straight_down_in_the_wing_frame(path, anchor):
    """The V3 kite is placed at 90° elevation, which puts its ground anchor on its
    wing's negative z axis."""
    structure = load_yaml(EXAMPLES / "structure" / path)
    [(_, origin, Q_KA2ENU, _)] = structure["wings"]["data"]
    pos_ENU = {row[0]: row[3] for row in structure["points"]["data"]}
    x, y, z = to_wing_frame(pos_ENU[anchor], origin, Q_KA2ENU)
    assert math.isclose(x, 0, abs_tol=1e-9) and math.isclose(y, 0, abs_tol=1e-9) and z < 0
