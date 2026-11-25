#!/usr/bin/env bash
# Keep a rolling gallery of the newest 15 reels on the gh-pages branch (GitHub Pages hosts the public mp4 URLs Instagram needs).
set -euo pipefail
git config --global user.name "ace-reels"
git config --global user.email "ace-reels@users.noreply.github.com"
rm -rf site && mkdir -p site
if git ls-remote --exit-code --heads origin gh-pages >/dev/null; then
  git clone -q --depth 1 --branch gh-pages "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" site
  rm -rf site/.git
fi
mkdir -p site/reels
cp out/* site/reels/
ls -t site/reels/*.mp4 | tail -n +16 | while read -r f; do b="${f%.mp4}"; rm -f "$b.mp4" "$b.jpg" "$b.json"; done
if [ -f picks/index.html ]; then  # the voice and music pick sheet: page, licences and final mp3s only, never picks/_raw
  rm -rf site/picks && mkdir -p site/picks/voice site/picks/music
  cp picks/index.html site/picks/
  [ -f picks/LICENCES.md ] && cp picks/LICENCES.md site/picks/
  cp picks/voice/*.mp3 site/picks/voice/
  cp picks/music/*.mp3 site/picks/music/
fi
python publish/index.py site
python publish/feed.py site
touch site/.nojekyll
cd site
git init -q -b gh-pages
git add -A
git commit -qm "reels $(date -u +%F-%H%M)"
git push -qf "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" gh-pages
echo "gallery updated"
