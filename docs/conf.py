"""Configuration file for the Sphinx documentation builder."""

#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import importlib.metadata as metadata
import os
import re
import sys

import toml

# Add directory with local extensions to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "extensions"))

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# Read pyproject.toml
pyproject = toml.load(os.path.join(PROJECT_ROOT, "pyproject.toml"))["tool"][
    "poetry"
]

project = pyproject["name"]
copyright = "2023, ZHAW Institute of Embedded Systems"
author = pyproject["authors"][0]
release = metadata.version("cocotb-wrapper")
version = re.sub(r"(\d+\.\d+)(?:\.\d+|)(.*)", r"\1\2", release)
version = re.sub(r"(\.dev\d+).*?$", r"\1", version)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.graphviz",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinxcontrib.katex",
    "sphinxcontrib.makedomain",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_togglebutton",
]

# Show typehints in the description rather than the signature
autodoc_typehints = "description"
# Use short typehints
autodoc_typehints_format = "short"

# Autosectionlabel throws warnings if section names are duplicated. The
# following tells autosectionlabel to not throw a warning for duplicated section
# names that are in different documents.
autosectionlabel_prefix_document = True

# Autosectionlabel throws warnings if section names are duplicated. The
# following tells autosectionlabel to not throw a warning for duplicated section
# names if they are deeper than three levels
autosectionlabel_maxdepth = 2

# Ignore functions/classes for the coverage
coverage_ignore_functions = ["main", "run"]

# Add requirements for the doctest
doctest_global_setup = """
import cocotb_wrapper
"""

# Add links to other sphinx documentations
intersphinx_mapping = {
    "cocotb": ("https://docs.cocotb.org/en/stable", None),
    "python": ("https://docs.python.org/3", None),
}

# Enable katex prerenderer
katex_prerender = True

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# Enable restructuredtext and markdown files
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Add any paths that contain templates
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "collapse_navigation": True,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.zhaw.ch/deaa/cocotb-wrapper",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
        {
            "name": "ZHAW InES HPMM Blog",
            "url": "https://blog.zhaw.ch/high-performance/",
            "icon": "_static/zhaw_logo_only.svg",
            "type": "local",
        },
    ],
    "icon_links_label": "Quick Links",
    "navbar_start": ["navbar-logo"],  # "version-switcher"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": [
        "theme-switcher",
        "navbar-icon-links",
    ],
    "navbar_persistent": [],
    # "switcher": {
    #     "version_match": "dev" if ".dev" in version else f"{version}",
    #     "json_url":
    #     "",
    # },
}
html_title = f"{pyproject['name']} v{version} Manual"
html_context = {
    "default_mode": "auto",
}
html_sidebars = {
    "**": ["search-field", "sidebar-nav-bs", "sidebar-ethical-ads"]
}
html_logo = "_static/zhaw_logo_only.svg"
html_css_files = ["css/custom.css"]
html_static_path = ["_static"]

htmlhelp_basename = "iaia"
# -- Options for Latex output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output

latex_engine = "lualatex"
latex_elements = {
    "fontpkg": r"""
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}
""",
    "preamble": r"""
\usepackage[titles]{tocloft}
\cftsetpnumwidth {1.25cm}\cftsetrmarg{1.5cm}
\setlength{\cftchapnumwidth}{0.75cm}
\setlength{\cftsecindent}{\cftchapnumwidth}
\setlength{\cftsecnumwidth}{1.25cm}
""",
    "fncychap": r"\usepackage[Bjornstrup]{fncychap}",
    "printindex": r"\footnotesize\raggedright\printindex",
}
latex_show_urls = "footnote"
