// Frame-perfect captures of our real sites (v2).
// timecut virtualises JS time (rAF, Date, performance.now, timers) and screenshots one frame per 1/30 virtual s.
// virtual.cjs adds what timecut lacks: CSS transitions / animations / element.animate are seeked to the virtual
// clock every frame (scroll reveals now play), and media play() returns a Promise (stolenvalour's loader).
// Skipped intro time is stepped one frame at a time (maximumAnimationFrameDuration) instead of jumped, so GSAP lag
// smoothing and rAF driven intros really finish before recording starts.
// Usage: node capture.cjs [siteId|all] [mobile|desktop]   (writes ../assets/clips_new/<site>-<mode>.mp4)
const { timecut, fixScreenshotClip } = require('./virtual.cjs');
const path = require('path');
const fs = require('fs');
const out = path.join(__dirname, '..', 'assets', 'clips_new');
fs.mkdirSync(out, { recursive: true });
const CHROME = ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'].find(fs.existsSync);

const SITES = [
  { id: 'obsidian', url: 'https://obsidian-crown.netlify.app' },
  { id: 'stolenvalour', url: 'https://stolenvalour.co.za', start: 7 }, // loader + logo finish at about 5 s virtual
  { id: 'saxonwold', url: 'https://saxonwold.netlify.app/?brand=randlord' },
  { id: 'kingdomshine', url: 'https://kingdom-shine.netlify.app' },
];
const MODES = [
  { id: 'mobile', viewport: { width: 432, height: 932, deviceScaleFactor: 2.5, isMobile: true, hasTouch: true } },
  { id: 'desktop', viewport: { width: 1600, height: 1000, deviceScaleFactor: 1.2 } },
];
const DUR = Number(process.env.ACE_DUR || 12);
const START = 5; // virtual seconds run (frame by frame, not recorded) so loaders and intros finish
const HOLD = 1.0; // seconds held at the top before the scroll starts
const SCREENS = 3.4; // viewport heights travelled at most

// Gentle eased scroll on the virtual clock. Drives Lenis too when a site exposes it.
function installScroll(dur, start, hold, screens) {
  var ease = function (x) { return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  var t0 = performance.now();
  var y0 = null; // relative to where the page parks itself (obsidian's infinite scroller sits at y=100000)
  var max = function () { return Math.max(0, document.documentElement.scrollHeight - innerHeight - y0); };
  var step = function () {
    var sec = (performance.now() - t0) / 1000 - start - hold;
    if (sec <= -0.05) y0 = null;
    else {
      if (y0 === null) y0 = window.scrollY;
      var p = Math.min(1, Math.max(0, sec / (dur - hold - 0.8)));
      var y = y0 + ease(p) * Math.min(max(), innerHeight * screens);
      if (window.lenis && typeof window.lenis.scrollTo === 'function') {
        try { window.lenis.scrollTo(y, { immediate: true, force: true }); } catch (e) {}
      }
      window.scrollTo(0, y);
    }
    requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

(async () => {
  const only = process.argv[2];
  const onlyMode = process.argv[3];
  for (const m of MODES) {
    if (onlyMode && m.id !== onlyMode) continue;
    for (const s of SITES) {
      if (only && only !== 'all' && s.id !== only) continue;
      const file = path.join(out, `${s.id}-${m.id}.mp4`);
      if (fs.existsSync(file)) {
        if (!process.argv.includes('--force')) { console.log('skip', file); continue; }
        const keep = path.join(__dirname, '..', 'tmp', 'retakes');
        fs.mkdirSync(keep, { recursive: true });
        fs.renameSync(file, path.join(keep, `${s.id}-${m.id}-${Date.now()}.mp4`)); // never delete: park old take
      }
      const start = s.start != null ? s.start : START;
      console.log('capturing', s.id, m.id);
      try {
        await timecut({
          url: s.url, viewport: m.viewport, fps: 30, start, duration: DUR, startDelay: 2, output: file,
          executablePath: CHROME, quiet: true,
          maximumAnimationFrameDuration: 1000 / 30,
          launchArguments: ['--enable-gpu-rasterization', '--ignore-gpu-blocklist', '--use-angle=d3d11', '--hide-scrollbars', '--mute-audio'],
          outputOptions: ['-c:v', 'libx264', '-crf', '19', '-preset', 'slow', '-maxrate', '4500k', '-bufsize', '9000k', '-pix_fmt', 'yuv420p', '-movflags', '+faststart'],
          preparePage: async (page) => { fixScreenshotClip(page); await page.evaluate(installScroll, DUR, start, HOLD, SCREENS); },
          preparePageForScreenshot: async (page) => { await page.evaluate(() => window.__aceSeek && window.__aceSeek()); },
        });
        console.log('done', file, fs.statSync(file).size);
      } catch (e) { console.log('FAILED', s.id, m.id, e.message); }
    }
  }
})();
