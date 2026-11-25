# voice-music-v7b: finish the voice and music pick sheet (continuation, 25 Nov 18:20)

The session for briefs/voice-music-v7.md was cut off at 14:56 by a usage limit, part way through. Read that brief first, then look at what already exists before doing anything: picks/ (including picks/_raw/best.json), render/voice/ (gen_local.py), render/music/ (fetch.py, build_picks.py, sheet_html.py). Do not redo work that is already there; finish it.

Since then (do not undo): Engine 6.1 is on main (cream and navy, voice drives every scene, music ducked under the voice, tts engine chosen by a "tts" setting in brands/stolenvalour.json). A separate session owns beats (assets/music_beats.json, render/qa.py, improve/). Do not touch reel/src, render/render5.py scene timing, or improve/.

## Finish
1. Pick sheet at picks/index.html: about 6 voices (V1 to V6, each reading the same 15 to 20 second Stolen Valour script, loudness matched around -16 LUFS) and about 6 music beds (M1 to M6, 20 to 30 seconds each, licence and credit line shown for each; only tracks free for commercial use; note any that need a caption credit). Plain cream and navy page, big play buttons, works on a phone.
2. Publish it on GitHub Pages at https://uzandigitalofficial.github.io/ace-reels/picks/. publish/pages.sh rebuilds gh-pages from scratch on every reel run, so make pages.sh copy picks/ (only the page and the final audio files, mp3 128k or smaller, nothing from picks/_raw) into the site, so the sheet survives every run. Keep picks/_raw out of git (add it to .gitignore).
3. Make each voice and each track drop-in ready: a voice id that can be set as "tts" in brands/stolenvalour.json, and a track entry that can be set as the music list there. Write the exact values for each V# and M# in picks/README.md. Do not change the live brand settings yourself.
4. Commit and push, ONE command per call: `git add <paths>`, then `git commit -m "..."`, then `git pull --rebase`, then `git push`. Then trigger a Pages publish with a test render: `gh workflow run reel.yml -f id=sv-092 -f post=no`, wait for it, and check that /picks/ loads and every player plays (curl the audio URLs for 200).
5. Final report: the URL, what each V# and M# is, any credit lines needed.

No em or en dashes anywhere. Never say AI in any audio or text.

## Report (25 Nov, finished)
Sheet: https://uzandigitalofficial.github.io/ace-reels/picks/ (live after test render run 45655106215, success; page, 6 voice mp3, 6 music mp3 and LICENCES.md all return 200).
Script: new 16 to 19 second Stolen Valour script on the sheet. All audio at -16 LUFS, mp3 128k mono.
Voices: V1 Microsoft Ava Multilingual (top pick), V2 Microsoft Emma Multilingual, V3 Microsoft Sonia (GB), V4 Microsoft Leah (ZA), V5 Kokoro Heart, V6 Chatterbox calm (12 s, reads faster).
Music: M1 Gymnopedie No 1, M2 Sincerely, M3 Lightless Dawn, M4 Windswept, M5 Fresh Air, M6 Perspectives. All Kevin MacLeod, CC-BY 4.0, free for commercial use, ALL need the caption credit (exact line per track in picks/README.md and on the sheet).
Drop-in values: picks/README.md. Live brand settings untouched.
Decisions: V1 to V4 need engine "edge", not in render5.py ENGINES (kept hands off). Ready function in render/voice/eng_edge.py; README says the one line to register it. Edge-tts is Microsoft's free consumer service (grey area, not tested from a GitHub runner); Azure Speech is the clean paid equivalent. V5 and V6 work today. Old v7 outputs moved to picks/_raw/old_v7 (gitignored). pages.sh now copies only the page, LICENCES.md and final mp3s. Sound design and mixes dropped from the sheet (not in the v7b brief).
