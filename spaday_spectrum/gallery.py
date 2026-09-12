"""Gallery of every Spectrum component wrapped by spaday-spectrum."""

from __future__ import annotations

import io
import keyword
import textwrap
import tokenize

from spaday import element
from spaday.backends.starlette import serve

from . import (
    SpButton,
    SpCheckbox,
    SpClearButton,
    SpCloseButton,
    SpSwitch,
    SpTab,
    SpTabPanel,
    SpTabs,
    SpTabsOverflow,
    SpTextfield,
    SpTheme,
    button,
    checkbox,
    package,
    switch,
    tabs,
    textfield,
    theme,
)

COMPONENT_MODULES = (button, checkbox, switch, tabs, textfield, theme)
COMPONENT_NAMES = tuple(name for module in COMPONENT_MODULES for name in module.__all__)
COMPONENT_SNIPPETS: list[str] = []


def _snippet(names: str, body: str) -> str:
    source = f"from spaday_spectrum import {names}\n\n{textwrap.dedent(body).strip()}\n"
    COMPONENT_SNIPPETS.append(source)
    return source


def _offsets(source: str) -> list[int]:
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def _code(source: str):
    """Render dependency-free highlighted Python."""
    offsets = _offsets(source)
    children = []
    cursor = 0
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.ENDMARKER:
            continue
        start = offsets[token.start[0] - 1] + token.start[1]
        end = offsets[token.end[0] - 1] + token.end[1]
        if start > cursor:
            children.append(source[cursor:start])
        token_class = None
        if token.type == tokenize.NAME and keyword.iskeyword(token.string):
            token_class = "keyword"
        elif token.type == tokenize.STRING:
            token_class = "string"
        elif token.type == tokenize.NUMBER:
            token_class = "number"
        elif token.type == tokenize.COMMENT:
            token_class = "comment"
        elif token.type == tokenize.OP:
            token_class = "operator"
        children.append(element("span", class_=f"token-{token_class}").text(token.string) if token_class else token.string)
        cursor = end
    return element("pre", element("code", *children), class_="code-block")


def _demo(title: str, description: str, source: str, preview):
    return element(
        "article",
        element(
            "header",
            element("div", element("h2").text(title), element("p").text(description)),
            element("span", class_="language-pill").text("Python"),
            class_="demo-heading",
        ),
        element("div", preview, class_="preview"),
        _code(source),
        class_="gallery-card",
    )


theme_actions = _demo(
    "Theme and actions",
    "Establish Spectrum color and scale once, then choose button treatment by intent.",
    _snippet(
        "SpButton, SpClearButton, SpCloseButton, SpTheme",
        """
        page = SpTheme(
            SpButton(variant="accent").text("Publish"),
            SpButton(variant="secondary", treatment="outline").text("Save draft"),
            SpClearButton(label="Clear selection"),
            SpCloseButton(label="Dismiss"),
            color="light",
            scale="medium",
            system="spectrum",
        )
        """,
    ),
    element(
        "div",
        SpButton(variant="accent").text("Publish"),
        SpButton(variant="secondary", treatment="outline").text("Save draft"),
        SpClearButton(label="Clear selection"),
        SpCloseButton(label="Dismiss"),
        class_="inline-preview",
    ),
)

fields = _demo(
    "Text fields",
    "Use the same typed element for compact entry, multiline copy, and validation feedback.",
    _snippet(
        "SpTextfield",
        """
        title = SpTextfield(label="Asset title", value="Campaign key visual")
        brief = SpTextfield(label="Brief", multiline=True, rows=3)
        email = SpTextfield(label="Owner email", type="email", invalid=True) \
            .child_in("negative-help-text", "Enter a valid address")
        """,
    ),
    element(
        "div",
        element("label", element("span").text("Asset title"), SpTextfield(label="Asset title", value="Campaign key visual")),
        element("label", element("span").text("Brief"), SpTextfield(label="Brief", multiline=True, rows=3, placeholder="Describe the deliverable")),
        element(
            "label",
            element("span").text("Owner email"),
            SpTextfield(label="Owner email", type="email", value="not-an-email", invalid=True).child_in(
                "negative-help-text", element("span").text("Enter a valid address")
            ),
        ),
        class_="form-preview",
    ),
)

