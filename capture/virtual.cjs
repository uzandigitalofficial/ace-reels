// Require this BEFORE timecut / timesnap. It upgrades timeweb (the virtual clock timesnap injects into pages):
//  1. Media play() returns a Promise like the real one. Sites that call video.play().catch(...) threw under the
//     stock timeweb, which stalled stolenvalour.co.za's loader forever (the intro never finished).
//  2. Appends an animation seeker: after every virtual frame, every document-timeline Web Animation (CSS
//     transitions, CSS animations, element.animate) is paused and set to the virtual clock. CSS motion then
//     advances exactly 1/30 s per captured frame, in lockstep with rAF, WebGL and GSAP. Scroll-driven animations
//     (ScrollTimeline / ViewTimeline) are left alone since they already follow the scroll position.
const fs = require('fs');
const path = require('path');

function seeker() {
  var seen = new WeakMap();
  function seek() {
    if (!document.getAnimations) return;
    var now = performance.now(); // virtual
    var list = document.getAnimations();
    for (var i = 0; i < list.length; i++) {
      var a = list[i];
      if (a.timeline && a.timeline !== document.timeline) continue;
      if (!seen.has(a)) seen.set(a, now);
      if (a.playState !== 'paused') a.pause();
      a.currentTime = (now - seen.get(a)) * (a.playbackRate || 1);
    }
  }
  window.__aceSeek = function () { try { seek(); } catch (e) {} };
  window.timeweb.on('postanimate', window.__aceSeek);
  window.timeweb.on('postseek', window.__aceSeek);
}

const timesnapDir = path.dirname(require.resolve('timesnap/package.json', { paths: [path.dirname(require.resolve('timecut'))] }));
const TIMEWEB = path.resolve(require.resolve('timeweb/dist/timeweb.js', { paths: [timesnapDir] }));
const readFileSync = fs.readFileSync;
fs.readFileSync = function (p, ...rest) {
  const r = readFileSync.call(fs, p, ...rest);
  if (typeof p === 'string' && path.resolve(p) === TIMEWEB) {
    const src = String(r);
    const report = 'catch (e) { try { (self.reportError || console.error)(e); } catch (_) {} }';
    const edits = [
      // media play() returns a Promise
      [/(node\.play = function \(\) \{[\s\S]*?node\.dispatchEvent\(new CustomEvent\('play', \{ detail: timewebEventDetail \}\)\);)(\s*\};)/,
        '$1\n      return Promise.resolve();$2'],
      // a throwing rAF callback must not drop every other callback queued for that frame (browsers isolate them;
      // stock timeweb aborted the frame, which silently killed stolenvalour's render loop and shader precompile)
      ['block.fn(virtualNow());', 'try { block.fn(virtualNow()); } ' + report],
      // same isolation for timers
      ['block.fn.apply(exportObject, block.args);', 'try { block.fn.apply(exportObject, block.args); } ' + report],
      // after each virtual step timeweb waits for every playing <video> to fire 'seeked'. Off-DOM videos (WebGL
      // video textures) stalled that wait and froze rAF on stolenvalour. Seek them without waiting; wait for
      // on-page videos at most 400 ms real time.
      ['return media.goToTime();', 'if (!media.node.isConnected) { media.goToTime(); return; } return Promise.race([media.goToTime(), new Promise(function (r) { __aceRealSetTimeout(r, 400); })]);'],
    ];
    let fixed = 'var __aceRealSetTimeout = self.setTimeout.bind(self);\n' + src;
    for (const [from, to] of edits) {
      const next = fixed.replace(from, to);
      if (next === fixed) throw new Error('timeweb patch did not apply (' + String(from).slice(0, 40) + '); check the timeweb version');
      fixed = next;
    }
    fs.readFileSync = readFileSync; // one-shot
    return fixed + '\n;(' + seeker.toString() + ')();\n';
  }
  return r;
};
// timesnap's bundled Puppeteer (2.x) passes the screenshot clip to Chrome in document coordinates, while timesnap
// computes it once as viewport (0,0). After any scroll the capture stayed pinned to the document top: fixed headers
// drifted down and everything past one screen recorded as blank. Shift the clip by the live scroll offset.
function fixScreenshotClip(page) {
  const orig = page.screenshot.bind(page);
  page.screenshot = async (opts = {}) => {
    if (!opts.clip) return orig(opts);
    const s = await page.evaluate(() => ({ x: window.scrollX, y: window.scrollY }));
    return orig({ ...opts, clip: { ...opts.clip, x: opts.clip.x + s.x, y: opts.clip.y + s.y } });
  };
}

// timesnap reads timeweb lazily (on the first capture), so the hook stays until that read, then removes itself.
module.exports = { timecut: require('timecut'), timesnap: require('timesnap'), fixScreenshotClip };
