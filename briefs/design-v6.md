# Brief: Reel Engine 6, informative 2D motion design

Owner: Uwais (ACE Sovereign Holdings). Manager: ACE. Written 25 Nov 2026.

## What Uwais said
"We don't even have to be making 3D stuff, we can make 2D, as long as voice, animations, everything is smooth and beautiful.
We want it informative too." Earlier: the old reels were "slop"; he wants smooth, beautiful, fully animated start to end,
engaging formats, a voice that does not sound like AI, and never anything like "made with AI".

## Context
Repo C:\Users\muwai\ace-reels (github.com/uzandigitalofficial/ace-reels). Read README-level files first: render/render5.py,
reel/src/Reel.tsx (Remotion 4.0.380), content/stolenvalour.json (90 scripts), brands/stolenvalour.json, .github/workflows/reel.yml,
assets/clips.json. Reels render on GitHub Actions 3 a day with no Claude tokens; Make.com posts gh-pages feed.xml to
@stolenvalour.co.za. Voice is Chatterbox with faster-whisper word timings (keep it, tune it if it helps). Test renders:
gh workflow run reel.yml -f id=<id> -f post=no (never posted; visible at https://uzandigitalofficial.github.io/ace-reels/).
Another session may have just updated capture/ and assets/clips*; do not undo its work. git pull --rebase before every push.

## Do this
1. Research first (web search, YouTube/Instagram write-ups, Remotion showcase, GitHub): what makes the best informative
   2D motion-graphic reels for small-business audiences (explainer pacing, hook in the first second, one idea per beat,
   kinetic type, animated UI mockups, icon animation, transitions, sound design, caption styles, length 15 to 30 s).
   Note 10 concrete principles at the end of this brief with sources.
2. Build a 2D scene library in reel/src: each script beat picks the scene that explains it best, all fully animated,
   smooth (spring and eased motion, no jumps), on-brand (black, white, mint #B8F2D6 accent, Inter Tight and Instrument Serif).
   At least: kinetic type statement; animated checklist with ticks; Google search result mock-up (a business appearing or
   not appearing); WhatsApp chat mock-up (customer asks, business replies); phone browser mock-up with a simple site being
   built block by block; before/after split (old slow site vs clean site, drawn in 2D, no real third-party brands);
   price card (R2,000 / R5,000 and what is included, only facts from brands file and content); timeline (day 1 to day 7);
   icon grid (lucide-react icons animating in). Site footage clips may still appear as one scene type, but 2D scenes lead.
3. Make the script bank informative: add a "teach" pillar of 30 new scripts that give a genuinely useful tip to a small
   business owner about websites, Google, WhatsApp enquiries, booking, trust (with each tip true and general, no invented
   statistics or percentages, no named real clients, no guarantees). Each script beat gets a "scene" field naming the scene
   type. Keep the existing 90, add scene fields to them too. Same JSON shape plus "scene" per beat.
4. Keep captions word-synced, keep the hook chip and CTA card, keep music under voice, keep under 5 Mbps.
5. Render 3 test reels (one teach, one pain, one value) with post=no, pull the mp4s, make contact sheets, look at them
   frame by frame, and fix anything ugly, jerky, cramped or unreadable. Repeat until they are genuinely beautiful.
6. Commit, push, and append a dated 6-line note to C:\Users\muwai\OneDrive\Desktop\jarvis-project\ace-context\HANDOFF.md.

## Rules
- No em dashes or en dashes anywhere. Plain words. South African English.
- Never claim results, clients, reviews or statistics that are not real. Prices only from brands/content files.
- Never mention AI in a reel. Never name Uwais.
- Never delete files: move to _to_delete.
- Do not change Make.com, the schedule, posting, or any other repo or website. Do not spend money or sign up for anything.

## Research: 10 principles for informative 2D reels (25 Nov 2026)
1. Show the payoff in the first second: a bold visual change and the result first, the how after. Hook text is on screen from frame 1.
   (clarigital.com/codex/social-media/instagram-reels-strategy, talhaaslan.com/en/blog/instagram-reels-hook-why-first-3-seconds-matter)
2. Design for sound off: on-screen headline restates the spoken point, captions carry the rest. (brandghost.ai/blog/posts/instagram-reels-best-practices-for-creators)
3. Change the picture every 2 to 3 seconds, no dead pauses, value inside the first five seconds. (zocialone.ai/blog/instagram-reels-strategy-hook-retention-cta)
4. One idea per beat: one claim, one visual, one headline. Practitioner consensus, matches the pacing advice above.
5. Captions 1 to 4 words on screen; word by word works for punchy lines, so keep scripts short and plain. (zellahq.com/blog/best-caption-styles-for-short-form-video, kreateflo.com/blog/can-word-by-word-caption-animation-keep-viewers-hooked)
6. Prove claims with animated UI mock-ups (chat, search result, phone screen) rather than telling. OpenMontage's animation pipeline and Locomotion's Before and After / Step Explainer templates work this way. (github.com/calesthio/OpenMontage, github.com/locomotion-pro/locomotion)
7. Sound is punctuation: one soft whoosh per cut, music low under the voice, never a whoosh on every element. (creatorsfx.in/blog/best-sound-effects-for-reels-and-shorts)
8. Length: sources disagree (15 to 30 s vs 30 to 60 s), so stay around 20 to 30 s and let the Insights retention curve decide. (feedhive.com/blog/instagram-reels-length, moonb.io/blog/instagram-reel-length)
9. Use the retention graph as the edit loop: find the second viewers drop and fix that beat first. (zocialone.ai, as above)
10. Give paper objects weight: spring drop-ins with a little overshoot, a settling rotation, a soft shadow plus a halftone offset shadow; editorial collage is a current trend. (kittl.com/blogs/graphic-design-trends-2027, remotion.dev/docs/spring)
OpenMontage (AGPL-3.0) is an agent-orchestrated pipeline (research, script, scene plan, assets, compose) with Remotion as renderer. Borrowed ideas only, no code: a per-beat scene plan in data, data-driven scene components, word-level captions.

## Report (25 Nov 2026)
Built (Reel Engine 6, light paper style per the 13:30 direction):
- reel/src/kit.tsx: palette (paper, ink navy, coral, tick green), Inter Tight / Instrument Serif / JetBrains Mono / Anton, paper-physics
  object (spring drop, settling rotation, soft shadow plus halftone offset shadow, idle drift), headline with one coral italic serif accent
  word (*word* markers or auto), typed mono section labels, ticks, stamps, pins, tape, Lucide icons drawn on stroke by stroke.
- reel/src/scenes.tsx, 12 scenes: kinetic statement, case file collage (kraft envelope, wax seal, CASE FILE label, roaming magnifier),
  checklist card, search result (you found / you nowhere), WhatsApp chat (late reply vs instant link reply), phone site built block by block
  with pinned labels, before/after (no real brands), price card(s) from brands file only, day 1 to 7 timeline, icon grid, site footage only
  inside a pinned polaroid on cork, CTA (DM us SITE or WhatsApp 065 027 6518, free and no obligation).
- reel/src/Reel.tsx: warm or cool paper background (no dark, no glow, no particles, no grid), scenes overlap 12 frames and slide out
  with a rotation, captions one or two words in big italic serif low centre synced to Whisper words, hook chip, progress bar, music
  under voice, plus a quiet generated paper swoosh and tap per cut (sfx.wav).
- render/scenes.py picks a scene, mood and niche per beat; every beat in content/stolenvalour.json now has "scene". render/teach_bank.py
  adds the "teach" pillar: sv-091 to sv-120 (30 general, true tips; no stats, names or guarantees). Bank is now 120 scripts.
- brands/stolenvalour.json: coral accent, phone, handle and a "plans" block with only facts already in the content (R2,000 studio,
  R5,000 showroom). render/render5.py: engine 6, --preview mode (fake word timings, no TTS) for laptop checks, scene-aware minimum
  beat lengths so chats and ticks finish. Keeps the other session's clip-window change. render/sheet.py and render/preview.py make
  contact sheets and stills.
Decisions: lucide-react could not be installed here, so Lucide paths are inlined (ISC) which also allows the draw-on effect. Prices
never count up (a rolling number briefly showed figures that are not our prices); they slam in. Teach reels use the cool paper.
Test reels (local preview renders, no voice, captions on fake timing, music and sfx on; 3.8 to 3.9 Mbps, 23 to 28 s):
  tmp/final/20261125-1208-sv-092.mp4 (teach), tmp/final/20261125-1209-sv-001.mp4 (pain), tmp/final/20261125-1210-sv-008.mp4 (value).
Still weak / not done:
- This session could not run git add/commit/push or gh (permission prompts cannot be answered in a non-interactive run), so nothing is
  committed and the GitHub post=no test renders with the real Chatterbox voice were not run. Run:
    git add reel/src reel/package.json reel/package-lock.json render brands content assets/paper briefs/design-v6.md
    git commit -m "Engine 6: light paper 2D scene library, teach pillar, scene per beat"; git pull --rebase; git push
    gh workflow run reel.yml -f id=sv-092 -f post=no   (then sv-001 and sv-008)
- Caption timing is only proven with fake timings; check one voiced render for sync.
- Footage clips are dark at the top in some windows; the polaroid works but a lighter clip window would look better.
- Icon grid is the least explanatory scene; checklist and chat scenes carry the teaching best.


## STYLE DIRECTION (added 13:30, overrides anything above; Uwais called the current reels "honestly shit")
He sent three references. Match their level and feel, then make it our own:
1. nick_saraev reel (instagram.com/reel/Dd_tRbkP0qO): clean light cards (e.g. a white GitHub repo stats card, "62.3k stars")
   filling the top half, and one big italic serif caption word at a time in the lower third ("completely", "all run").
   Note: it shows the repo calesthio/OpenMontage ("AI production studio"); research it and use what helps.
2. ai.byarsh carousel (instagram.com/p/Df1A60SCAEd): warm off-white background, navy heavy sans headline with one coral
   italic serif accent word ("Built into *every* reel"), a coral pill label ("THE SKILL"), a white rounded card holding
   rows with green tick circles, a bold line and a grey sub-line each, small footer brand text.
3. adilet.fndr reel (instagram.com/reel/De_3hwXIBYi): editorial paper collage. Textured surfaces (cork board, light paper
   with halftone dots), real-looking objects drawn in code (polaroids pinned with pins, a yellow sticky note, an envelope
   with a red wax seal and a "CASE FILE / HOW?" label, a magnifying glass), small mono section labels like "// 02 - the
   roadmap", heavy condensed headline with a red accent word ("GET CLAUDE CODE"), halftone drop shadows, an app icon card.

Rules for the new look:
- LIGHT, warm, paper-like backgrounds. No dark backgrounds, no green glow, no floating particles, no grid. Remove the
  ambient green light completely (Uwais: "no idea where that random green shit in the bg came from").
- Palette: paper #F4F1EA (and a cool variant #F2F1F8), ink navy #13162B, accent coral red #E5533D, tick green #22A06B,
  card white with soft shadow. Mint is retired.
- Type: heavy grotesk for headlines (Inter Tight 800/900 or a condensed like Anton/Oswald for collage scenes), italic serif
  accent word (Instrument Serif), mono for section labels (JetBrains Mono or IBM Plex Mono).
- Captions: one or two words at a time, big italic serif, centred low, synced to the voice. No pill highlight boxes.
- Every beat is a crafted 2D scene: cards, checklists, collage objects, UI mock-ups (Google result, WhatsApp chat, site
  building block by block), price card, day 1 to 7 timeline. Objects drop in with paper physics (slight rotation, spring,
  soft halftone shadow). Smooth, no jumps, 30 fps, fully animated start to end.
- Site footage, if used at all, only inside a polaroid or a card, never as a blurred full-screen background.
- CTA stays honest: "DM us SITE" (Instagram) or WhatsApp 065 027 6518 for a free homepage mock-up.
