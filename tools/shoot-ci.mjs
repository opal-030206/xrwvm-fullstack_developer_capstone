/**
 * Captures the green GitHub Actions run page as screenshots/CICD.png
 * (Task 23), using the same window-capture + verification helpers as shoot.mjs.
 *
 *   node tools/shoot-ci.mjs
 */
import { execFileSync } from "node:child_process";
import { statSync } from "node:fs";
import { chromium } from "playwright-core";

const ROOT = "D:\\guestbook-final-project\\cars-dealership";
const SHOTS = `${ROOT}\\screenshots`;
const URL =
  process.env.CI_URL ||
  "https://github.com/opal-030206/Capstone_carDealership/actions/runs/41175652194";
const NAME = "CICD";

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function capture(name) {
  const out = `${SHOTS}\\${name}.png`;
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
      `shotmarker-${name}`,
    ],
    { encoding: "utf8" }
  ).trim();

  const match = /(\d+)x(\d+) uniqueColors=(\d+) mode=(\w+) front=(\w+) title='(.*)'/.exec(result);
  const colors = match ? Number(match[3]) : 0;
  const bytes = statSync(out).size;
  console.log(
    `${name}.png  ${match ? `${match[1]}x${match[2]}` : "?"}  ${Math.round(bytes / 1024)}KB  colors=${colors}  mode=${match ? match[4] : "?"}`
  );
  if (bytes < 20000 || colors < 40) {
    throw new Error(`Capture for ${name} looks wrong (${bytes} bytes, colors=${colors}).`);
  }
  return out;
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
  const summary = verdict.split(/\r?\n/).find((line) => line.startsWith("bestOffset"));
  console.log(`   verify: ${summary}`);
  if (!verdict.includes("VERDICT: window capture contains the page")) {
    throw new Error(`Window capture for ${name} is not showing this page.\n${verdict}`);
  }
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

  await page.goto(URL, { waitUntil: "load", timeout: 60000 });
  // Wait for the run summary to render its job list.
  await page.getByText("Django tests", { exact: false }).first().waitFor({ timeout: 60000 });
  await page.waitForFunction(() => /success/i.test(document.body.innerText), { timeout: 60000 });

  await page.evaluate((marker) => (document.title = `Cars Dealership ${marker}`), `shotmarker-${NAME}`);
  await wait(1200);

  const pageFile = `${SHOTS}\\tmp\\${NAME}-page.png`;
  await page.screenshot({ path: pageFile });
  capture(NAME);
  verify(NAME, pageFile);

  await context.close();
} finally {
  await browser.close();
}
