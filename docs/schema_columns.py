"""Sphinx directive rendering the columns of each table block of a schema."""

import re
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.statemachine import StringList
from ruamel.yaml import YAML
from sphinx.util.nodes import nested_parse_with_titles


def described(description):
    """A schema description as one line of reStructuredText."""
    return re.sub(r"`([^`]+)`", r"``\1``", " ".join(description.split()))


def columns(block):
    """A table block's columns, required then optional, as (header, unit, meaning)."""
    required = []
    for part in block.get("allOf", []):
        table = part.get("properties", {})
        if "headers" in table:
            required = [(header["const"], unit["const"],
                         described(header.get("description", "")))
                        for header, unit in zip(table["headers"]["items"],
                                                table["units"]["items"])]
    optional = [(header, column["unit"], "*Optional.* " + described(column["description"]))
                for header, column in block.get("optionalColumns", {}).items()]
    return required + optional


def column_table(name, rows):
    """A list-table of one block's columns, as reStructuredText lines."""
    lines = [f".. list-table:: ``{name}``", "   :header-rows: 1", "   :widths: 2 1 6", "",
             "   * - Column", "     - Unit", "     - Meaning"]
    for header, unit, meaning in rows:
        lines += [f"   * - ``{header}``", f"     - ``{unit}``", f"     - {meaning}"]
    return lines + [""]


class SchemaColumns(Directive):
    """`.. schema-columns:: <path>`: one column table per table block, in schema order."""

    required_arguments = 1

    def run(self):
        source = Path(self.state.document.current_source).parent / self.arguments[0]
        schema = YAML(typ="safe").load(source.read_text())
        lines = []
        for name, block in schema["properties"].items():
            rows = columns(block)
            if rows:
                lines += column_table(name, rows)
        section = nodes.container()
        nested_parse_with_titles(self.state, StringList(lines, source=str(source)), section)
        return section.children


def setup(app):
    app.add_directive("schema-columns", SchemaColumns)
    return {"parallel_read_safe": True}
