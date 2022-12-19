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
import typing as t
from datetime import date

from autoapi.mappers.python.objects import PythonModule
from packaging.version import parse as parse_version
from sphinx.application import Sphinx

try:
    from tomllib import load as toml_parse
except ModuleNotFoundError:  # python <3.11
    from tomli import load as toml_parse

sys.path.insert(0, os.path.abspath(".."))


def setup(sphinx: Sphinx) -> None:
    """Some setup steps for sphinx."""
    sphinx.connect("autoapi-skip-member", skip_data_from_docs)


# -- Project information -----------------------------------------------------


def _get_project_meta() -> t.Dict[str, str]:
    """Get project meta from ``pyproject.toml``."""
    with open("../pyproject.toml", "rb") as pyproject:
        return t.cast(t.Dict[str, str], toml_parse(pyproject)["tool"]["poetry"])


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
needs_sphinx = "5.0"

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
language = os.getenv("DOCS_LANGUAGE", "en")

locale_dirs = ["locale/"]
gettext_compact = False

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

# -- Extension configuration -------------------------------------------------

napoleon_include_private_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_references = True

# Configuration for autoapi
autoapi_dirs = ["../pinger_bot"]
autoapi_template_dir = "_autoapi_templates"
autoapi_root = "api"


# Third-party projects documentation references:
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "hikari": ("https://www.hikari-py.dev/", None),
    "lightbulb": ("https://hikari-lightbulb.readthedocs.io/en/latest/", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
}


def skip_data_from_docs(
    app: Sphinx,
    what: str,
    name: str,
    obj: PythonModule,
    skip: t.Optional[bool],
    options: t.List[str],  # skipcq: PYL-W0613
) -> t.Optional[bool]:
    """Skip ``log`` function and ``_`` attribute everywhere. And skip all if language is not English."""
    if language != "en":
        return True

    if what == "data" and name.endswith(".log"):
        skip = True
    # this is a shortcut for ``gettext`` usually
    if what == "data" and name.endswith("._"):
        skip = True
    return skip


# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
