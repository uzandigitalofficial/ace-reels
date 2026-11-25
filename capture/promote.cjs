// Promote fresh captures: assets/clips/*.mp4 -> assets/clips_old/<stamp>/, then assets/clips_new/*.mp4 -> assets/clips/.
// Never deletes anything. Usage: node promote.cjs <stamp>
const fs = require('fs');
const path = require('path');
const A = path.join(__dirname, '..', 'assets');
const stamp = process.argv[2] || new Date().toISOString().slice(0, 10);
const fresh = fs.readdirSync(path.join(A, 'clips_new')).filter((f) => f.endsWith('.mp4'));
const old = path.join(A, 'clips_old', stamp);
fs.mkdirSync(old, { recursive: true });
for (const f of fresh) {
  const cur = path.join(A, 'clips', f);
  if (fs.existsSync(cur)) { fs.renameSync(cur, path.join(old, f)); console.log('parked', f, '->', path.relative(A, old)); }
  fs.renameSync(path.join(A, 'clips_new', f), cur);
  console.log('promoted', f);
}
