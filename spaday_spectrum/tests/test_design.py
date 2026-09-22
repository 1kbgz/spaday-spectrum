import json

import pytest
from spaday import Button, Checkbox, TextArea, TextInput, ToggleSwitch, validate
from spaday.ui import conformance, resolve
from spaday.ui.design import _plain

from spaday_spectrum import DESIGN, package


def _props(node: dict) -> dict:
    return {key: _plain(value) for key, value in node.get("props", {}).items()}


def _find(node: dict, tag: str) -> dict:
    if node["tag"] == tag:
        return node
    for children in node.get("slots", {}).values():
        for child in children:
            if isinstance(child, dict):
                try:
                    return _find(child, tag)
                except LookupError:
                    pass
    raise LookupError(tag)


def test_find_walks_all_slots_and_reports_missing_tags():
    tree = {"tag": "root", "slots": {"first": ["text", {"tag": "other"}], "second": [{"tag": "target"}]}}
    assert _find(tree, "target")["tag"] == "target"
    with pytest.raises(LookupError):
        _find(tree, "missing")


def test_the_package_publishes_its_design():
    assert package.design is DESIGN
    assert set(DESIGN.controls) == {"button", "checkbox", "input", "switch", "textarea"}


def test_spectrum_controls_map_the_shared_contract():
    button = resolve(Button(label="Save", intent="primary", appearance="outline", size="lg").to_node(), DESIGN)
    assert button["tag"] == "sp-button"
    assert _props(button) == {"textContent": "Save", "variant": "accent", "treatment": "outline", "size": "l"}

    text = resolve(
        TextInput(label="Name", help="Hint", error="Bad", type="search", size="lg").bind("value", "name", mode="two-way").to_node(),
        DESIGN,
    )
    control = _find(text, "sp-textfield")
    assert _props(control) == {"label": "Name", "invalid": True, "type": "search", "size": "l"}
    assert control["bindings"] == {"value": {"field": "name", "mode": "two-way"}}
    assert _props(text["slots"]["default"][0]) == {"textContent": "Name"}
    assert _props(control["slots"]["help-text"][0]) == {"slot": "help-text", "textContent": "Hint"}
    assert _props(control["slots"]["negative-help-text"][0]) == {"slot": "negative-help-text", "textContent": "Bad"}

    textarea = _find(resolve(TextArea(label="Notes", rows=3, minlength=2, maxlength=20).to_node(), DESIGN), "sp-textfield")
    assert _props(textarea) == {"multiline": True, "label": "Notes", "rows": 3, "minlength": 2, "maxlength": 20}

    checkbox = _find(resolve(Checkbox(label="Agree").bind("value", "agree", mode="two-way").to_node(), DESIGN), "sp-checkbox")
    assert checkbox["bindings"]["checked"] == {"field": "agree", "mode": "two-way"}

    switch = _find(resolve(ToggleSwitch(label="Dark").bind("value", "dark", mode="two-way").to_node(), DESIGN), "sp-switch")
    assert switch["bindings"]["checked"] == {"field": "dark", "mode": "two-way"}


def test_the_conformance_page_uses_native_fallbacks_for_missing_controls():
    node = resolve(conformance.page().to_node(), DESIGN)
    validate(node)
    rendered = json.dumps(node)
    assert '"tag": "ui-' not in rendered
    assert rendered.count("data-ui-fallback") == 8
