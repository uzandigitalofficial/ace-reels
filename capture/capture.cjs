// Smooth, frame-perfect captures of our real sites. timecut virtualises time (rAF, Date, performance.now),
// so WebGL scenes and our injected scroll advance exactly one frame per frame: no stutter.
// Usage: node capture.cjs [siteId]   (writes ../assets/clips/<site>-<mode>.mp4)
const timecut = require('timecut');
const path = require('path');
const fs = require('fs');
const out = path.join(__dirname, '..', 'assets', 'clips');
fs.mkdirSync(out, { recursive: true });
const CHROME = ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'].find(fs.existsSync);

const SITES = [
  { id: 'obsidian', url: 'https://obsidian-crown.netlify.app' },
  { id: 'stolenvalour', url: 'https://stolenvalour.co.za', start: 17 },
  { id: 'saxonwold', url: 'https://saxonwold.netlify.app/?brand=randlord' },
  { id: 'kingdomshine', url: 'https://kingdom-shine.netlify.app' },
];
const MODES = [
  { id: 'mobile', viewport: { width: 432, height: 932, deviceScaleFactor: 2.5, isMobile: true, hasTouch: true } },
  { id: 'desktop', viewport: { width: 1600, height: 1000, deviceScaleFactor: 1.2 } },
];
const DUR = 10;
const START = 8; // virtual seconds skipped first, so site intros and loaders finish before recording

(async () => {
  const only = process.argv[2];
  for (const m of MODES) {
    for (const s of SITES) {
      if (only && s.id !== only) continue;
      const file = path.join(out, `${s.id}-${m.id}.mp4`);
      if (fs.existsSync(file)) { console.log('skip', file); continue; }
      console.log('capturing', s.id, m.id);
      try {
        await timecut({
          url: s.url, viewport: m.viewport, fps: 30, start: s.start || START, duration: DUR, startDelay: 3, output: file,
          executablePath: CHROME,
          launchArguments: ['--enable-gpu-rasterization', '--ignore-gpu-blocklist', '--use-angle=d3d11', '--hide-scrollbars'],
          outputOptions: ['-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p'],
          preparePage: async (page) => {
            await page.evaluate((dur, start) => {
              const ease = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
              let t0 = null;
              const max = () => Math.max(0, document.documentElement.scrollHeight - innerHeight);
              const step = (now) => {
                if (t0 === null) t0 = now;
                const p = Math.min(1, Math.max(0, ((now - t0) / 1000 - start - 0.8) / (dur - 1.8)));
                window.scrollTo(0, ease(p) * Math.min(max(), innerHeight * 2.6));
                requestAnimationFrame(step);
              };
              requestAnimationFrame(step);
            }, DUR, s.start || START);
          },
        });
        console.log('done', file, fs.statSync(file).size);
      } catch (e) { console.log('FAILED', s.id, m.id, e.message); }
    }
  }
})();
