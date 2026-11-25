# design-v6b: cream and navy, no slide numbers, voice the whole way (Uwais, 25 Nov 14:14)

Continue from the current working tree in C:\Users\muwai\ace-reels (design-v6 work is uncommitted on disk: reel/src/scenes.tsx, kit.tsx, types.ts, Reel.tsx, Root.tsx, render/render5.py, render/scenes.py, render/preview.py, render/textures.py, assets/paper). Read briefs/design-v6.md first for the full style direction. Uwais approved the paper style ("Good") with these changes:

## 1. Cream and navy
- Background: warm cream paper (around #F2EBDD, keep the paper texture). Ink: deep navy (around #14213D) for all headlines, body text, icons, card outlines, the progress line and the italic highlight words.
- Drop the coral red everywhere (chips, italic highlights, stamps, wax seal, prices, progress bar). Use navy, or a lighter navy tint (around #3A4A6B) for secondary text. Card fills stay white or a lighter cream.
- The only other colour allowed is inside realistic UI mock-ups where it is part of the real thing (WhatsApp green bubble, Google map pin). Keep those muted.
- Update brands/stolenvalour.json colours to match so every reel uses it.

## 2. Remove the template look
- Remove the "01 / 05" slide counter at the top. Remove the mono "// 01 the tip_" style eyebrow labels and any other numbered step labels. Remove the mono "STOLEN VALOUR" strip at the top. A small serif SV wordmark in a corner is fine, nothing else up there.
- Nothing that looks like a generic AI template: no mono code-style labels, no "//", no underscores, no numbering.

## 3. Voice speaks the entire reel, realistic pacing
- The voice must run from frame 1 to the final frame. No silent stretches longer than about 0.35 s, no music-only intro, no silent end card. The CTA card is on screen while the voice says the CTA.
- Drive every scene's timing from the voice's word timestamps (faster-whisper), not fixed durations. The video length = voice length + about 0.4 s tail.
- Natural pacing: roughly 150 to 165 words a minute, short natural pauses between sentences (0.15 to 0.3 s), never rushed, never dragging. If a script is too short to cover the scenes, extend the script (write more useful words in the same plain voice) rather than padding with silence. Check every script in content/stolenvalour.json and fix any that would leave gaps.
- Remove the evening music-only format (slot 2): all three daily slots are voiced.
- Captions/word highlights stay synced to the voice.
- Voice engine choice is being made in the voice-music-v7 session (pick sheet at /picks/). Keep tts in render5.py pluggable: one function, engine set in brands/stolenvalour.json, so the chosen voice drops in without touching scenes. Do not change which engine is used yourself; use the current one for previews.
- Music sits under the voice, ducked (voice clearly on top).

## Done means
- Previews in tmp/final for sv-092, sv-008 and sv-001 with contact sheets, checked by you frame by frame: cream and navy only, no counters or numbered labels, voice present across the whole timeline (check with ffmpeg silencedetect, report the longest silence per reel).
- All work committed and pushed to main (one command per call, no compound commands: `git add <paths>` then `git commit -m ...` then `git push`).
- One GitHub test render with post=no (`gh workflow run reel.yml -f id=sv-092 -f post=no`), watched to green.
- A short report at the end: what changed, longest silence per reel, run id.

## Report (25 Nov 2026)
What changed:
- Cream and navy: kit palette is paper #F2EBDD, ink #14213D, soft navy #3A4A6B, cards white or cream #FBF7EE. Coral removed everywhere
  (chips, accents, stamps, wax seal, pins, prices, progress line, captions); ticks are navy. Only muted WhatsApp green (#4F9B73, bubble
  #DCF3D6) inside chat and button mock-ups. Envelope, board and sticky notes are cream tones. New texture assets/paper/paper-cream.jpg
  (old warm, cool and cork textures moved to _to_delete/). brands/stolenvalour.json "colors" now hold the palette and Reel.tsx applies
  them at render time (applyPalette), so every reel follows the brand file.
- Template look removed: no "01 / 05" counter, no mono STOLEN VALOUR strip, no "// 0x" labels (Label component deleted), no "fig. 0x",
  no mono font at all (JetBrains Mono dropped). Top of frame: navy progress line plus a small serif SV wordmark.
- Voice end to end (render/render5.py, engine 6.1): one tts(texts, brand) entry point; engine set by brands "tts": {"engine": "chatterbox"}
  (ENGINES dict, Kokoro fallback; TTS_ENGINE env override is for local dev only). Shared post-processing for any engine: trim each take,
  cut pauses over 0.32 s to 0.24 s, time-stretch (ffmpeg atempo, pitch kept) into 150 to 165 wpm, then faster-whisper word timestamps.
  Each scene starts on its beat's first word; gaps 0.21 s after a sentence, 0.15 s otherwise; voice starts at 0.04 s; video = voice + 0.4 s.
  Scene padding (MIN_VOICE) and the evening music-only slot are gone: all three slots are voiced. Music ducked to 0.06 under the voice,
  sfx 0.55. Each render logs and stores (meta json "voice_longest_silence") an ffmpeg silencedetect check of the voice stem.
- Whisper now gets a 16 kHz array instead of a file path (avoids a PyAV version clash seen locally).
- Scripts: all 120 checked. At 158 wpm every beat outlasts its scene animation, so nothing needed padding; 5 short beats were extended
  (sv-100 line 1, sv-112 line 3, sv-116 line 1, sv-002 and sv-004 CTA). 41 DM CTAs now say "DM us the word SITE" to match the CTA card.
  No dashes, no AI mentions; prices only R2,000 Studio and R5,000 Showroom (R2,000 Studio confirmed in jarvis brain knowledge/prices.md).

Previews (tmp/final, with .sheet.jpg contact sheets and .voice.wav stems), checked frame by frame: cream and navy only, no counters or
numbered labels, captions on the voice, CTA card on screen while the CTA is spoken.
  sv-092 20261125-1236: 20.6 s, 161 wpm, longest silence inside the voice 0.32 s
  sv-008 20261125-1237: 26.3 s, 160 wpm, longest silence 0.33 s
  sv-001 20261125-1239: 20.1 s, 162 wpm, longest silence 0.30 s
  (silencedetect -35 dB on the voice stems; on the final mp4s the only silence is the planned 0.4 s tail.)
  IMPORTANT: these previews use the Kokoro fallback voice, because Chatterbox is not installed in this PC's Python 3.14. The timing
  pipeline is engine-agnostic, so Chatterbox renders on GitHub go through the same trim, pace and silence check.

Not done (blocked): this non-interactive session cannot get approval for git add/commit/push or gh, so nothing is committed or pushed
and the GitHub test render was not run. Run, one per call:
  git add brands/stolenvalour.json content/stolenvalour.json reel/src render/render5.py render/preview.py render/scenes.py render/sheet.py render/teach_bank.py render/textures.py assets/paper briefs/design-v6.md briefs/design-v6b.md
  git commit -m "Engine 6.1: cream and navy, no template labels, voice drives every scene end to end"
  git pull --rebase
  git push
  gh workflow run reel.yml -f id=sv-092 -f post=no
Then check the run log line "voice check: ... longest silence" (Chatterbox). Leave picks/, render/voice/ and assets/clips_new/ to their
own sessions.

Rules: no em or en dashes in any on-screen text or script. Never say AI or "made with AI". Prices only as already in content (R5,000 Showroom; check the Studio price against C:\Users\muwai\jarvis brain knowledge prices.md before keeping any R2,000).
