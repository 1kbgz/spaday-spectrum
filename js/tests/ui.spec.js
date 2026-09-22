import { expect, test } from "@playwright/test";

const PAGE = "http://127.0.0.1:8030";

test("renders Spectrum controls and explicit native fallbacks", async ({
  page,
}) => {
  await page.goto(PAGE);
  await page.locator("#dialog").waitFor({ state: "attached" });
  expect(
    await page.evaluate(() =>
      ["save", "name", "notes", "agree", "dark"].map(
        (id) => document.getElementById(id).localName,
      ),
    ),
  ).toEqual([
    "sp-button",
    "sp-textfield",
    "sp-textfield",
    "sp-checkbox",
    "sp-switch",
  ]);
  await expect(page.locator("[data-ui-fallback]")).toHaveCount(8);
});

test("Spectrum values round-trip through the shared store", async ({
  page,
}) => {
  await page.goto(PAGE);
  const state = page.locator("#state");
  await page.locator("#name").evaluate((element) => {
    element.value = "Ada";
    element.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await page.locator("#notes").evaluate((element) => {
    element.value = "Ready";
    element.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await page.locator("#agree").click();
  await page.locator("#dark").click();
  await expect(state).toHaveText(
    "Ada|Ready|2|2026-09-14|true|true|basic|1|5|25|false|false",
  );
  await page.locator("#save").click();
  await expect(state).toContainText("|true|false");
});

test("labels, errors, and disabled state render", async ({ page }) => {
  await page.goto(PAGE);
  await expect(page.getByText("Your name")).toBeVisible();
  await expect(page.getByText("Required")).toBeVisible();
  await expect(page.locator("#email")).toHaveJSProperty("invalid", true);
  await expect(page.locator("#never")).toHaveJSProperty("disabled", true);
  await expect(page.locator("#save")).toHaveText("Save");
  await expect(page.locator("#save")).toHaveAttribute("variant", "accent");
});
