import fs from "fs";
import { expect, test } from "@playwright/test";

const built = fs.existsSync("dist/lite/index.html");

async function renderedComponentTags(page, prefix) {
  return page.locator("body").evaluate((body, prefix) => {
    const components = [...body.querySelectorAll("*")].filter((element) =>
      element.localName.startsWith(prefix),
    );
    const tags = [...new Set(components.map((element) => element.localName))];
    const unrendered = tags.filter(
      (tag) =>
        !components
          .filter((element) => element.localName === tag)
          .some((element) => {
            const bounds = element.getBoundingClientRect();
            return bounds.width > 0 && bounds.height > 0;
          }),
    );
    return { count: tags.length, unrendered };
  }, prefix);
}

async function waitForPython(page) {
  await page.waitForFunction(
    () =>
      document.documentElement.dataset.ready === "true" ||
      document.querySelector("#pyodide-status")?.textContent ===
        "Unable to start",
    undefined,
    { timeout: 150_000 },
  );
  await expect(page.locator("html")).toHaveAttribute("data-ready", "true");
}

function collectErrors(page) {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  return errors;
}

async function expectNoHorizontalOverflow(page) {
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - window.innerWidth,
  );
  expect(overflow).toBeLessThanOrEqual(1);
}

test("runs the complete example in Pyodide", async ({ page }) => {
  test.skip(!built, "run `make pyodide-example` first");
  test.setTimeout(180_000);
  await page.setViewportSize({ width: 320, height: 800 });
  const errors = collectErrors(page);

  await page.goto("/dist/lite/index.html");
  await waitForPython(page);
  await expect(page.locator(".hero h1")).toHaveText("Creative review");

  await page.locator("sp-tab[value=brief]").click();
  await page.locator("#email input").fill("mara@example.com");
  await page.locator("#submit").click();
  await expect(page.locator("#brief-message")).toContainText(
    "Filed Autumn launch",
  );

  await page.locator("sp-tab[value=assets]").click();
  const assets = page.locator(".asset");
  const initial = await assets.count();
  await expect
    .poll(() => assets.count(), { timeout: 10_000 })
    .toBeGreaterThan(initial);
  const waiting = assets.filter({ hasText: "Needs review" }).first();
  const id = await waiting.getAttribute("data-id");
  await waiting.locator("sp-button", { hasText: "Approve" }).click();
  await expect(page.locator(`.asset[data-id="${id}"] .status`)).toHaveText(
    "Approved",
  );
  await expectNoHorizontalOverflow(page);
  expect(errors).toEqual([]);
});

test("runs the complete gallery in Pyodide", async ({ page }) => {
  test.skip(!built, "run `make pyodide-example` first");
  test.setTimeout(180_000);
  await page.setViewportSize({ width: 320, height: 800 });
  const errors = collectErrors(page);

  await page.goto("/dist/lite/?example=gallery");
  await waitForPython(page);
  await expect(page.locator(".hero h1")).toHaveText("Component gallery");
  expect(await page.locator(".gallery-card").count()).toBe(5);
  await expect(page.locator("sp-tabs-overflow")).toBeVisible();
  const rendered = await renderedComponentTags(page, "sp-");
  expect(rendered.count).toBe(11);
  expect(rendered.unrendered).toEqual([]);
  await expect(page.locator(".token-keyword").first()).toHaveText("from");
  await expectNoHorizontalOverflow(page);
  expect(errors).toEqual([]);
});
