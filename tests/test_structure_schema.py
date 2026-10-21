"""Conformance tests for structure_schema.yml and the examples it is written for."""

import hashlib
import math
import re
import warnings
from pathlib import Path

import pytest

from awesio.validator import validate
from awesio.yaml import load_yaml

EXAMPLE_DIR = Path(__file__).parent.parent / "examples/structure"
EXAMPLES = sorted(EXAMPLE_DIR.glob("*.yml"))
SCHEMA = Path(__file__).parent.parent / "src/awesio/schemas/structure_schema.yml"
CONVENTIONS = Path(__file__).parent.parent / "docs/source/conventions.rst"


@pytest.fixture(params=EXAMPLES, ids=lambda path: path.stem)
def structure(request):
    """Every .yml in examples/structure, so the invariants below cover all of them."""
    return load_yaml(request.param)


@pytest.fixture
def beam():
    """The beam kite, the one example filling every block the cases below break."""
    return load_yaml(EXAMPLE_DIR / "v3_beam_structure.yml")


def rows(structure, block):
    """An absent optional block means the same as an empty one."""
    return structure.get(block, {"data": []})["data"]


def a_point_on_a_body(structure):
    """Most rows leave `body` null; breaking that column needs one that does not."""
    return next(row for row in rows(structure, "points") if row[2] is not None)


def append_column(table, header, value, unit=None):
    """Append a column to every row of `table`, leaving its units short without `unit`."""
    table["headers"].append(header)
    if unit is not None:
        table["units"].append(unit)
    for row in table["data"]:
        row.append(value)


def drop_column(table, header):
    """Remove the column under `header` from `table`, wherever it stands."""
    i = table["headers"].index(header)
    for row in [table["headers"], table["units"], *table["data"]]:
        del row[i]


def move_column_to_the_end(table, header):
    """Move the column under `header` behind every other, a tool's columns included."""
    i = table["headers"].index(header)
    for row in [table["headers"], table["units"], *table["data"]]:
        row.append(row.pop(i))


def append_header(table, header, unit):
    """Append a header and its unit to `table`, leaving every row one value short."""
    table["headers"].append(header)
    table["units"].append(unit)


def assert_valid(data):
    """`validate` warns rather than raises, so a passing file must warn nothing."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        validate(data)


def assert_invalid(data):
    with pytest.warns(UserWarning, match="Validation failed"):
        validate(data)


def connectivity_preimage(structure):
    """One-based row numbers, so zero-based readers do not disagree with the writer."""
    def section(named, paired):
        row_number = {row[0]: i + 1 for i, row in enumerate(rows(structure, named))}
        return f"{len(row_number)};" + "".join(
            f"{row_number[a]},{row_number[b]};"
            for _, (a, b), *_ in rows(structure, paired)
        )

    point_number = {row[0]: i + 1 for i, row in enumerate(rows(structure, "points"))}
    faces = rows(structure, "canopy_faces")
    corners = "".join(",".join(str(point_number[point]) for point in face[2]) + ";"
                      for face in faces)
    return (section("points", "segments") + section("bodies", "tubes")
            + f"{len(faces)};{corners}")


def test_connectivity_sha_hashes_the_preimage(structure):
    digest = hashlib.sha256(connectivity_preimage(structure).encode()).hexdigest()
    assert digest == structure["metadata"]["connectivity_sha"]


def test_the_documented_preimage_is_what_the_rule_produces():
    """The line `metadata.connectivity_sha` quotes, so the two cannot drift apart."""
    three_in_a_row = {"points": {"data": [["a"], ["b"], ["c"]]},
                      "segments": {"data": [["s1", ("a", "b")], ["s2", ("b", "c")]]},
                      "bodies": {"data": [["x"], ["y"]]},
                      "tubes": {"data": [["t1", ("x", "y")]]},
                      "canopy_faces": {"data": [["f1", "c", ["a", "b", "c"]]]}}
    assert connectivity_preimage(three_in_a_row) == "3;1,2;2,3;2;1,2;1;1,2,3;"


def test_every_unit_the_schema_pins_is_spelled_on_the_conventions_page():
    units_section = CONVENTIONS.read_text().split("Units\n-----")[1].split("\n---")[0]
    listed = set(re.findall(r"\* - ``([^`]+)``", units_section))
    for name, block in load_yaml(SCHEMA)["properties"].items():
        for part in block.get("allOf", []):
            for item in part.get("properties", {}).get("units", {}).get("items", []):
                assert item["const"] in listed, name
        for header, column in block.get("optionalColumns", {}).items():
            assert column["unit"] in listed, header


def test_n_points_agrees_with_the_points_block(structure):
    assert structure["metadata"]["n_points"] == len(structure["points"]["data"])


def test_body_and_wing_frames_are_unit_quaternions(structure):
    """Draft-07 can hold `Q_KA2ENU` to four numbers but not to unit length."""
    for block in ("bodies", "wings"):
        for name, _, frame, *_ in rows(structure, block):
            assert math.isclose(math.hypot(*frame), 1.0, abs_tol=1e-12), name


def test_body_inertia_is_symmetric(structure):
    """Draft-07 can hold `extra_inertia_KA` to three rows but not to symmetry."""
    for name, *_, inertia in rows(structure, "bodies"):
        for i in range(3):
            for j in range(i):
                assert inertia[i][j] == inertia[j][i], name


def direction(start, end):
    """Unit vector from `start` to `end`."""
    span = [end_i - start_i for start_i, end_i in zip(start, end)]
    return [component / math.hypot(*span) for component in span]


def test_every_point_is_joined_to_the_rest(structure):
    """Segments, canopy faces, a point's body and tubes make the example one mechanism."""
    neighbours = {}

    def join(*names):
        for name in names:
            neighbours.setdefault(name, set()).update(names)

    for name, _, body, *_ in rows(structure, "points"):
        join(name, *([("body", body)] if body else []))
    for _, endpoints, *_ in rows(structure, "segments"):
        join(*endpoints)
    for _, pair, *_ in rows(structure, "tubes"):
        join(*(("body", body) for body in pair))
    for *_, corners in rows(structure, "canopy_faces"):
        join(*corners)
    reached, frontier = set(), [structure["points"]["data"][0][0]]
    while frontier:
        name = frontier.pop()
        if name not in reached:
            reached.add(name)
            frontier.extend(neighbours[name])
    assert {row[0] for row in rows(structure, "points")} <= reached


