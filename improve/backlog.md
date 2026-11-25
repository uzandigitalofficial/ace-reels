# Improvement backlog

Ranked, highest value first. One item per night. Each line: the change, then how to verify it. Mark done items like
`- [x] (2026-11-26) ...`. Every change must keep improve/rules.md and pass render/qa.py on sv-092, sv-008 and sv-001.

- [x] (2026-11-25) Beat-synced cuts and accents: scene cuts snap to a beat within 0.12 s of the voice cue, stamps, ticks, pops, underlines, cursor and progress line land on beats. Verify: qa beat_pct and the "beats:" log line.
- [x] (2026-11-25) Automatic scorecard render/qa.py wired into render5.py; hard fail keeps a reel off the feed. Verify: "qa:" line in the Actions log, meta json "qa".
- [ ] Better hook in the first 1.5 s: headline words land by frame 20 and the kicker pill on the first beat. Verify: still at 0.5 s and 1.5 s on the contact sheet shows the full hook; qa motion stays 20.
- [ ] Smoother easing on card entries: try a slightly softer drop spring (damping 15, stiffness 110) and compare overshoot. Verify: frame-by-frame sheet at 10 fps over the first 20 frames of a checklist scene shows no jump bigger than 40 px between frames.
- [ ] Kinetic emphasis on prices: R2,000 and R5,000 get a short underline swash and a beat-timed scale pulse after the slam. Verify: sv-008 price scene stills; qa off palette stays 0.
- [ ] Varied scene types so reels do not repeat: render/scenes.py avoids the same scene twice in a row and the same opener three reels running. Verify: count scenes over 9 consecutive rotation picks; qa scenes item at 20 for all three previews.
- [ ] Tighter CTA: typed message starts on the first word of the CTA and sends before the last word. Verify: CTA stills against word timings in props.json.
- [ ] Better music fit per pillar: brands "music" as {"pain": [...], "value": [...], "teach": [...], "default": [...]} (music_for already accepts it); calmer tracks for teach. Verify: log line "beats:" shows the pillar's track; listen to one per pillar.
- [ ] Raise beat alignment: let choose_offset also try off-bar beats when no strong beat gives 60 % of cuts on a beat. Verify: qa beat_pct over 60 on all three previews.
- [ ] Richer paper grain: add a second, very faint grain layer that drifts slowly (opacity under 0.06). Verify: qa off palette 0, motion 20, a still at 100 % zoom shows grain without banding.
- [ ] Caption polish: keep the hot word (price, free, Google, WhatsApp) up 4 frames longer. Verify: caption stills around the price word in sv-008.
- [ ] Breath lift tuning: music lifts in sentence gaps to 0.095; try 0.11 with a 0.08 s ramp. Verify: loudness of music-only gaps with ffmpeg astats, voice still clearly on top.
- [ ] Whoosh on beat: the cut swoosh peaks exactly on the snapped cut time. Verify: sfx.wav peak times vs props cuts within 20 ms.
- [ ] Stagger checklist rows so each tick lands on its own beat (no two ticks on one beat). Verify: tick frames vs props beats in a checklist scene.
- [ ] Footage polaroid: choose the clip window with the most motion in its first second. Verify: qa motion over footage seconds; still frames show content, not a blank top.
- [ ] Safe margins: keep every element 60 px from the sides. Verify: qa margins at 20 with the margin widened to 60 px.
- [ ] Hook scene variety: alternate kinetic and case file openers by pillar. Verify: openers over 9 rotation picks.
- [ ] End frame: the last 0.4 s holds the CTA still with a gentle settle (no fade to blank). Verify: last frame of each preview is the CTA card; qa blank check passes.
- [ ] Shorter long beats: any beat over 6 s gets a mid-beat accent (second card or stamp) so the picture changes every 2 to 3 s. Verify: qa motion, and per-second frame difference never below 0.5 for more than 2 s.
- [ ] Price card alignment: the "a month" serif baseline sits on the price baseline. Verify: zoomed still of sv-008 price scene.
- [ ] Icon grid: only show icons that match the words, fill the rest with one big explanatory icon. Verify: icon scene stills read as one idea.
- [ ] qa.py: add a loudness check (voice integrated loudness between -18 and -12 LUFS on the final mix). Verify: qa json "lufs" on three previews.
- [ ] qa.py: flag text smaller than 22 px at 1080 width as a soft penalty. Verify: soft item appears, score unchanged on current previews.

## From Uwais's Instagram shares, 25 Nov (see briefs/ig-ideas-25nov.md)
- [ ] 3D hero shots via Blender (Uwais asked: "What if we used Astra in blender..."): render a website-on-laptop or phone turn once on the laptop, cache as a short clip in assets/3d/, use as one scene type. Never render Blender inside the daily Action. Verify: one test reel with the clip, qa PASS, looks premium against rules.md.
- [ ] Sound design that never sounds cheap: at most 3 subtle real foley hits per reel (paper, pen, soft click), low level under the voice, no stock bleeps. Verify: by ear on the preview and voice still clearly on top.
- [ ] Later, after Instagram posting is stable: reformat each reel for YouTube Shorts and TikTok with its own hook, caption and cover text.
