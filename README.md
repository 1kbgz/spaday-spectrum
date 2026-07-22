# spaday-spectrum

[Spectrum](https://opensource.adobe.com/spectrum-web-components/) for [spaday](https://1kbgz.github.io/spaday/)

[![Build Status](https://github.com/1kbgz/spaday-spectrum/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/1kbgz/spaday-spectrum/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/1kbgz/spaday-spectrum/branch/main/graph/badge.svg)](https://codecov.io/gh/1kbgz/spaday-spectrum)
[![License](https://img.shields.io/github/license/1kbgz/spaday-spectrum)](https://github.com/1kbgz/spaday-spectrum)
[![PyPI](https://img.shields.io/pypi/v/spaday-spectrum.svg)](https://pypi.python.org/pypi/spaday-spectrum)

## Overview

`spaday-spectrum` provides generated Python bindings and a self-contained registration bundle for a
focused first slice of Adobe Spectrum Web Components:

- Theme
- Button, clear button, and close button
- Textfield
- Checkbox and switch
- Tabs, tab panels, and tabs overflow

## Interactive example

The textfield updates the greeting immediately, the checkbox switches Spectrum themes, and the button
resets state. All three interactions run in the browser through spaday's reactive store.

```python
from spaday import SetField, cond, element, field
from spaday.backends.starlette import serve
from spaday_spectrum import SpButton, SpCheckbox, SpTextfield, SpTheme

page = (
    SpTheme(scale="medium")
    .compute("color", cond(field("dark"), "dark", "light"))
    .style(display="block", max_width="32rem", margin="2rem auto", padding="1.5rem")
    .child(element("h1").text("Spectrum profile"))
    .child(SpTextfield(label="Display name", placeholder="Your name").bind("value", "name", mode="two-way"))
    .child(SpCheckbox().text("Dark theme").bind("checked", "dark", mode="two-way"))
    .child(
        element("p")
        .child("Hello, ")
        .child(element("strong").bind("textContent", "name"))
    )
    .child(SpButton(treatment="fill").text("Reset name").on("click", SetField("name", "Ada")))
)

app = serve(page, packages=["spectrum"], store={"name": "Ada", "dark": False})
```

Save this as `app.py`, then run `pip install spaday-spectrum starlette uvicorn` and
`uvicorn app:app`. Open <http://127.0.0.1:8000>.

Installing this project registers the `spectrum` entry point with spaday. The equivalent explicit
forms are `packages=[spaday_spectrum.package]` and `packages=["spaday_spectrum:package"]`.

The first release pins the six individual Spectrum packages to `1.11.2`. It deliberately avoids the
full `@spectrum-web-components/bundle`; more components should be added from concrete application needs
and generated from their published Custom Elements Manifests.

> [!NOTE]
> This library was generated using [copier](https://copier.readthedocs.io/en/stable/) from the [Base Python Project Template repository](https://github.com/python-project-templates/base).