def test_stations_run_from_the_left_tip_to_the_right(beam):
    """Station rows run from the left wing tip to the right."""
    pos = {row[0]: row[3] for row in beam["points"]["data"]}
    span_axis = direction(pos["wing_le_10"], pos["wing_le_1"])

    def spanwise(members):
        return sum(sum(a * b for a, b in zip(span_axis, pos[point])) for point in members)

    along_span = [spanwise(members) / len(members)
                  for *_, members in beam["spanwise_stations"]["data"]]
    assert along_span == sorted(along_span, reverse=True)


def test_every_reference_resolves_to_a_named_row(structure):
    def names(block):
        return {row[0] for row in rows(structure, block)}

    points, segments, bodies = names("points"), names("segments"), names("bodies")
    materials = names("materials")
    for name, _, body, *_ in rows(structure, "points"):
        assert body is None or body in bodies, name
    for name, endpoints, _, _, material, *_ in rows(structure, "segments"):
        assert set(endpoints) <= points and material in materials, name
    for _, pair, *_ in rows(structure, "pulleys"):
        assert set(pair) <= segments
    for name, wing, members in rows(structure, "spanwise_stations"):
        assert wing in names("wings") and set(members) <= points, name
    for _, start, end, members in rows(structure, "tethers"):
        assert {start, end} <= points and set(members) <= segments
    for name, pair, _, _, material, *_ in rows(structure, "tubes"):
        assert set(pair) <= bodies and material in materials, name
    canopies = {name: material for name, _, _, material, *_ in rows(structure, "wings")}
    for name, material in canopies.items():
        assert material is None or material in materials, name
    with_a_canopy = {name for name, material in canopies.items() if material}
    for name, wing, corners, *_ in rows(structure, "canopy_faces"):
        assert wing in with_a_canopy and set(corners) <= points, name


