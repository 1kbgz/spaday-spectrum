# spaday-spectrum

[Spectrum](https://opensource.adobe.com/spectrum-web-components/) for [spaday](https://1kbgz.github.io/spaday/)

[![Build Status](https://github.com/1kbgz/spaday-spectrum/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/1kbgz/spaday-spectrum/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/1kbgz/spaday-spectrum/branch/main/graph/badge.svg)](https://codecov.io/gh/1kbgz/spaday-spectrum)
[![License](https://img.shields.io/github/license/1kbgz/spaday-spectrum)](https://github.com/1kbgz/spaday-spectrum)
[![PyPI](https://img.shields.io/pypi/v/spaday-spectrum.svg)](https://pypi.python.org/pypi/spaday-spectrum)

## Overview

> [!NOTE]
> This library was generated using [copier](https://copier.readthedocs.io/en/stable/) from the [Base Python Project Template repository](https://github.com/python-project-templates/base).

`spaday-spectrum` provides generated Python bindings and a self-contained registration bundle for a
focused first slice of Adobe Spectrum Web Components:

- Theme
- Button, clear button, and close button
- Textfield
- Checkbox and switch
- Tabs, tab panels, and tabs overflow

```python
from spaday.backends.starlette import serve
from spaday_spectrum import SpButton, SpTextfield, SpTheme

page = SpTheme(color="light", scale="medium").child(
    SpTextfield(value="hello"),
    SpButton(treatment="fill").text("Save"),
)

app = serve(page, packages=["spectrum"])
```

Installing this project registers the `spectrum` entry point with spaday. The equivalent explicit
forms are `packages=[spaday_spectrum.package]` and `packages=["spaday_spectrum:package"]`.

The first release pins the six individual Spectrum packages to `1.11.2`. It deliberately avoids the
full `@spectrum-web-components/bundle`; more components should be added from concrete application needs
and generated from their published Custom Elements Manifests.
