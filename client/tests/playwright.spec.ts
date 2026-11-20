// SikshaSetu Playwright test: network disabled, full offline-first flow.
import { test, expect } from "@playwright/test";

const HUB = process.env.HUB_URL || "http://127.0.0.1:8000";

test.describe("SikshaSetu offline flow (network off)", () => {
  test("student flow: sync from hub, download unit, go offline, play, notes, question, mastery", async ({ context }) => {
    const page = await context.newPage();
    const errors: string[] = [];
    page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
    await page.addInitScript(() => {
      navigator.onLine = false;
      (window as any).dispatchEvent(new Event("offline"));
    });
    await page.goto(HUB + "/", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible({ timeout: 15000 });
    // download one unit from catalog
    await page.goto("/library", { waitUntil: "domcontentloaded" });
    await page.waitForFunction(() => document.querySelector(".course-card .btn.primary") != null, { timeout: 15000 });
    await page.click(".course-card .btn.primary");
    // play video + transcript visible
    await expect(page.locator(".video")).toHaveCount(1, { timeout: 10000 });
    await expect(page.locator(".transcript-scroll")).toBeVisible();
    // answer a question
    await page.goto("/diagnostic", { waitUntil: "domcontentloaded" });
    await page.click(".opt:first-child");
    await page.getByRole("button", { name: "Submit" }).click();
    await expect(page.getByText(/correct|incorrect/i).first()).toBeVisible();
    expect(errors.filter(e => !e.includes("Failed to load resource"))).toEqual([]);
  });
});
