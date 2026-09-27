import json
from pathlib import Path

from spaday import ComponentPackage, Token

from . import button, checkbox, switch, tabs, textfield, theme
from .button import *
from .checkbox import *
from .design import DESIGN
from .switch import *
from .tabs import *
from .textfield import *
from .theme import *

__version__ = "0.4.0"

# the exact version of each JS library the package serves, written by its JS build
_VERSIONS = Path(__file__).parent / "extension" / "versions.json"

package = ComponentPackage(
    name="spectrum",
    assets_dir=Path(__file__).parent / "extension",
    assets=(("css", "css/index.css"), ("js", "cdn/index.js")),
    components=tuple(getattr(module, name) for module in (button, checkbox, switch, tabs, textfield, theme) for name in module.__all__),
    provides=json.loads(_VERSIONS.read_text(encoding="utf-8")) if _VERSIONS.exists() else {},
    design=DESIGN,
)

TOKENS = {
    "spectrum_background_layer_2_color": Token("--spectrum-background-layer-2-color", "drives --spa-surface"),
    "spectrum_background_layer_1_color": Token("--spectrum-background-layer-1-color", "drives --spa-surface-2"),
    "spectrum_gray_300": Token("--spectrum-gray-300", "drives --spa-border"),
    "spectrum_neutral_content_color_default": Token("--spectrum-neutral-content-color-default", "drives --spa-text"),
    "spectrum_neutral_subdued_content_color_default": Token("--spectrum-neutral-subdued-content-color-default", "drives --spa-muted"),
    "spectrum_accent_content_color_default": Token("--spectrum-accent-content-color-default", "drives --spa-accent and --spa-info"),
    "spectrum_positive_visual_color": Token("--spectrum-positive-visual-color", "drives --spa-success"),
    "spectrum_notice_visual_color": Token("--spectrum-notice-visual-color", "drives --spa-warning"),
    "spectrum_negative_visual_color": Token("--spectrum-negative-visual-color", "drives --spa-danger"),
}

__all__ = [  # noqa: PLE0604
    *(name for module in (button, checkbox, switch, tabs, textfield, theme) for name in module.__all__),
    "DESIGN",
    "TOKENS",
    "package",
]
