// Render video: node render.mjs [--workers 4] [--from 0] [--to N] [--stills 100,200]
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const { chromium } = await import(path.join(process.env.PW_ROOT || '/opt/node22/lib/node_modules', 'playwright/index.mjs')).catch(async () => {
  const root = (await import('node:child_process')).execSync('npm root -g').toString().trim();
  return import(path.join(root, 'playwright/index.mjs'));
});
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const timing = JSON.parse(fs.readFileSync(path.join(here, 'build/timing.json'), 'utf8'));
const total = timing.totalFrames;
const from = +arg('from', 0), to = +arg('to', total), workers = +arg('workers', 4);
const stills = arg('stills', '');
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }).catch(() => chromium.launch());

async function openPage() {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('console', (m) => { if (['error', 'warning'].includes(m.type())) console.log('[page]', m.text()); });
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  await page.goto('file://' + path.join(here, 'engine.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate((t) => window.ENGINE.init(t), timing);
  return page;
}

if (stills) {
  const page = await openPage();
  fs.mkdirSync(path.join(here, 'build/stills'), { recursive: true });
  for (const f of stills.split(',').map(Number).sort((a, b) => a - b)) {
    await page.evaluate((n) => window.ENGINE.simTo(n), f);
    await page.screenshot({ path: path.join(here, `build/stills/f${String(f).padStart(5, '0')}.png`) });
  }
  await browser.close(); process.exit(0);
}

// Lượt 1: mô phỏng toàn bộ để lấy danh sách hiệu ứng âm thanh
{
  const page = await openPage();
  await page.evaluate((n) => window.ENGINE.simTo(n), total - 1);
  const ev = await page.evaluate(() => window.ENGINE.sfxEvents());
  fs.writeFileSync(path.join(here, 'build/sfx_events.json'), JSON.stringify(ev));
  console.log('sfx events', ev.length);
  await page.close();
}

const segDir = path.join(here, 'build/seg'); fs.mkdirSync(segDir, { recursive: true });
const span = Math.ceil((to - from) / workers);
const t0 = Date.now();
const jobs = [];
for (let w = 0; w < workers; w++) {
  const a = from + w * span, b = Math.min(to, a + span);
  if (a >= b) continue;
  jobs.push((async () => {
    const page = await openPage();
    const out = path.join(segDir, `seg${w}.mp4`);
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', '24', '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', '24', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = a; f < b; f++) {
      await page.evaluate((n) => window.ENGINE.simTo(n), f);
      const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if (w === 0 && (f - a) % 240 === 0) console.log(`worker0 ${f - a}/${b - a} frames, ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end();
    await new Promise((r) => ff.on('close', r));
    await page.close();
    return out;
  })());
}
const segs = await Promise.all(jobs);
fs.writeFileSync(path.join(segDir, 'list.txt'), segs.map((s) => `file '${s}'`).join('\n'));
await new Promise((r) => spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(segDir, 'list.txt'), '-c', 'copy', path.join(here, 'build/video.mp4')], { stdio: 'inherit' }).on('close', r));
console.log('done in', ((Date.now() - t0) / 1000).toFixed(0), 's');
await browser.close();
