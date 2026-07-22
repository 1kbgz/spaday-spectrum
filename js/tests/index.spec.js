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
