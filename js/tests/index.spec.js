import { expect, test } from "@playwright/test";

test("registers the first Spectrum component slice with a theme", async ({
  page,
}) => {
  await page.goto("/dist/index.html");
  await page.evaluate(() => {
    document.body.innerHTML = `
      <sp-theme color="light" scale="medium">
        <sp-button>Save</sp-button>
        <sp-textfield value="hello"></sp-textfield>
        <sp-checkbox>Enabled</sp-checkbox>
        <sp-switch>Live</sp-switch>
      </sp-theme>`;
  });

  await expect(page.locator("sp-button")).toHaveText("Save");
  await expect(page.locator("sp-textfield")).toHaveJSProperty("value", "hello");
  await expect(page.locator("sp-theme")).toHaveJSProperty("color", "light");
});

test("warns, naming what it serves, when another copy registered its elements first", async ({
  page,
}) => {
  // the page keeps the first registration, so the loser says which elements are not its own
  const warnings = [];
  page.on("console", (message) => {
    if (message.type() === "warning") warnings.push(message.text());
  });
  await page.addInitScript(() => {
    customElements.define("sp-button", class extends HTMLElement {});
  });
  await page.goto("/dist/index.html");
  await expect
    .poll(() => warnings.find((text) => text.includes("<sp-button>")))
    .toMatch(/ \d+\.\d+\.\d+\S*: another copy on the page already registered /);
  expect(warnings.find((text) => text.includes("<sp-button>"))).toContain(
    "@spectrum-web-components ",
  );
});
