// Debug: virtual-time snapshots, one every 1/fps seconds, no scroll. node dbg.cjs <url> <seconds> [fps] [mobile|desktop]
const { timesnap } = require('./virtual.cjs');
const fs = require('fs');
const path = require('path');
const CHROME = ['C:/Program Files/Google/Chrome/Application/chrome.exe'].find(fs.existsSync);
const [, , url, secs = '20', fps = '1', mode = 'mobile'] = process.argv;
const dir = path.join(__dirname, '..', 'tmp', 'dbg');
fs.mkdirSync(dir, { recursive: true });
(async () => {
  await timesnap({
    url, fps: Number(fps), duration: Number(secs), outputDirectory: dir, outputPattern: 'f-%03d.png',
    viewport: mode === 'mobile' ? { width: 432, height: 932, deviceScaleFactor: 1, isMobile: true, hasTouch: true } : { width: 1600, height: 1000 },
    executablePath: CHROME, quiet: true, maximumAnimationFrameDuration: 1000 / 30,
    launchArguments: ['--enable-gpu-rasterization', '--ignore-gpu-blocklist', '--use-angle=d3d11', '--hide-scrollbars'],
    navigatePageToURL: async ({ page, url }) => {
      await page.setRequestInterception(true);
      page.on('request', async (req) => {
        if (/Base\.astro_astro_type_script/.test(req.url())) {
          const r = await fetch(req.url());
          let body = await r.text();
          body = body.replace('loadingUIController.show();', 'loadingUIController.show();window.__lui=loadingUIController;window.__plm=pageLoadingManager;');
          return req.respond({ status: 200, contentType: 'application/javascript', body });
        }
        req.continue();
      });
      await page.goto(url, { waitUntil: 'networkidle0' });
    },
    preparePage: async (page) => {
      page.on('console', (m) => console.log('console:', m.text().slice(0, 200)));
      page.on('pageerror', (e) => console.log('pageerror:', e.message.slice(0, 200)));
      await page.evaluate(() => { window.__rafs = 0; const f = () => { window.__rafs++; requestAnimationFrame(f); }; requestAnimationFrame(f); window.__tms = 0; setInterval(() => window.__tms++, 100); });
    },
    preparePageForScreenshot: async (page, n) => {
      const s = await page.evaluate(() => ({ t: Math.round(performance.now()), y: scrollY, ov: !!document.querySelector('#loading-overlay:not([data-hidden])'), an: document.getAnimations().length, rafs: window.__rafs, rafsrc: String(window.requestAnimationFrame).slice(0, 60),tms: window.__tms,lui: window.__lui && { rp: __lui._realProgress, dp: __lui._displayProgress, ct: __lui._currentTime, tt: __lui._targetTime, done: __lui._isProgressComplete, logo: __lui._isLogoPlaying, lt: __lui._logoCurrentTime, anim: __lui._isAnimating, hp: !!__lui._hidePromise, pcr: !!__lui._progressCompleteResolve }, items: window.__plm && [...__plm._loadingItems.values()].filter((x) => !x.completed).map((x) => x.id).join(','),logo: (document.querySelector('#loading-logo') || {}).style?.opacity, body: JSON.stringify(document.body.dataset), lottie: (document.querySelector('#loading-lottie') || {}).style?.opacity, vids: [...document.querySelectorAll('video')].map((v) => v.readyState + ':' + v.paused).join(',') }));
      console.log('frame', n, JSON.stringify(s));
    },
  });
})();
