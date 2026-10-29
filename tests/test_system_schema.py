"""The optional onboard turbine of a soft kite's control system."""

import copy
import warnings
from pathlib import Path

import pytest

from awesio.validator import validate
from awesio.yaml import load_yaml

SYSTEM_EXAMPLE = (
    Path(__file__).parent.parent
    / "examples/system_config/soft_kite_pumping_ground_gen_system.yml"
)
TURBINE = {
    "name": "Onboard turbine",
    "type": "horizontal_axis_turbine",
    "version": 1.0,
    "structure": {
        "rotor_diameter": 0.5,
        "number_of_blades": 4,
        "mass": 2.8,
        "position_KA": [0.0, 0.0, 0.5],
    },
}


def validation_warnings(data):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        validate(data)
    return [str(warning.message) for warning in caught]


def with_turbine(turbine):
    system = load_yaml(SYSTEM_EXAMPLE)
    system["components"]["kites"][0]["control_system"]["turbine"] = turbine
    return system


def test_a_control_unit_may_carry_a_turbine():
    assert validation_warnings(with_turbine(TURBINE)) == []


def test_a_hanging_turbine_sits_below_the_control_unit():
    turbine = copy.deepcopy(TURBINE)
    turbine["structure"]["position_KA"] = [0.0, 0.0, -0.8]
    assert validation_warnings(with_turbine(turbine)) == []


@pytest.mark.parametrize("field", ["rotor_diameter", "mass", "position_KA"])
def test_a_turbine_states_its_size_mass_and_place(field):
    turbine = copy.deepcopy(TURBINE)
    del turbine["structure"][field]
    [warning] = validation_warnings(with_turbine(turbine))
    assert field in warning


def test_a_turbine_position_is_a_3_vector():
    turbine = copy.deepcopy(TURBINE)
    turbine["structure"]["position_KA"] = [0.0, 0.5]
    assert validation_warnings(with_turbine(turbine))


def test_a_turbine_keeps_to_its_listed_keys():
    turbine = copy.deepcopy(TURBINE)
    turbine["thrust_coefficient"] = 0.85
    [warning] = validation_warnings(with_turbine(turbine))
    assert "thrust_coefficient" in warning
