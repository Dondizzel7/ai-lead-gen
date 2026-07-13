// Records the animated demo page to a WebM using Playwright's screencast.
// Usage: node record.mjs <durations-json> <out-dir>
//   durations-json: JSON array of 9 scene durations in ms
import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const durations = JSON.parse(process.argv[2]);
const outDir = process.argv[3] || path.join(__dirname, 'out');

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM_PATH || undefined,
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--force-device-scale-factor=1'],
});
const context = await browser.newContext({
  viewport: { width: 1280, height: 720 },
  recordVideo: { dir: outDir, size: { width: 1280, height: 720 } },
});
const page = await context.newPage();
await page.goto('file://' + path.join(__dirname, 'ghl-followup-demo.html'));
await page.waitForTimeout(500);

// white sync marker: video is white until the exact moment the demo starts
await page.evaluate(() => { document.body.style.background = '#ffffff'; });
await page.waitForTimeout(1500);
const total = await page.evaluate((d) => {
  document.body.style.background = '';
  return window.startDemo(d);
}, durations);
console.log('demo total ms:', total);
await page.waitForTimeout(total + 800);

await context.close();
const video = page.video();
const p = await video.path();
console.log('video saved:', p);
await browser.close();
