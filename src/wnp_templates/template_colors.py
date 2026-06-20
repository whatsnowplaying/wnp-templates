"""CSS variable management and template assembly for What's Now Playing templates.

Reads CSS custom properties (--wnp-* variables) from built templates,
assembles named templates with user CSS var overrides and timing scripts,
and provides the canonical TEMPLATE_FAMILIES registry.
"""

import hashlib
import logging
import pathlib
import re

import yaml

BUNDLED_TEMPLATE_DIR: pathlib.Path = pathlib.Path(__file__).parent / "bundled"

_VENDOR_YAML: pathlib.Path = pathlib.Path(__file__).parent / "vendor.yaml"


def _load_vendor_files() -> dict[str, str]:
    """Return filename → URL map from the packaged vendor.yaml."""
    if not _VENDOR_YAML.exists():
        return {}
    data = yaml.safe_load(_VENDOR_YAML.read_text(encoding="utf-8"))
    return {
        filename: info["url"]
        for filename, info in data.get("vendor_dependencies", {}).items()
    }


VENDOR_FILES: dict[str, str] = _load_vendor_files()

_TIMING_JS_TEMPLATE = """\
<script>(function(){{
var H={hide_after},R={repeat_anim},D={delay_update};
var _ht=null,_rt=null,_cm=null;
function wrap(){{
  var orig=window.updateDisplay;
  if(!orig){{setTimeout(wrap,50);return;}}
  window.updateDisplay=function(m){{
    if(D>0&&m&&m.title){{setTimeout(function(){{apply(m);}},D*1000);}}
    else{{apply(m);}}
  }};
  function apply(m){{
    _cm=m;
    if(_ht){{clearTimeout(_ht);_ht=null;}}
    if(_rt){{clearInterval(_rt);_rt=null;}}
    orig(m);
    if(m&&m.title){{
      if(H>0){{_ht=setTimeout(function(){{orig(null);}},H*1000);}}
      if(R>0){{_rt=setInterval(function(){{orig(null);setTimeout(function(){{orig(_cm);}},500);}},R*1000);}}
    }}
  }}
}}
if(document.readyState==='loading'){{document.addEventListener('DOMContentLoaded',wrap);}}
else{{wrap();}}
}})()</script>"""


def make_timing_script(hide_after: int, repeat_anim: int, delay_update: int) -> str:
    """Return a self-contained timing <script> block, or empty string if all zeros."""
    if hide_after == 0 and repeat_anim == 0 and delay_update == 0:
        return ""
    return _TIMING_JS_TEMPLATE.format(
        hide_after=hide_after, repeat_anim=repeat_anim, delay_update=delay_update
    )


_TIMING_META_RE = re.compile(
    r'<meta\s+name=["\']wnp-timing["\'][^>]*content=["\'](\d+),(\d+),(\d+)["\']',
    re.IGNORECASE,
)

_USER_STYLE_ID = "wnp-user-colors"
_VAR_RE = re.compile(r"--(wnp-[\w-]+)\s*:\s*([^;}{]+?)\s*;")
_USER_BLOCK_RE = re.compile(
    r'<style[^>]+id=["\']' + _USER_STYLE_ID + r'["\'][^>]*>.*?</style>',
    re.DOTALL | re.IGNORECASE,
)
_CSS_KEY_RE = re.compile(r"^wnp-[\w-]+$")

# Family name → ordered dict of effect_label → template_stem
# The first entry in each family is the canonical (no-effect) variant.
TEMPLATE_FAMILIES: dict[str, dict[str, str]] = {
    "Basic Text": {
        "None": "ws-basic-text",
        "Fade": "ws-basic-text-fade",
        "Explode": "ws-basic-text-explode",
        "Spin": "ws-basic-text-spin",
        "Slide": "ws-basic-text-slide",
        "Anime Elastic": "ws-basic-text-anime-elastic",
        "Anime Bounce": "ws-basic-text-anime-bounce",
        "Anime Stagger": "ws-basic-text-anime-stagger",
    },
    "Generic DJ": {
        "None": "ws-generic-dj",
    },
    "MTV": {
        "None": "ws-mtv",
        "Fade": "ws-mtv-fade",
    },
    "WebGL": {
        "Cube": "ws-webgl-cube",
        "Hologram": "ws-webgl-hologram",
        "Spectrum": "ws-webgl-spectrum",
        "Vinyl": "ws-webgl-vinyl",
        "Wave": "ws-webgl-wave",
    },
    "Canvas": {
        "Particles": "ws-canvas-particles",
    },
}

