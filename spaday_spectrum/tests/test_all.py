import ast
import re
from pathlib import Path

import pytest
from spaday import generate
from spaday.bootstrap import bootstrap

from spaday_spectrum import SpButton, SpCheckbox, SpSwitch, SpTab, SpTabPanel, SpTabs, SpTextfield, SpTheme, package

ROOT = Path(__file__).parent.parent
CATALOG = ("button", "checkbox", "switch", "tabs", "textfield", "theme")


def test_representative_spectrum_components_serialize():
    page = SpTheme(color="light", scale="medium").child(
        SpButton(treatment="fill").text("Save"),
        SpTextfield(value="hello"),
        SpCheckbox(checked=True).text("Enabled"),
        SpTabs(selected="one").child(SpTab(value="one").text("One"), SpTabPanel(value="one").text("Panel")),
    )
    node = page.to_node()
    assert node["tag"] == "sp-theme"
    assert [child["tag"] for child in node["slots"]["default"]] == ["sp-button", "sp-textfield", "sp-checkbox", "sp-tabs"]


def test_package_drives_bootstrap_asset_url():
    assert package.name == "spectrum"
    assert 'src="/components/spectrum/cdn/index.js"' in bootstrap(packages=[package])


def test_catalog_declares_every_element_the_bundle_registers():
    entry = (ROOT.parent / "js" / "src" / "ts" / "index.ts").read_text(encoding="utf-8")
    registered = set(re.findall(r"/(sp-[\w-]+)\.js", entry))
    assert {schema.tag for schema in package.catalog} == registered


def test_catalog_carries_what_other_spectrum_packages_contribute():
    """Spectrum's per-package manifests leave out inherited attributes declared in another package."""
    props = {schema.tag: {prop.name for prop in schema.props} for schema in package.catalog}
    assert {"checked", "disabled", "size"} <= props["sp-switch"]  # CheckboxBase, Focusable, SizedMixin
    assert {"disabled", "href", "label", "size"} <= props["sp-button"]  # Focusable, LikeAnchor, SizedMixin
    assert SpSwitch(checked=True).to_node()["props"]["checked"] == {"Bool": True}


@pytest.mark.parametrize("name", CATALOG)
def test_generated_catalog_is_current(name):
    fresh = generate(str(ROOT / "manifests" / f"{name}.json"), source=f"@spectrum-web-components/{name}")
    assert ast.dump(ast.parse(fresh)) == ast.dump(ast.parse((ROOT / f"{name}.py").read_text(encoding="utf-8")))
