"""wnp-templates: shared template source and utilities for What's Now Playing."""

from wnp_templates.template_colors import (
    BUNDLED_TEMPLATE_DIR,
    STEM_TO_FAMILY,
    TEMPLATE_FAMILIES,
    TEMPLATE_FAMILY_DESCRIPTIONS,
    VENDOR_FILES,
    assemble_named_template,
    get_base_checksum,
    get_template_timing_defaults,
    get_template_variables,
    get_user_colors,
    make_timing_script,
)

__all__ = [
    "BUNDLED_TEMPLATE_DIR",
    "STEM_TO_FAMILY",
    "TEMPLATE_FAMILIES",
    "TEMPLATE_FAMILY_DESCRIPTIONS",
    "VENDOR_FILES",
    "assemble_named_template",
    "get_base_checksum",
    "get_template_timing_defaults",
    "get_template_variables",
    "get_user_colors",
    "make_timing_script",
]
