// Debug helper: node probe.cjs <url> [mobile|desktop]  -> saves page HTML, script list and real-time screenshots to ../tmp/probe
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const CHROME = ['C:/Program Files/Google/Chrome/Application/chrome.exe'].find(fs.existsSync);
const dir = path.join(__dirname, '..', 'tmp', 'probe');
fs.mkdirSync(dir, { recursive: true });
(async () => {
  const [, , url, mode = 'mobile'] = process.argv;
  const b = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ['--enable-gpu-rasterization', '--ignore-gpu-blocklist', '--use-angle=d3d11'] });
  const p = await b.newPage();
  await p.setViewport(mode === 'mobile' ? { width: 432, height: 932, deviceScaleFactor: 1, isMobile: true, hasTouch: true } : { width: 1600, height: 1000 });
  const scripts = [];
  p.on('response', async (r) => {
    const u = r.url();
    if (/\.(m?js)(\?|$)/.test(u) || r.request().resourceType() === 'script') {
      try { const t = await r.text(); const f = path.join(dir, 'js-' + scripts.length + '.js'); fs.writeFileSync(f, t); scripts.push(u + ' -> ' + f); } catch (e) {}
    }
  });
  await p.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
  fs.writeFileSync(path.join(dir, 'page.html'), await p.content());
  for (const t of [1, 4, 8, 14]) {
    await new Promise((r) => setTimeout(r, t === 1 ? 1000 : 3000));
    await p.screenshot({ path: path.join(dir, `shot-${t}.png`) });
  }
  const info = await p.evaluate(() => ({
    anims: document.getAnimations().length,
    h: document.documentElement.scrollHeight,
    canvases: document.querySelectorAll('canvas').length,
    ls: Object.keys(localStorage), ss: Object.keys(sessionStorage),
  }));
  console.log(JSON.stringify({ scripts, info }, null, 1));
  await b.close();
})();
