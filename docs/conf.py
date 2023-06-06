# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = "Overhave"
copyright = "2023, TCS group, Inc."
author = "Vladislav Mukhamatnurov <livestreamepidemz@yandex.ru>"

# -- General configuration ---------------------------------------------------
extensions = ["sphinx.ext.todo", "sphinx.ext.viewcode", "sphinx.ext.autodoc"]
templates_path: list[str] = []
exclude_patterns: list[str] = []

# -- Options for HTML output -------------------------------------------------
html_theme = "pyramid"
html_static_path: list[str] = []
pygments_style = "sphinx"
