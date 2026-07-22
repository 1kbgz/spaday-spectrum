from spaday.bootstrap import bootstrap

from spaday_spectrum import SpButton, SpCheckbox, SpTab, SpTabPanel, SpTabs, SpTextfield, SpTheme, package


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
