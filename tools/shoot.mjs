/**
 * Drives real Chrome through the graded screens and captures the whole browser
 * window (address bar included) as a PNG.
 *
 *   node tools/shoot.mjs admin        # Tasks 12-13
 *   node tools/shoot.mjs app          # Tasks 17-22
 *
 * Each run launches its own browser. Before every capture the page title gets a
 * unique marker so the capture helper grabs exactly this window, even if other
 * Chrome windows are open.
 */
import { execFileSync } from "node:child_process";
import { statSync } from "node:fs";
import { chromium } from "playwright-core";

const ROOT = "D:\\guestbook-final-project\\cars-dealership";
const SHOTS = `${ROOT}\\screenshots`;
const BASE = process.env.SHOOT_BASE || "http://localhost:8000";
const FLOW = process.argv[2] || "app";

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
  const mode = match ? match[4] : "?";
  const title = match ? match[6] : "";
  const dims = match ? `${match[1]}x${match[2]}` : "?";
  const bytes = statSync(out).size;

  console.log(
    `${name}.png  ${dims}  ${Math.round(bytes / 1024)}KB  colors=${colors}  ${mode}  window="${title}"`
  );
  if (bytes < 20000 || colors < 40) {
    throw new Error(
      `Capture for ${name} looks wrong (${bytes} bytes, colors=${colors}, mode=${mode}).`
    );
  }
  return out;
}

/**
 * Prove the window capture really shows this page (rather than another Chrome
 * window): grab the page separately and check it lines up below the address bar.
 */
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
  const summary = verdict.split(/\r?\n/).find((line) => line.startsWith("bestOffset"));
  console.log(`   verify: ${summary}`);
  if (!verdict.includes("VERDICT: window capture contains the page")) {
    throw new Error(`Window capture for ${name} is not showing this page.\n${verdict}`);
  }
}

/** Tag the document title so the capture helper can find this exact window. */
async function tag(page, name) {
  await page.evaluate(
    (marker) => (document.title = `Cars Dealership ${marker}`),
    `shotmarker-${name}`
  );
  await wait(500);
}

/** Force lazy images to load, then park the page at the requested offset. */
async function prepare(page, scrollY = 0) {
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
}

async function shot(page, name, scrollY = 0) {
  await prepare(page, scrollY);
  await tag(page, name);
  const pageFile = `${SHOTS}\\tmp\\${name}-page.png`;
  await page.screenshot({ path: pageFile });
  capture(name);
  verify(name, pageFile);
}

async function startBrowser() {
  return chromium.launch({
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
}

async function runAdmin() {
  const browser = await startBrowser();
  try {
    const context = await browser.newContext({ viewport: null });
    const page = await context.newPage();

    // Task 12 - root logged in to the Django admin.
    await page.goto(`${BASE}/admin/`, { waitUntil: "load" });
    await page.fill("#id_username", "root");
    await page.fill("#id_password", "root123");
    await Promise.all([
      page.waitForLoadState("load"),
      page.click('input[type="submit"]'),
    ]);
    await page.waitForFunction(() =>
      document.body.innerText.toLowerCase().includes("welcome, root")
    );
    await shot(page, "admin_login");

    // Task 13 - root logged out again. Django's admin logout lands on the site
    // home page, so revisit /admin/ to show the logged-out login form.
    const logout = page.getByRole("button", { name: /log out/i });
    if ((await logout.count()) === 0) {
      throw new Error("Could not find the admin Log out control.");
    }
    await Promise.all([page.waitForLoadState("load"), logout.first().click()]);
    await page.goto(`${BASE}/admin/`, { waitUntil: "load" });
    await page.waitForSelector("#id_username");
    await page.waitForFunction(
      () => !document.body.innerText.includes("Site administration")
    );
    await shot(page, "admin_logout");

    await context.close();
  } finally {
    await browser.close();
  }
}

async function runApp() {
  const browser = await startBrowser();
  try {
    const context = await browser.newContext({ viewport: null });
    const page = await context.newPage();

    // Task 17 - home page, signed out.
    await page.goto(`${BASE}/`, { waitUntil: "load" });
    await page.locator(".dealer-card").first().waitFor();
    await shot(page, "get_dealers", 0);

    // Sign in as root.
    await page.goto(`${BASE}/login`, { waitUntil: "load" });
    await page.fill("#login-username", "root");
    await page.fill("#login-password", "root123");
    await page.click('button[type="submit"]');
    await page.locator(".user-chip").waitFor();

    // Task 18 - signed in: username chip, Review Dealer buttons, endpoint.
    await page.goto(`${BASE}/`, { waitUntil: "load" });
    await page.getByRole("link", { name: "Review Dealer" }).first().waitFor();
    await shot(page, "get_dealers_loggedin", 58);

    // Task 19 - filtered to Kansas.
    await page.goto(`${BASE}/dealers/Kansas`, { waitUntil: "load" });
    await page.locator(".dealer-card").first().waitFor();
    await page.selectOption("#state-filter", "Kansas");
    await page.waitForFunction(() =>
      document.querySelector("h1")?.textContent.includes("Kansas")
    );
    await shot(page, "dealersbystate", 0);

    // Task 20 - dealer details with reviews.
    await page.goto(`${BASE}/dealer/1`, { waitUntil: "load" });
    await page.locator(".review-card").first().waitFor();
    await shot(page, "dealer_id_reviews", 70);

    // Task 21 - review form filled in, before submission.
    await page.goto(`${BASE}/postreview/1`, { waitUntil: "load" });
    await page.locator("#review").waitFor();
    await page.locator('input[type="checkbox"]').check();
    await page.fill("#purchase_date", "2026-10-20");
    await page.selectOption("#car_make", "Toyota");
    await page.selectOption("#car_model", "Camry");
    await page.fill("#car_year", "2024");
    await page.fill(
      "#review",
      "Fantastic services! The team at Kansas City Auto Mall was friendly, " +
        "quick and completely transparent about pricing. I would happily buy " +
        "my next car here again."
    );
    await shot(page, "dealership_review_submission", 130);

    // Task 22 - the review as posted.
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/dealer\/1/);
    await page
      .getByText("Fantastic services!", { exact: false })
      .first()
      .waitFor();
    await prepare(page, 0);
    await page.evaluate(() =>
      document.querySelector(".review-card")?.scrollIntoView({ block: "center" })
    );
    await wait(700);
    await shot(page, "added_review", 0);

    await context.close();
  } finally {
    await browser.close();
  }
}

if (FLOW === "admin") {
  await runAdmin();
} else if (FLOW === "app") {
  await runApp();
} else {
  throw new Error(`Unknown flow: ${FLOW}`);
}

console.log(`${FLOW} flow complete`);