selection = _demo(
    "Selection",
    "Capture independent choices with a checkbox and persistent settings with a switch.",
    _snippet(
        "SpCheckbox, SpSwitch",
        """
        web = SpCheckbox(checked=True, emphasized=True).text("Web")
        social = SpCheckbox().text("Social")
        automatic = SpSwitch(checked=True, emphasized=True).text("Auto-publish approved assets")
        """,
    ),
    element(
        "div",
        SpCheckbox(checked=True, emphasized=True).text("Web"),
        SpCheckbox().text("Social"),
        SpSwitch(checked=True, emphasized=True).text("Auto-publish approved assets"),
        class_="selection-preview",
    ),
)

navigation = _demo(
    "Tabs and panels",
    "Bind one selected value while keeping tabs and their matching panels explicit.",
    _snippet(
        "SpTab, SpTabPanel, SpTabs",
        """
        review = SpTabs(
            SpTab(label="Assets", value="assets"),
            SpTab(label="Activity", value="activity"),
            selected="assets",
            label="Review sections",
        ) \
            .child_in("tab-panel", SpTabPanel("3 assets waiting", value="assets")) \
            .child_in("tab-panel", SpTabPanel("Recent decisions", value="activity"))
        """,
    ),
    SpTabs(
        SpTab(label="Assets", value="assets"),
        SpTab(label="Activity", value="activity"),
        selected="assets",
        label="Review sections",
    )
    .child_in("tab-panel", SpTabPanel(element("p").text("3 assets waiting for review"), value="assets"))
    .child_in("tab-panel", SpTabPanel(element("p").text("Recent decisions appear here"), value="activity")),
)

overflow = _demo(
    "Overflowing tabs",
    "Wrap a dense tab set to retain accessible previous and next controls in narrow containers.",
    _snippet(
        "SpTabsOverflow",
        """
        overflow = SpTabsOverflow(
            SpTabs(
                *(SpTab(label=label, value=label.lower()) for label in labels),
                selected="overview",
                label="Project sections",
            ),
            label_previous="Previous tabs",
            label_next="Next tabs",
        )
        """,
    ),
    element(
        "div",
        SpTabsOverflow(
            SpTabs(
                *(
                    SpTab(label=label, value=label.lower().replace(" ", "-"))
                    for label in ("Overview", "Assets", "Briefs", "Approvals", "Activity", "Archive")
                ),
                selected="overview",
                label="Project sections",
            ),
            label_previous="Previous tabs",
            label_next="Next tabs",
        ),
        class_="overflow-demo",
    ),
)

page = SpTheme(
    element(
        "main",
        element(
            "header",
            element("p", class_="eyebrow").text("SPADAY · SPECTRUM"),
            element("h1").text("Component gallery"),
            element("p", class_="lede").text(
                "The complete focused Spectrum catalog in spaday-spectrum: eleven typed custom elements, composed into practical Python examples."
            ),
            element("div", element("span").text("11 generated elements"), element("span").text("6 Spectrum packages"), class_="hero-meta"),
            class_="hero",
        ),
        element("section", theme_actions, fields, selection, navigation, overflow, class_="gallery-grid"),
        element("footer").text(f"Generated components: {len(COMPONENT_NAMES)} Spectrum elements · Python runs locally in Pyodide"),
        class_="gallery-page",
    ),
    color="light",
    scale="medium",
    system="spectrum",
    id="gallery-theme",
)