# Family name → short description for documentation and UI
TEMPLATE_FAMILY_DESCRIPTIONS: dict[str, str] = {
    "Basic Text": "Simple text overlay with configurable animation effects.",
    "Generic DJ": "Full DJ layout with cover art, fanart slideshow, and metadata.",
    "MTV": "MTV-style lower-third with cover art and track info.",
    "WebGL": "GPU-accelerated animated backgrounds using WebGL.",
    "Canvas": "Animated backgrounds using Canvas 2D.",
}

# Reverse map: template stem → (family_name, effect_label)
STEM_TO_FAMILY: dict[str, tuple[str, str]] = {
    stem: (family, effect)
    for family, effects in TEMPLATE_FAMILIES.items()
    for effect, stem in effects.items()
}


def get_template_timing_defaults(stem: str) -> dict[str, int]:
    """Return timing defaults embedded in a bundled template, or all zeros if absent."""
    path = BUNDLED_TEMPLATE_DIR / f"{stem}.htm"
    if not path.exists():
        return {"hide_after": 0, "repeat_animation": 0, "delay_update": 0}
    m = _TIMING_META_RE.search(path.read_text(encoding="utf-8"))
    if m:
        return {
            "hide_after": int(m.group(1)),
            "repeat_animation": int(m.group(2)),
            "delay_update": int(m.group(3)),
        }
    return {"hide_after": 0, "repeat_animation": 0, "delay_update": 0}


def get_base_checksum(stem: str) -> str | None:
    """Return the SHA-256 hex digest of the bundled template file, or None if missing."""
    path = BUNDLED_TEMPLATE_DIR / f"{stem}.htm"
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def get_template_variables(template_path: pathlib.Path) -> dict[str, str]:
    """Return all --wnp-* CSS variables defined in *template_path*.

    Only the first occurrence of each variable name is returned (the default
    defined in the stock template's :root block). User overrides in the
    wnp-user-colors block are excluded so callers always get the built-in
    default, not a previously saved value.
    """
    text = template_path.read_text(encoding="utf-8")
    text_no_user = _USER_BLOCK_RE.sub("", text)
    seen: dict[str, str] = {}
    for match in _VAR_RE.finditer(text_no_user):
        seen[match.group(1)] = match.group(2).strip()
    return seen


def get_user_colors(template_path: pathlib.Path) -> dict[str, str]:
    """Return the user-saved color overrides from *template_path*.

    Returns an empty dict if the template has no saved customizations.
    """
    text = template_path.read_text(encoding="utf-8")
    block_match = _USER_BLOCK_RE.search(text)
    if not block_match:
        return {}
    return {
        m.group(1): m.group(2).strip() for m in _VAR_RE.finditer(block_match.group())
    }


def _build_user_style_block(colors: dict[str, str]) -> str:
    lines = ["    :root {"]
    for name, value in colors.items():
        if not _CSS_KEY_RE.match(name):
            raise ValueError(f"Invalid CSS variable name: {name!r}")
        safe_value = value.replace("</", "")
        lines.append(f"        --{name}: {safe_value};")
    lines.append("    }")
    inner = "\n".join(lines)
    return f'<style id="{_USER_STYLE_ID}">\n{inner}\n    </style>'


def assemble_named_template(
    base_html: str,
    css_vars: dict[str, str],
    hide_after: int = 0,
    repeat_animation: int = 0,
    delay_update: int = 0,
) -> str:
    """Assemble a named template from base HTML, CSS var overrides, and timing.

    Strips any existing user style block, injects CSS vars before </head>,
    and injects the timing script before </body>. Returns the assembled HTML.
    """
    html = _USER_BLOCK_RE.sub("", base_html)

    if css_vars:
        style_block = _build_user_style_block(css_vars)
        html = html.replace("</head>", f"    {style_block}\n</head>", 1)

    timing_script = make_timing_script(hide_after, repeat_animation, delay_update)
    if timing_script:
        if "</body>" in html:
            html = html.replace("</body>", timing_script + "</body>", 1)
        else:
            logging.warning("template has no </body>; appending timing script")
            html += timing_script

    return html