@pytest.mark.parametrize(
    "label, mutate",
    [
        ("reordered headers",
         lambda d: d["points"]["headers"].reverse()),
        ("points in the CAD frame",
         lambda d: d["points"]["headers"].__setitem__(3, "pos_CAD")),
        ("a point's fixed flag given as a solver's dynamics type",
         lambda d: d["points"]["data"][0].__setitem__(1, "STATIC")),
        ("a point both held in the world and on a body",
         lambda d: a_point_on_a_body(d).__setitem__(1, True)),
        ("two-component pos_ENU",
         lambda d: d["points"]["data"][0].__setitem__(3, [0.0, 0.0])),
        ("a point's body given as an index",
         lambda d: a_point_on_a_body(d).__setitem__(2, 2)),
        ("a point with negative extra mass",
         lambda d: d["points"]["data"][3].__setitem__(4, -8.4)),
        ("a point row without its extra mass",
         lambda d: d["points"]["data"][3].pop()),
        ("a segment with three endpoints",
         lambda d: d["segments"]["data"][0][1].append("tether_2")),
        ("negative segment length",
         lambda d: d["segments"]["data"][0].__setitem__(2, -1.0)),
        ("a segment's material given as a number",
         lambda d: d["segments"]["data"][0].__setitem__(4, 970.0)),
        ("a material with an empty law name",
         lambda d: d["materials"]["data"][0].__setitem__(1, "")),
        ("a linear material without its Young's modulus",
         lambda d: d["materials"]["data"][0][2].pop("youngs_modulus")),
        ("a negative Young's modulus",
         lambda d: d["materials"]["data"][0][2].update(youngs_modulus=-5.5e10)),
        ("a membrane material holding a line's parameters",
         lambda d: d["materials"]["data"][2].__setitem__(2, d["materials"]["data"][0][2])),
        ("a breukels2011 material without C19",
         lambda d: d["materials"]["data"][3][2].pop("C19")),
        ("a breukels2011 material with a constant it does not define",
         lambda d: d["materials"]["data"][3][2].update(C20=1.0)),
        ("a material whose parameters are a list",
         lambda d: d["materials"]["data"][0].__setitem__(2, [970.0, 5.5e10])),
        ("a station holding a bare point name",
         lambda d: d["spanwise_stations"]["data"][0].__setitem__(2, "le_left")),
        ("a station without its wing",
         lambda d: d["spanwise_stations"]["data"][0].__setitem__(1, None)),
        ("a body inertia given as principal moments",
         lambda d: d["bodies"]["data"][0].__setitem__(4, [1.0, 1.0, 1.0])),
        ("a three-component body frame",
         lambda d: d["bodies"]["data"][0].__setitem__(2, [1.0, 0.0, 0.0])),
        ("a tube naming a null body",
         lambda d: d["tubes"]["data"][0][1].__setitem__(1, None)),
        ("a tube joining three bodies",
         lambda d: d["tubes"]["data"][0][1].append("kcu")),
        ("negative tube pressure",
         lambda d: d["tubes"]["data"][0].__setitem__(3, -1.0)),
        ("a tube's material given as a number",
         lambda d: d["tubes"]["data"][0].__setitem__(4, 42)),
        ("short segment row",
         lambda d: d["segments"]["data"][0].pop()),
        ("empty component name",
         lambda d: d["segments"]["data"][0].__setitem__(0, "")),
        ("tether segments given as indices",
         lambda d: d["tethers"]["data"][0].__setitem__(3, [1, 2, 3])),
        ("a winch without its drum radius",
         lambda d: d["winches"]["data"][0].pop()),
        ("a negative winch gear ratio",
         lambda d: d["winches"]["data"][0].__setitem__(3, -1.0)),
        ("missing connectivity_sha",
         lambda d: d["metadata"].pop("connectivity_sha")),
        ("truncated connectivity_sha",
         lambda d: d["metadata"].update(connectivity_sha="abc")),
        ("uppercase connectivity_sha",
         lambda d: d["metadata"].update(connectivity_sha="A" * 64)),
        ("awesIO_version without a patch component",
         lambda d: d["metadata"].update(awesIO_version="1.0")),
        ("another schema's name",
         lambda d: d["metadata"].update(schema="system_schema.yml")),
        ("missing segments block",
         lambda d: d.pop("segments")),
        ("a non-string appended header",
         lambda d: d["segments"]["headers"].append(42)),
        ("a header given twice",
         lambda d: append_column(d["segments"], "name", "seg", unit="-")),
        ("a negative diameter behind a tool's column",
         lambda d: (append_column(d["segments"], "damping_per_stiffness", 0.002, unit="s"),
                    move_column_to_the_end(d["segments"], "diameter"),
                    d["segments"]["data"][0].__setitem__(-1, -0.004))),
        ("a rest length in mm behind a tool's column",
         lambda d: (append_column(d["segments"], "damping_per_stiffness", 0.002, unit="s"),
                    move_column_to_the_end(d["segments"], "rest_length"),
                    d["segments"]["units"].__setitem__(-1, "mm"))),
        ("a row shorter than its appended headers",
         lambda d: append_header(d["segments"], "damping_per_stiffness", "s")),
        ("a row longer than its headers",
         lambda d: d["segments"]["data"][0].append(0.002)),
        ("an undeclared key inside metadata",
         lambda d: d["metadata"].update(tool="SAM")),
        ("an undeclared key beside a table's headers, units and data",
         lambda d: d["segments"].update(comment="bridle")),
        ("a table without its units",
         lambda d: d["segments"].pop("units")),
        ("a diameter in mm",
         lambda d: d["segments"]["units"].__setitem__(3, "mm")),
        ("a tube pressure in bar",
         lambda d: d["tubes"]["units"].__setitem__(3, "bar")),
        ("a required column without its unit",
         lambda d: d["points"]["units"].pop()),
        ("an appended column without its unit",
         lambda d: append_column(d["segments"], "damping_per_stiffness", 0.002)),
        ("an appended column with an empty unit",
         lambda d: append_column(d["segments"], "damping_per_stiffness", 0.002, unit="")),
        ("a canopy face with two corners",
         lambda d: d["canopy_faces"]["data"][0][2].__delitem__(slice(2))),
        ("a canopy face with a repeated corner",
         lambda d: d["canopy_faces"]["data"][0][2].__setitem__(
             1, d["canopy_faces"]["data"][0][2][0])),
        ("a segment from a point to itself",
         lambda d: d["segments"]["data"][0][1].__setitem__(
             1, d["segments"]["data"][0][1][0])),
        ("a canopy face with five corners",
         lambda d: d["canopy_faces"]["data"][0][2].append("wing_le_8")),
        ("a canopy material given as a number",
         lambda d: d["wings"]["data"][0].__setitem__(3, 42)),
        ("a canopy face without its wing",
         lambda d: d["canopy_faces"]["data"][0].__setitem__(1, None)),
        ("a wing without its origin", lambda d: drop_column(d["wings"], "pos_ENU")),
        ("a wing without its frame", lambda d: drop_column(d["wings"], "Q_KA2ENU")),
        ("a wing origin in millimetres",
         lambda d: d["wings"]["units"].__setitem__(1, "mm")),
        ("a wing frame of three numbers",
         lambda d: d["wings"]["data"][0][2].pop()),
    ],
)
def test_malformed_structures_are_rejected(beam, label, mutate):
    mutate(beam)
    assert_invalid(beam)


