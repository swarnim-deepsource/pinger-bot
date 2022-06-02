"""Configuration file for the Sphinx documentation builder.

This file does only contain a selection of the most common options. For a
full list see the documentation:
http://www.sphinx-doc.org/en/master/config
"""

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
from datetime import date
from os import makedirs
from typing import Dict, List, Optional

import sphobjinv
from autoapi.mappers.python.objects import PythonModule
from packaging.version import parse as parse_version
from sphinx.application import Sphinx
from tomli import load as toml_parse

sys.path.insert(0, os.path.abspath(".."))


def setup(sphinx: Sphinx) -> None:
    """Some setup steps for sphinx."""
    sphinx.connect("autoapi-skip-member", skip_data_from_docs)


# -- Project information -----------------------------------------------------


def _get_project_meta() -> Dict[str, str]:
    with open("../pyproject.toml", "rb") as pyproject:
        return toml_parse(pyproject)["tool"]["poetry"]  # type: ignore[no-any-return]


pkg_meta = _get_project_meta()
project = str(pkg_meta["name"])
copyright = str(date.today().year) + ", PerchunPak"
author = "PerchunPak"

parsed_version = parse_version(pkg_meta["version"])

# The short X.Y.Z version
version = parsed_version.base_version
# The full version, including alpha/beta/rc tags
release = str(parsed_version)

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = "4.5"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    # Used to reference for third party projects:
    "sphinx.ext.intersphinx",
    # Used to write beautiful docstrings:
    "sphinx.ext.napoleon",
    # Used to include .md files:
    "m2r2",
    # Used to insert typehints into the final docs:
    "sphinx_autodoc_typehints",
    # Same to `sphinx.ext.autodoc`, but parse source code
    # instead of importing it:
    "autoapi.extension",
]

autoclass_content = "class"
autodoc_member_order = "bysource"

autodoc_default_flags = {
    "members": "",
    "undoc-members": "code,error_template",
    "exclude-members": "__dict__,__weakref__",
}

# Set `typing.TYPE_CHECKING` to `True`:
# https://pypi.org/project/sphinx-autodoc-typehints/
set_type_checking_flag = True

# Automatically generate section labels:
autosectionlabel_prefix_document = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:

source_suffix = [".rst", ".md"]

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "ru"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
# Also, this should ignore AutoAPI template files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "_autoapi_templates/*"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

add_module_names = False

autodoc_default_options = {
    "show-inheritance": True,
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "furo"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "navigation_with_keys": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Extension configuration -------------------------------------------------

napoleon_include_private_with_doc = True

# Configuration for autoapi
autoapi_dirs = ["../pinger_bot"]
autoapi_template_dir = "_autoapi_templates"
autoapi_root = "api"


def get_patched_hikari_inv() -> str:
    """Patching hikari's ``objects.inv`` file, with correct roles.

    Returns:
        Path to patched ``inv`` file.
    """
    inv = sphobjinv.Inventory(url="https://www.hikari-py.dev/objects.inv")
    for object_ in inv.objects:
        if object_.role == "func" or object_.role == "var":
            object_.role = {"func": "function", "var": "variable"}[object_.role]
    makedirs("./_build/doctrees", exist_ok=True)
    sphobjinv.writebytes("./_build/doctrees/hikari_objects.inv", sphobjinv.compress(inv.data_file()))
    return "./_build/doctrees/hikari_objects.inv"


# Third-party projects documentation references:
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "hikari": ("https://www.hikari-py.dev/", get_patched_hikari_inv()),
    "lightbulb": ("https://hikari-lightbulb.readthedocs.io/en/latest/", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
}


def skip_data_from_docs(
    app: Sphinx, what: str, name: str, obj: PythonModule, skip: Optional[bool], options: List[str]
) -> Optional[bool]:
    """Skip ``log`` function everywhere."""
    if what == "data" and name.endswith(".log"):
        skip = True
    return skip


# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
