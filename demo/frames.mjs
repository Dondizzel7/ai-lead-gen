// Deterministic frame-by-frame render of the demo using CDP virtual time.
// Frames are piped into ffmpeg at an exact 30 fps — no wall-clock drift.
// Usage: node frames.mjs <durations-json> <out.mp4> [page.html]
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const durations = JSON.parse(process.argv[2]);
const outFile = process.argv[3] || 'demo.mp4';
const pageFile = process.argv[4] || 'ghl-followup-demo.html';
const FPS = 30;

const browser = await chromium.launch({
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--force-device-scale-factor=1',
         '--run-all-compositor-stages-before-draw', '--disable-checker-imaging'],
});
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
await page.goto('file://' + path.join(__dirname, pageFile));
await page.waitForTimeout(300);

const cdp = await page.context().newCDPSession(page);
const budgetExpired = () => new Promise(r => cdp.once('Emulation.virtualTimeBudgetExpired', r));

// pause virtual time, then start the demo clock under our control
let exp = budgetExpired();
await cdp.send('Emulation.setVirtualTimePolicy', { policy: 'pauseIfNetworkFetchesPending', budget: 50 });
await exp;
const totalMs = await page.evaluate((d) => window.startDemo(d), durations);
const totalFrames = Math.ceil((totalMs / 1000) * FPS);
console.log('total ms:', totalMs, '→ frames:', totalFrames);

const ff = spawn('ffmpeg', ['-y', '-v', 'error',
  '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p',
  '-movflags', '+faststart', outFile], { stdio: ['pipe', 'inherit', 'inherit'] });

const step = 1000 / FPS;
for (let i = 0; i < totalFrames; i++) {
  exp = budgetExpired();
  await cdp.send('Emulation.setVirtualTimePolicy', { policy: 'pauseIfNetworkFetchesPending', budget: step });
  await exp;
  const { data } = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 92 });
  if (!ff.stdin.write(Buffer.from(data, 'base64'))) {
    await new Promise(r => ff.stdin.once('drain', r));
  }
  if (i % 300 === 0) console.log(`frame ${i}/${totalFrames}`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
console.log('done:', outFile);
await browser.close();
