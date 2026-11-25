# beats-improve-v8: beat-synced motion + the self-improvement kit (Uwais, 25 Nov 14:52)

Uwais approved Engine 6.1 ("Perfect like this"). Commit 2cb5d2d on main. Do NOT change the look: cream #F2EBDD paper, navy #14213D ink, lighter navy #3A4A6B, no counters, no numbered or mono labels, voice from first frame to last, natural pace 150 to 165 wpm, no em or en dashes, never say AI. Read briefs/design-v6.md and briefs/design-v6b.md first.

Do not touch picks/, render/voice/ or render/music/ (voice-music-v7 owns them and is still running). Keep tts and music selection pluggable as they are.

## 1. Beats synced
- Detect the beat grid of whichever music track a reel uses (librosa beat_track, or a numpy onset detector if librosa will not install on this PC's Python 3.14; add librosa to requirements.txt for GitHub's Python 3.11). Cache the grid per track in assets/music_beats.json keyed by track URL or file hash.
- Voice still drives scene timing. On top of that:
  - Snap each scene transition to the nearest beat within about 0.12 s of the voice cue (never cut a word; if no beat is close, keep the voice cue).
  - Land small accents on beats inside a scene: card pops, stamp hits, tick marks, underline draws, cursor blinks, the progress line nudging. Subtle, not a music video.
  - Choose the music start offset so a strong beat lands on frame 1 and the drop or phrase change lands near the CTA.
  - Duck music under the voice (already there), lift it slightly in breaths between sentences.
- Pass beats into Remotion props (beats: number[] in seconds) and expose a helper in kit.tsx (e.g. onBeat(frame, fps, beats, window)).

## 2. Self-improvement kit (used by a nightly scheduled task, so it must be simple and safe)
- improve/rules.md: the locked rules above plus anything in the design briefs Uwais approved. The nightly improver may never break these.
- improve/backlog.md: 15 to 25 concrete small improvements, ranked, each one line with how to verify it (examples: smoother easing on card entries, better hook first 1.5 s, kinetic emphasis on prices, richer paper grain, varied scene types so reels do not repeat, tighter CTA, better music fit per pillar). Mark done items with the date.
- improve/log.md: dated entries, one per change: what changed, why, before and after numbers.
- render/qa.py <mp4> [--json]: automatic scorecard, exit non-zero on a hard fail.
  - Hard: longest silence in voice region over 0.4 s; any frame region of saturated colour outside the palette larger than a small threshold (allow the muted WhatsApp green inside mock-ups); duration under 15 s or over 60 s; bitrate over 4.5 Mbps; black or blank frames.
  - Soft score 0 to 100: words per minute in range, scene count and variety, motion present in every second (frame difference), text inside safe margins, beat alignment percentage of cuts.
- Wire qa.py into render5.py after each render: print a "qa" line in the Actions log and save qa json next to the mp4 in the meta. A hard fail must stop posting (exclude from feed), not crash the workflow.

## Done means
- Previews in tmp/final for sv-092, sv-008, sv-001 with beats, checked by you frame by frame and by qa.py (report scores).
- Commit and push to main yourself, ONE command per call: `git add <paths>` then `git commit -m "..."` then `git pull --rebase` then `git push`. If git or gh is blocked for you, say so in the final report and list the exact commands; do not loop on it.
- One GitHub test render `gh workflow run reel.yml -f id=sv-008 -f post=no`, watched to green, qa line read from the log.
- Final report: what changed, qa scores, beat alignment %, run id.