styles = """
<style>
  body { margin: 0; }
  sp-theme { display: block; min-height: 100vh; color: var(--spectrum-neutral-content-color-default);
    background: radial-gradient(circle at 12% 0, color-mix(in srgb, var(--spectrum-accent-color-900) 13%, transparent), transparent 32rem),
      var(--spectrum-background-layer-1-color); font-family: var(--spectrum-sans-font-family-stack, system-ui); }
  .gallery-page { box-sizing: border-box; width: min(100%, 88rem); margin: 0 auto; padding: 3rem 1.25rem 4rem; }
  .hero { padding: 1.5rem 0 2.5rem; }
  .eyebrow { margin: 0; color: var(--spectrum-accent-content-color-default); font-size: .72rem; font-weight: 800; letter-spacing: .16em; }
  h1 { margin: .35rem 0 0; font-size: clamp(2.6rem, 6vw, 4.9rem); line-height: .98; letter-spacing: -.055em; }
  .lede { max-width: 50rem; margin: 1rem 0; color: var(--spectrum-neutral-subdued-content-color-default); font-size: 1.08rem; line-height: 1.6; }
  .hero-meta { display: flex; flex-wrap: wrap; gap: .55rem; }
  .hero-meta span { padding: .42rem .7rem; border: 1px solid var(--spectrum-gray-300); border-radius: 999px;
    background: color-mix(in srgb, var(--spectrum-background-layer-2-color) 90%, transparent); font-size: .85rem; }
  .gallery-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 26rem), 1fr)); gap: 1rem; align-items: start; }
  .gallery-card { min-width: 0; padding: 1.15rem; border: 1px solid var(--spectrum-gray-300); border-radius: 12px;
    background: var(--spectrum-background-layer-2-color); box-shadow: 0 18px 50px rgb(0 0 0 / .08); }
  .demo-heading { display: flex; align-items: start; justify-content: space-between; gap: 1rem; margin-bottom: 1rem; }
  .demo-heading > div { min-width: 0; }
  .demo-heading h2 { margin: 0; font-size: 1.1rem; }
  .demo-heading p { margin: .3rem 0 0; color: var(--spectrum-neutral-subdued-content-color-default); font-size: .88rem; line-height: 1.45; }
  .language-pill { flex: 0 0 auto; padding: .25rem .5rem; border-radius: 999px; color: var(--spectrum-accent-content-color-default);
    background: color-mix(in srgb, var(--spectrum-accent-color-900) 12%, transparent); font-size: .72rem; font-weight: 750; }
  .preview { box-sizing: border-box; min-height: 9rem; margin-bottom: 1rem; padding: 1.25rem; overflow: auto;
    border: 1px solid var(--spectrum-gray-300); border-radius: 10px; background: var(--spectrum-background-layer-1-color); }
  .preview > * { max-width: 100%; }
  .inline-preview { display: flex; flex-wrap: wrap; align-items: center; gap: .75rem; }
  .form-preview, .selection-preview { display: grid; gap: 1rem; }
  .form-preview label { display: grid; gap: .35rem; color: var(--spectrum-neutral-subdued-content-color-default); font-size: .85rem; }
  .form-preview sp-textfield { width: 100%; }
  .overflow-demo { width: 17rem; max-width: 100%; }
  .code-block { box-sizing: border-box; max-height: 19rem; margin: 0; padding: 1rem; overflow: auto; border-radius: 10px;
    color: #dbeafe; background: #171a22; font: .78rem/1.6 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    tab-size: 4; white-space: pre; }
  .token-keyword { color: #c4b5fd; } .token-string { color: #86efac; } .token-number { color: #fcd34d; }
  .token-comment { color: #94a3b8; font-style: italic; } .token-operator { color: #7dd3fc; }
  footer { margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid var(--spectrum-gray-300);
    color: var(--spectrum-neutral-subdued-content-color-default); font-size: .85rem; }
  @media (max-width: 600px) { .gallery-page { padding: 2rem .75rem 3rem; } .hero { padding-top: .75rem; }
    .preview { padding: .9rem; } }
</style>
"""

app = serve(page, packages=[package], head=styles, title="spaday-spectrum gallery")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8029)
