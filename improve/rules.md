# Locked rules for the nightly improver

These come from looks and briefs Uwais approved (Engine 6.1, commit 2cb5d2d, "Perfect like this"; briefs/design-v6.md,
briefs/design-v6b.md, briefs/beats-improve-v8.md). The nightly improver may never break any of them. If a backlog item
needs a rule broken, skip the item and write why in improve/log.md.

## Look
- Cream paper background #F2EBDD with the paper texture (assets/paper/paper-cream.jpg). Light, warm, paper-like. Never a dark background.
- Navy ink #14213D for headlines, body text, icons, outlines, the progress line and the italic highlight words. Lighter navy
  #3A4A6B for secondary text. Card fills white #FFFFFF or light cream #FBF7EE; sticky notes and kraft stay cream tones.
- No other colour, except inside realistic UI mock-ups where it belongs to the real thing (muted WhatsApp green #4F9B73 and
  bubble #DCF3D6, Google map pin), kept muted. No coral, no mint, no glow, no particles, no grid.
- Colours come from brands/stolenvalour.json "colors" (applyPalette). Do not hard-code new colours in scenes.
- Type: Inter Tight heavy grotesk headlines, Instrument Serif italic for the one accent word and captions, Anton only for stamps
  and collage labels. No mono font anywhere.
- No template look: no slide counter ("01 / 05"), no numbered or mono labels, no "//", no underscores, no "fig. 0x", no
  "STOLEN VALOUR" strip. Top of frame holds only the navy progress line and a small serif SV wordmark.
- Site footage only inside a polaroid or a card, never full screen or blurred behind everything.
- Paper physics for objects: spring drop with a little overshoot, settling rotation, soft shadow plus halftone offset shadow.
  Smooth, no jumps, 30 fps, motion in every second.

## Voice and timing
- Voice speaks from the first frame to the last. No music-only intro, no silent end card, no silent stretch over 0.4 s inside
  the voice (qa.py hard fail). The CTA card is on screen while the CTA is spoken. Video = voice + about 0.4 s tail.
- Every scene's timing comes from the voice's word timestamps. Never cut a word to hit a beat or a length.
- Natural pace 150 to 165 words a minute; pauses between sentences 0.15 to 0.3 s.
- Captions stay word-synced: one or two words at a time, big italic serif, low and centred.
- Music always sits ducked under the voice (voice clearly on top). Beat sync is subtle: cuts and small accents only, not a music video.
- Keep the voice engine and music selection pluggable: tts() and ENGINES in render/render5.py, music_for() for music. Do not
  change which voice engine is used; that is Uwais's call.

## Words
- No em dashes or en dashes anywhere, on screen or in scripts. Plain South African English.
- Never say AI, "made with AI" or similar. Never name Uwais.
- Never invent results, clients, reviews, statistics or guarantees. Prices only R2,000 Studio and R5,000 Showroom as in
  brands/stolenvalour.json. Prices slam in; they are never counted or rolled.
- CTA stays honest: "DM us the word SITE" or WhatsApp 065 027 6518 for a free homepage mock-up, no obligation.

## Delivery limits
- Length 15 to 60 s (aim 20 to 30 s). Video bitrate under 4.5 Mbps (render at 4M). 1080x1920, 30 fps.
- render/qa.py must pass (exit 0) on every reel. A hard fail keeps the reel off the feed and off Instagram.

## How the improver works
- One small change per night, taken from the top open item of improve/backlog.md. Render sv-092, sv-008 and sv-001 before
  and after, run qa.py on both, and keep the change only if no hard check fails and the soft score does not drop.
- Log every change in improve/log.md (date, what, why, before and after numbers). Mark the backlog item done with the date.
- Never delete files (move them to _to_delete/). Never touch picks/, render/voice/, render/music/, the schedule, posting,
  Make.com, secrets or other repos. Never push a change that fails qa.py.
