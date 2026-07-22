from pathlib import Path

from spaday import ComponentPackage

from .button import *
from .checkbox import *
from .switch import *
from .tabs import *
from .textfield import *
from .theme import *

__version__ = "0.1.0"

package = ComponentPackage(
    name="spectrum",
    assets_dir=Path(__file__).parent / "extension",
    assets=(("js", "cdn/index.js"),),
)
