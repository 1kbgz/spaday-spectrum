import json
from pathlib import Path

from spaday import ComponentPackage

from . import button, checkbox, switch, tabs, textfield, theme
from .button import *
from .checkbox import *
from .switch import *
from .tabs import *
from .textfield import *
from .theme import *

__version__ = "0.1.0"

# the exact version of each JS library the package serves, written by its JS build
_VERSIONS = Path(__file__).parent / "extension" / "versions.json"

package = ComponentPackage(
    name="spectrum",
    assets_dir=Path(__file__).parent / "extension",
    assets=(("js", "cdn/index.js"),),
    components=tuple(getattr(module, name) for module in (button, checkbox, switch, tabs, textfield, theme) for name in module.__all__),
    provides=json.loads(_VERSIONS.read_text(encoding="utf-8")) if _VERSIONS.exists() else {},
)
