/**
 * Captures the four "deployed application" screenshots (Tasks 25-28).
 *
 *   node tools/shoot-deployed.mjs http://127.0.0.1:8002
 *   node tools/shoot-deployed.mjs https://cars-dealership.xxxx.codeengine.appdomain.cloud
 *
 * Point it at the running deployment - the address bar in each screenshot shows
 * the URL you pass, so the same script works for the local production-mode
 * server and for IBM Cloud Code Engine.
 */
import { execFileSync } from "node:child_process";
import { statSync } from "node:fs";
import { chromium } from "playwright-core";

const ROOT = "D:\\guestbook-final-project\\cars-dealership";
const SHOTS = `${ROOT}\\screenshots`;
const BASE = process.argv[2];
if (!BASE) {
  console.error("usage: node tools/shoot-deployed.mjs <base-url>");
  process.exit(1);
}

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function capture(name) {
  const out = `${SHOTS}\\${name}.png`;
  const marker = `shotmarker-${name}`;
  const result = execFileSync(
    "powershell",
    [
      "-NoProfile",
      "-ExecutionPolicy",
      "Bypass",
      "-File",
      `${ROOT}\\tools\\capture.ps1`,
      "-Out",
      out,
      "-ExpectTitle",
      marker,
    ],
    { encoding: "utf8" }
  ).trim();

  const match =
    /(\d+)x(\d+) uniqueColors=(\d+) mode=(\w+) front=(\w+) title='(.*)'/.exec(
      result
    );
  const colors = match ? Number(match[3]) : 0;
  const bytes = statSync(out).size;
  console.log(
    `${name}.png  ${match ? `${match[1]}x${match[2]}` : "?"}  ` +
      `${Math.round(bytes / 1024)}KB  colors=${colors}`
  );
  if (bytes < 20000 || colors < 40) {
    throw new Error(`Capture for ${name} looks blank.`);
  }
}

function verify(name, pageFile) {
  const verdict = execFileSync(
    "powershell",
    [
      "-NoProfile",
      "-ExecutionPolicy",
      "Bypass",
      "-File",
      `${ROOT}\\tools\\verify-shot.ps1`,
      "-WindowPath",
      `${SHOTS}\\${name}.png`,
      "-PagePath",
      pageFile,
    ],
    { encoding: "utf8" }
  ).trim();
  const summary = verdict
    .split(/\r?\n/)
    .find((line) => line.startsWith("bestOffset"));
  console.log(`   verify: ${summary}`);
  if (!verdict.includes("VERDICT: window capture contains the page")) {
    throw new Error(`Window capture for ${name} is not showing this page.`);
  }
}

async function shot(page, name, scrollY = 0) {
  await page.evaluate(async () => {
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise((resolve) => setTimeout(resolve, 400));
    window.scrollTo(0, 0);
    await Promise.all(
      [...document.images].map((img) =>
        img.complete
          ? Promise.resolve()
          : new Promise((resolve) => {
              img.addEventListener("load", resolve, { once: true });
              img.addEventListener("error", resolve, { once: true });
            })
      )
    );
  });
  await page.evaluate((y) => window.scrollTo(0, y), scrollY);
  await wait(700);
  await page.evaluate(
    (marker) => (document.title = `Cars Dealership ${marker}`),
    `shotmarker-${name}`
  );
  await wait(400);

  const pageFile = `${SHOTS}\\tmp\\${name}-page.png`;
  await page.screenshot({ path: pageFile });
  capture(name);
  verify(name, pageFile);
}

const browser = await chromium.launch({
  channel: "chrome",
  headless: false,
  args: [
    "--window-position=0,0",
    "--window-size=1280,720",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-session-crashed-bubble",
    "--hide-crash-restore-bubble",
    "--force-device-scale-factor=1",
  ],
});

try {
  const context = await browser.newContext({ viewport: null });
  const page = await context.newPage();

  // Task 25 - landing page of the deployed app.
  await page.goto(`${BASE}/`, { waitUntil: "load" });
  await page.locator(".dealer-card").first().waitFor();
  await shot(page, "deployed_landingpage", 0);

  // Task 26 - logged in as root; the header shows the username.
  await page.goto(`${BASE}/login`, { waitUntil: "load" });
  await page.fill("#login-username", "root");
  await page.fill("#login-password", "root123");
  await page.click('button[type="submit"]');
  await page.locator(".user-chip").waitFor();
  await page.goto(`${BASE}/`, { waitUntil: "load" });
  await page.getByRole("link", { name: "Review Dealer" }).first().waitFor();
  await shot(page, "deployed_loggedin", 58);

  // Task 27 - dealer details page.
  await page.goto(`${BASE}/dealer/1`, { waitUntil: "load" });
  await page.locator(".review-card").first().waitFor();
  await shot(page, "deployed_dealer_detail", 70);

  // Task 28 - submit a review and show it on the dealer page.
  await page.goto(`${BASE}/postreview/1`, { waitUntil: "load" });
  await page.locator("#review").waitFor();
  await page.locator('input[type="checkbox"]').check();
  await page.fill("#purchase_date", "2026-10-22");
  await page.selectOption("#car_make", "Toyota");
  await page.selectOption("#car_model", "Camry");
  await page.fill("#car_year", "2024");
  await page.fill(
    "#review",
    "Fantastic services - the Kansas City team had me in a new Camry the " +
      "same afternoon and the price matched the quote exactly."
  );
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/dealer\/1/);
  await page
    .getByText("Fantastic services -", { exact: false })
    .first()
    .waitFor();
  await page.evaluate(() =>
    document.querySelector(".review-card")?.scrollIntoView({ block: "center" })
  );
  await wait(800);
  await shot(page, "deployed_add_review", 0);

  await context.close();
} finally {
  await browser.close();
}

console.log("deployed flow complete");
