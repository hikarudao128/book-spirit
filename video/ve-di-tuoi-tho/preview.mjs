// Renders props-preview.html boards to build/preview/*.png
// Usage: node preview.mjs
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const out = join(here, 'build', 'preview');
mkdirSync(out, { recursive: true });

let browser;
try { browser = await chromium.launch(); } catch { browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }); }
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('console', (m) => console.log('[page]', m.text()));
page.on('pageerror', (e) => console.error('[pageerror]', e.message));
await page.goto(pathToFileURL(join(here, 'props-preview.html')).href);
await page.waitForFunction(() => window.__ready || window.__error, null, { timeout: 30000 });
const err = await page.evaluate(() => window.__error);
if (err) { console.error(err); process.exit(1); }
await page.evaluate(() => document.fonts.ready);
const ids = await page.evaluate(() => [...document.querySelectorAll('svg.board')].map((s) => s.id));
for (const id of ids) {
  await page.locator(`svg[id="${id}"]`).screenshot({ path: join(out, id + '.png') });
  console.log('wrote', join(out, id + '.png'));
}
await browser.close();
