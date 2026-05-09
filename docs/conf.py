# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

project = "NLM Cell Knowledge Network (NLM-CKN)"
copyright = "2026, NLM-CKN"
author = "NLM-CKN"

extensions = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"

html_static_path = ["_static"]
html_logo = "_static/nlm-ckn-logo-light-sm.png"

html_static_path = ["_static"]

html_theme_options = {
    "navigation_depth": 3,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "titles_only": False,
}

# Include custom CSS and JS
html_css_files = [
    "css/custom.css",
]
html_js_files = [
    "js/reference_form.js",
]

# Allow raw HTML in RST files
html_extra_path = []
