"""How Spectrum renders spaday's generic controls (:mod:`spaday.ui`)."""

from spaday.ui import ControlSpec, Design, Part, Value, Wrap

_SIZES = {"sm": "s", "md": "m", "lg": "l"}
_BUTTON_INTENTS = {
    "neutral": "secondary",
    "primary": "accent",
    "info": "accent",
    "success": "primary",
    "warning": "secondary",
    "danger": "negative",
}
_FIELD = {"disabled": "disabled", "required": "required", "readonly": "readonly", "name": "name", "size": "size"}
_WRAP = Wrap(tag="label", props={"class": "ui-field"})
_LABEL = (Part(kind="attr", name="label"), Part(kind="sibling", tag="span"))
_HELP = Part(kind="slot", name="help-text", tag="span")
_ERROR = Part(kind="slot", name="negative-help-text", tag="span")
_TOGGLE_WRAP = Wrap(tag="div", props={"class": "ui-field"})
_TOGGLE_HELP = Part(kind="sibling", tag="small")
_TOGGLE_ERROR = Part(kind="sibling", tag="small", props={"role": "alert"}, after=True)

DESIGN = Design(
    name="spectrum",
    controls={
        "button": ControlSpec(
            tag="sp-button",
            label=Part(kind="text"),
            props={"intent": "variant", "appearance": "treatment", "size": "size", "disabled": "disabled", "name": None},
            values={
                "intent": _BUTTON_INTENTS,
                "appearance": {"filled": "fill", "outline": "outline", "plain": "outline"},
                "size": _SIZES,
            },
        ),
        "input": ControlSpec(
            tag="sp-textfield",
            wrap=_WRAP,
            label=_LABEL,
            help=_HELP,
            error=_ERROR,
            invalid={"invalid": True},
            props={**_FIELD, "placeholder": "placeholder", "type": "type"},
            values={"size": _SIZES},
        ),
        "textarea": ControlSpec(
            tag="sp-textfield",
            fixed={"multiline": True},
            wrap=_WRAP,
            label=_LABEL,
            help=_HELP,
            error=_ERROR,
            invalid={"invalid": True},
            props={**_FIELD, "placeholder": "placeholder", "rows": "rows", "minlength": "minlength", "maxlength": "maxlength"},
            values={"size": _SIZES},
        ),
        "checkbox": ControlSpec(
            tag="sp-checkbox",
            wrap=_TOGGLE_WRAP,
            label=Part(kind="text"),
            help=_TOGGLE_HELP,
            error=_TOGGLE_ERROR,
            invalid={"invalid": True},
            props={"disabled": "disabled", "required": None, "name": "name", "size": "size"},
            values={"size": _SIZES},
            value=Value(prop="checked"),
        ),
        "switch": ControlSpec(
            tag="sp-switch",
            wrap=_TOGGLE_WRAP,
            label=Part(kind="text"),
            help=_TOGGLE_HELP,
            error=_TOGGLE_ERROR,
            invalid={"aria-invalid": "true"},
            props={"disabled": "disabled", "required": None, "name": "name", "size": "size"},
            values={"size": _SIZES},
            value=Value(prop="checked"),
        ),
    },
)

__all__ = ["DESIGN"]
