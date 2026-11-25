// Contact sheets: node sheet.cjs <video.mp4> [out.png] [everyNFrames]
// One tile per N frames (default 30 = one per second at 30 fps), frame number stamped in the corner.
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const FF = [
  'C:/Users/muwai/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1-full_build/bin/ffmpeg.exe',
  'ffmpeg',
].find((p) => p === 'ffmpeg' || fs.existsSync(p));
const [, , src, dstArg, everyArg] = process.argv;
const every = Number(everyArg || 30);
const dst = dstArg || path.join(__dirname, '..', 'tmp', 'sheets', path.basename(src, '.mp4') + '.png');
fs.mkdirSync(path.dirname(dst), { recursive: true });
const probe = spawnSync(FF, ['-i', src], { encoding: 'utf8' }).stderr;
const portrait = /, (\d+)x(\d+)/.exec(probe);
const w = portrait ? Number(portrait[1]) : 1080, h = portrait ? Number(portrait[2]) : 1920;
const tall = h > w;
const tileW = tall ? 200 : 320;
const cols = tall ? 8 : 5;
const vf = `select='not(mod(n\\,${every}))',scale=${tileW}:-2,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='%{n}':x=4:y=4:fontcolor=yellow:fontsize=16:box=1:boxcolor=black@0.6,tile=${cols}x${tall ? 2 : 3}:padding=2`;
const r = spawnSync(FF, ['-v', 'error', '-y', '-i', src, '-vf', vf, '-vsync', 'vfr', '-frames:v', '1', dst], { encoding: 'utf8' });
if (r.status !== 0) { console.error(r.stderr); process.exit(1); }
const dur = /Duration: ([\d:.]+)/.exec(probe), br = /bitrate: (\d+ kb\/s)/.exec(probe);
console.log(dst, w + 'x' + h, dur && dur[1], br && br[1]);