def test_optional_blocks_may_be_absent(structure):
    """An absent optional block means the same as an empty one."""
    for block in ("materials", "spanwise_stations", "pulleys", "tethers", "winches",
                  "bodies", "tubes", "wings", "canopy_faces"):
        structure.pop(block, None)
    for row in structure["points"]["data"]:
        row[2] = None
    assert_valid(structure)


def test_the_core_alone_is_a_valid_structure(structure):
    """Every column a block does not require may be left out, materials and all."""
    structure.pop("materials", None)
    for name, block in load_yaml(SCHEMA)["properties"].items():
        for header in block.get("optionalColumns", {}):
            if name in structure and header in structure[name]["headers"]:
                drop_column(structure[name], header)
    drop_column(structure["pulleys"], "efficiency")
    assert_valid(structure)


def test_a_material_may_name_any_law_with_any_parameters(beam):
    curve = {"strain": [0.0, 0.01], "force": [0.0, 80.0]}
    beam["materials"]["data"][0][1:] = ["tabulated", curve]
    assert_valid(beam)


def test_a_wing_may_have_no_canopy(structure):
    structure["wings"]["data"][0][3] = None
    structure.pop("canopy_faces")
    assert_valid(structure)


def test_a_reader_accepts_columns_appended_by_a_later_minor_version(structure):
    """Blocks are addressed by header, so appended columns must not break v1.0."""
    append_column(structure["segments"], "damping_per_stiffness", 0.002, unit="s")
    assert_valid(structure)
