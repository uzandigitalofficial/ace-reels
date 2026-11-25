# beats-improve-v8b: continuation (25 Nov 18:20)

The session for briefs/beats-improve-v8.md was cut off at 14:56 by a usage limit after only reading code (about 28 tool calls, nothing written). Read briefs/beats-improve-v8.md and carry it out in full; it is the brief. Check git status first in case anything was written.

Notes from the first attempt:
- librosa is installed on this PC. Python 3.14 here; GitHub uses 3.11.
- Run one command per tool call (no `;`, `&&` or pipes), since compound commands need approval in headless runs and get refused.
- A voice-music-v7b session is finishing picks/, render/voice/ and render/music/ at the same time, and may edit publish/pages.sh and .gitignore. Do not touch those paths. If you need pages.sh or .gitignore changed, pull first and make a small edit.
- Commit only your own paths. `git pull --rebase` before `git push`.

## Report (25 Nov 2026, 19:10)
What changed (commit 30b7c50 on main; the look is untouched):
- render/beats.py: librosa beat_track grid per track (tempo, beats, strong beats on the bar phase with the most onset energy,
  phrase changes where the energy of the next 4 beats jumps over 25 % above the previous 4), cached in assets/music_beats.json
  keyed by URL or file sha1 (all 6 brand tracks pre-cached, so GitHub skips the analysis). librosa>=0.10 is in requirements.txt.
- Music offset: always a strong beat on frame 1; the cost also rewards a phrase change within 1.5 s of the CTA cut (8 bar grid when
  the track has none) and the number of cuts that can sit on a beat. Remotion plays it with trimBefore.
- Cuts: each scene cut moves to the nearest beat within 0.12 s of the voice cue, never before the previous beat's last word and
  never after this beat's first word (seg "cut"; sfx swoosh and tap follow it). Voice timing is unchanged.
- Accents (kit.tsx onBeat, beatDelay, useBeatDelay, useBeatPulse, useBlink, BeatCtx): stamps, ticks, crosses, pins, wax seal, price
  slams, underline swashes, chat bubbles (only later, never earlier), main cards and sticky notes land on beats; the text cursors
  blink on the beat; the progress line nudges thicker on each beat. No beats means exactly the old behaviour.
- Music ducked at 0.06 under the voice, lifts to 0.095 in gaps between words over 0.14 s, 3 frame fade in so the first beat is heard.
- Pace fix (needed to pass qa): Chatterbox reads at 193 to 206 wpm, and one 0.86 stretch left reels at 164 to 179 wpm. tts() now does
  a second smaller pass (total stretch floor 0.78), which brings all three into 156 to 164 wpm.
- render/qa.py <mp4> [--voice] [--props] [--json]: hard checks (voice silence over 0.4 s, off palette area over 0.6 % with WhatsApp
  green, navy blues and footage windows allowed, 15 to 60 s, over 4.5 Mbps, black or blank frames) and a soft score of 5 x 20 (wpm,
  scene count and variety, motion every second, safe margins, beat alignment). render5.py prints a "qa:" line, stores meta["qa"], and
  on a hard fail sets meta["qa_fail"]. feed.py leaves qa_fail reels out of the feed and post_ig.py skips them (exit 0, no crash).
  A qa crash is caught and logged as skipped.
- improve/rules.md (locked rules), improve/backlog.md (23 ranked items, 2 marked done), improve/log.md (first entry).
Decisions: the beat window is 0.12 s each side of the cue, as the brief says; a cut counts as "on a beat" in qa within 35 ms. Offsets use
only strong beats, so the first frame is always on the bar. Card snapping is only on the main card of each scene, so staggered cascades
keep their rhythm. No props or voice stems are written into out/, because pages.sh copies out/* to the gallery.

Previews in tmp/final (Chatterbox voice; .sheet.jpg, .voice.wav and .props.json kept next to each), checked on the contact sheets
(cream and navy only, no counters, CTA on screen while it is spoken, cuts clean):
  sv-092 20261125-1645: PASS 95/100, 21.3 s, 3.84 Mbps, 160 wpm, silence 0.31 s, beats 75 % of cuts (music from 4.60 s)
  sv-008 20261125-1651: PASS 95/100, 25.1 s, 3.92 Mbps, 161 wpm, silence 0.32 s, beats 75 % of cuts (music from 8.62 s)
  sv-001 20261125-1656: PASS 100/100, 20.1 s, 3.89 Mbps, 161 wpm, silence 0.33 s, beats 100 % of cuts (music from 51.55 s)
  Average beat alignment 83 % of cuts. None of the reels found a real drop near the CTA (track 744 has no strong energy jump),
  so the 8 bar phrase grid was used.
GitHub test render: run 45659661661 (sv-008, post=no), green. Log: "qa: PASS score 95/100 | 24.32 s 3.97 Mbps 165 wpm | silence 0.329 s |
  off palette 0.0% | beats 75% of 4 cuts".
Not done: nothing in the brief. I could not run git fetch or tsc here (approval prompts). git pull --rebase reported up to date before the push.
