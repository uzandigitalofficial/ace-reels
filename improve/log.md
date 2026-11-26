# Improvement log

One dated entry per change: what changed, why, before and after numbers (render/qa.py on sv-092, sv-008, sv-001).

## 2026-11-25: beat sync, second pace pass, qa scorecard (beats-improve-v8)
- What: render/beats.py (librosa beat grid cached in assets/music_beats.json; music start offset so a strong beat is on frame 1,
  a phrase change near the CTA when the track has one, and as many cuts as possible near a beat); scene cuts snap to a beat within
  0.12 s of the voice cue without cutting a word; stamps, ticks, crosses, pins, wax seal, price slams, underline swashes, chat
  bubbles, main cards and text cursors land on beats; the progress line nudges on every beat; music lifts from 0.06 to 0.095 in
  breaths between words. Pace: a second, smaller time-stretch pass when Chatterbox reads too fast. New render/qa.py wired into
  render5.py (meta "qa"; a hard fail sets "qa_fail", which feed.py and post_ig.py skip).
- Why: brief beats-improve-v8; Chatterbox read at 193 to 206 wpm and one 0.86 stretch left reels at 164 to 179 wpm.
- Before (Engine 6.1, earlier Chatterbox render of sv-092 with only one stretch pass): qa 90/100, 170 wpm, 75 % of cuts on a beat.
- After (tmp/final, Chatterbox voice):
  sv-092 20261125-1645: PASS 95/100, 21.3 s, 3.84 Mbps, 160 wpm, silence 0.31 s, off palette 0 %, beats 75 % of 4 cuts
  sv-008 20261125-1651: PASS 95/100, 25.1 s, 3.92 Mbps, 161 wpm, silence 0.32 s, off palette 0 %, beats 75 % of 4 cuts
  sv-001 20261125-1656: PASS 100/100, 20.1 s, 3.89 Mbps, 161 wpm, silence 0.33 s, off palette 0 %, beats 100 % of 4 cuts
- Sanity check of the palette detector: the old coral render tmp/final/20261125-1208-sv-092.mp4 fails with 17 % off palette.

## 2026-11-26: clean scene exits (reel/src/Reel.tsx SceneWrap)
- What: the outgoing scene's opacity now runs on frames (1 to 0 from len-4 to len+4) instead of on the eased slide value, which
  kept it near full opacity for most of the 12 frame overlap. The slide and rotation are unchanged.
- Why: in the last 3 posted reels (sv-003, sv-004, sv-005) the old headline sat on top of the new one during cuts; worst at
  sv-004's CTA, where "Your domain, your name" covered "WhatsApp 065". The top backlog item (hook by frame 20) was already met.
- Before (posted meta qa): sv-003 100, sv-004 100, sv-005 95 (avg 98.3), all PASS.
- After (run 45893088746, sv-004 test 20261126-2050): PASS 100/100, 26.18 s, 3.71 Mbps, 160 wpm, silence 0.304 s, off palette 0 %,
  beats 100 % of 4 cuts. Frames every 2 around the CTA cut: old scene fades away as the new headline lands, one faint frame left.
- Note: standalone qa.py on a gh-pages mp4 without props flags polaroid footage as off palette (sv-004 at 13.8 s); added to backlog.
