import { expect, test } from "@playwright/test";

/* The review board in spaday_spectrum/example.py, run as its own server. */

const PAGE = "http://127.0.0.1:8028";

test("streams assets from Python and reviews them", async ({ page }) => {
  await page.goto(PAGE);
  const assets = page.locator(".asset");
  await expect(assets.first()).toBeVisible();
  const ids = () =>
    assets.evaluateAll((rows) => rows.map((row) => row.dataset.id));
  const initial = await ids();
  // an asset arrives every few seconds
  await expect
    .poll(async () => (await ids()).some((id) => !initial.includes(id)), {
      timeout: 10_000,
    })
    .toBe(true);
  const id = await assets.evaluateAll(
    (rows) =>
      rows.find(
        (row) => row.querySelector(".status").textContent === "Needs review",
      )?.dataset.id,
  );
  const row = page.locator(`.asset[data-id="${id}"]`);
  await row.locator("sp-button", { hasText: "Approve" }).click();
  await expect(row.locator(".status")).toHaveText("Approved");
  await expect(page.locator("#decision")).toContainText("Approved:");
});

test("files a brief, flagging the email until it is valid", async ({
  page,
}) => {
  await page.goto(PAGE);
  await page.locator("sp-tab[value=brief]").click();
  await page.locator("#submit").click();
  await expect(page.locator("#email")).toHaveJSProperty("invalid", true);
  await page.locator("#email input").fill("mara@example.com");
  await page.locator("#channel-print").click();
  await page.locator("#submit").click();
  await expect(page.locator("#brief-message")).toHaveText(
    "Filed Autumn launch for mara@example.com: web, social, print, held for scheduling.",
  );
  await expect(page.locator("#email")).toHaveJSProperty("invalid", false);
  // the button's own action switches the tabs through the store
  await page.locator("sp-button", { hasText: "Review assets" }).click();
  await expect(page.locator("#tabs")).toHaveJSProperty("selected", "assets");
});

test("the close button dismisses the banner", async ({ page }) => {
  await page.goto(PAGE);
  await expect(page.locator(".callout").first()).toBeVisible();
  await page.locator("#dismiss-banner").click();
  await expect(page.locator("#dismiss-banner")).toHaveCount(0);
});

test("switches drive Spectrum's color and scale, and the shell follows", async ({
  page,
}) => {
  await page.goto(PAGE);
  const theme = page.locator("#theme");
  const nav = () =>
    page
      .locator("spa-nav")
      .evaluate((el) => getComputedStyle(el).backgroundColor);
  const light = await nav();
  await page.locator("#dark").click();
  await expect(theme).toHaveJSProperty("color", "dark");
  await expect.poll(nav).not.toBe(light);
  await page.locator("#large").click();
  await expect(theme).toHaveJSProperty("scale", "large");
});
