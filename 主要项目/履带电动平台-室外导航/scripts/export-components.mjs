import path from "node:path";
import { mkdir } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright";

const rootDir = process.cwd();
const htmlPath = path.resolve(rootDir, "hmi_menu_demo.html");
const outputDir = path.resolve(rootDir, "exports", "png");

const captureTasks = [
  { target: "home", selector: "#page-home", name: "home_overview.png" },
  { target: "gps", selector: "#page-gps .gps-left", name: "gps_info_panel.png" },
  { target: "gps", selector: "#page-gps .gps-map-wrap", name: "gps_map_panel.png" },
  { target: "obstacle", selector: "#page-obstacle .obs-left", name: "obstacle_distance_panel.png" },
  { target: "obstacle", selector: "#page-obstacle .obs-right", name: "obstacle_envelope_panel.png" },
  { selector: ".menu", name: "right_menu.png" },
  { selector: ".emergency", name: "emergency_bar.png" },
  { selector: ".stop-btn", name: "emergency_button.png" }
];

async function activatePage(page, target) {
  if (!target) return;
  await page.locator(`.menu-btn[data-target="${target}"]`).click();
  await page.waitForTimeout(150);
}

async function main() {
  await mkdir(outputDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1366, height: 820 },
    deviceScaleFactor: 2
  });
  const page = await context.newPage();

  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "load" });
  await page.waitForTimeout(300);

  for (const task of captureTasks) {
    await activatePage(page, task.target);
    const locator = page.locator(task.selector).first();
    await locator.waitFor({ state: "visible", timeout: 5000 });
    const savePath = path.join(outputDir, task.name);
    await locator.screenshot({ path: savePath });
    console.log(`exported: ${task.name}`);
  }

  await browser.close();
  console.log(`done: ${outputDir}`);
}

main().catch((err) => {
  console.error("export failed:", err);
  process.exit(1);
});
