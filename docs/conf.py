# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

"""Sphinx configuration for awesIO documentation.

This configuration follows the windIO documentation architecture, adapted for
Airborne Wind Energy (AWE) systems. Key features:
- Auto-generation of HTML schema reference pages from YAML schemas
- Multi-version documentation support via sphinx-multiversion
- GitHub Pages deployment compatibility
- Read the Docs theme integration
"""

import os
import sys
from pathlib import Path

# -- Path setup --------------------------------------------------------------
# Add the project root to the path for autodoc to find modules
projectRoot = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(projectRoot / "src"))
sys.path.insert(0, str(projectRoot / "docs"))

# -- Project information -----------------------------------------------------
project = "awesIO"
copyright = "2026, awesIO Developers"
author = "awesIO Developers"
release = "0.1.0"
version = "0.1"

# Project description for meta tags
description = "YAML schemas for Airborne Wind Energy systems"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx-jsonschema",
]

try:
    import sphinx_multiversion  # noqa: F401
except ImportError:
    print("Warning: sphinx_multiversion not installed; skipping multi-version support.")
else:
    extensions.append("sphinx_multiversion")

# Templates path
templates_path = ["_templates"]

# Patterns to exclude from source files
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The master toctree document
master_doc = "index"

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"

# Logo configuration - appears on top left of all pages
html_logo = "logo/Final logo awesIO.svg"

# Theme options for furo
html_theme_options = {
    "navigation_with_keys": True,
}

# Static files path (custom CSS, generated schema HTML, etc.)
html_static_path = ["_static"]

# Custom CSS
html_css_files = [
    "custom.css",
]

# HTML context for templates
html_context = {
    "display_github": True,
    "github_user": "awegroup",
    "github_repo": "awesIO",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# -- Options for sphinx-multiversion -----------------------------------------
# Whitelist pattern for tags (x.y.z)
smv_tag_whitelist = r"^v\d+\.\d+\.\d+$"

# Whitelist pattern for branches
smv_branch_whitelist = r"^(main|develop)$"

# Whitelist pattern for remotes
smv_remote_whitelist = r"^origin$"

# Pattern for released versions
smv_released_pattern = r"^refs/tags/v\d+\.\d+\.\d+$"

# Format for versioned output directories
smv_outputdir_format = "{ref.name}"

# -- Options for intersphinx -------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

# -- Napoleon settings -------------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# -- Autodoc settings --------------------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}


