# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
from typing import List

project = "Overhave"
copyright = "2022, TCS group, Inc."
author = "Vladislav Mukhamatnurov <livestreamepidemz@yandex.ru>"

# -- General configuration ---------------------------------------------------
extensions = ["sphinx.ext.todo", "sphinx.ext.viewcode", "sphinx.ext.autodoc"]
templates_path: List[str] = []
exclude_patterns: List[str] = []

# -- Options for HTML output -------------------------------------------------
html_theme = "pyramid"
html_static_path: List[str] = []
pygments_style = "sphinx"
