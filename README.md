# wnp-templates

Shared display templates and utilities for [What's Now Playing](https://whatsnowplaying.github.io/).

This package provides:

* Pre-built HTML/CSS/JS display templates for OBS and other broadcast software
* `template_colors.py` — CSS variable extraction, named template assembly, and timing script injection
* Sample preview images for the template editor
* The Jinja2-based template build toolchain

## Installation

Install directly from a GitHub Release wheel:

```bash
pip install https://github.com/whatsnowplaying/wnp-templates/releases/latest/download/wnp_templates-VERSION-py3-none-any.whl
```

## Usage

```python
import wnp_templates

# Registry of all template families and their effect variants
print(wnp_templates.TEMPLATE_FAMILIES)

# Path to the bundled .htm files
print(wnp_templates.BUNDLED_TEMPLATE_DIR)

# Read CSS variables from a built template
from pathlib import Path
vars = wnp_templates.get_template_variables(Path("ws-basic-text.htm"))

# Assemble a named template with user color overrides and timing
html = wnp_templates.assemble_named_template(
    base_html=Path("ws-basic-text.htm").read_text(),
    css_vars={"wnp-accent-color": "#ff6600"},
    hide_after=30,
)
```

## Template families

| Family | Effects |
|---|---|
| Basic Text | None, Fade, Explode, Spin, Slide, Anime Elastic, Anime Bounce, Anime Stagger |
| Generic DJ | None |
| MTV | None, Fade |
| WebGL | Cube, Hologram, Spectrum, Vinyl, Wave |
| Canvas | Particles |

## Building templates from source

```bash
python -m venv .venv
source .venv/bin/activate
pip install jinja2 pyyaml truststore
python tools/build_templates.py
```

Built `.htm` files are written to `src/wnp_templates/bundled/` and are excluded
from version control — the wheel distributed via GitHub Releases includes them
pre-built.

## License

MIT
