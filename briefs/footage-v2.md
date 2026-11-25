# Brief: Reel footage library v2

Owner: Uwais (ACE Sovereign Holdings). Manager: ACE (Claude in the ACE project). Written 25 Nov 2026.

## Context
This repo (github.com/uzandigitalofficial/ace-reels) makes 3 Instagram reels a day on GitHub Actions with no Claude tokens:
render/render5.py (Chatterbox voice, Whisper word timings) feeds reel/ (Remotion 4.0.380, src/Reel.tsx). Footage is real
screen captures of our websites in assets/clips/*.mp4, recorded on this laptop by capture/capture.cjs (timecut, virtual time).
assets/clips.json lists the usable frame window of each clip; only listed clips are used. Make.com posts finished reels from the
gh-pages feed.xml to @stolenvalour.co.za. Test renders (workflow_dispatch with post=no) never post.

## The problem
1. CSS transitions and CSS animations do not advance under timecut's virtual time, so any section that fades or slides in on
   scroll records as blank. Only the top of each page is usable.
2. stolenvalour.co.za has a long intro (logo drawing) that runs on real time, so the capture never reaches the 3D hero.
3. Only 3 sites are usable, so reels will repeat visually.

## Do this
1. Research first (web search, GitHub): the best current way to record perfectly smooth 30 fps video of a web page that mixes
   WebGL, requestAnimationFrame, CSS transitions, CSS animations and scroll-triggered reveals. Compare at least: timecut/timesnap,
   stepping document.getAnimations() currentTime per frame alongside virtual JS time, Chrome HeadlessExperimental.beginFrame with
   --enable-begin-frame-control, CDP screencast at real time on the GPU, puppeteer-screen-recorder. Pick the approach that gives
   the smoothest, most complete footage. Write 10 lines on what you chose and why at the end of this brief.
2. Upgrade capture/capture.cjs (or replace it) so scroll reveals, CSS transitions and animations play correctly and smoothly.
   Keep it deterministic and smooth (no dropped or doubled frames).
3. Make stolenvalour.co.za capture its 3D hero: skip or wait out the intro, whichever works.
4. Recapture, mobile (432x932 at 2.5x) and desktop (1600x1000 at 1.2x), 10 to 14 seconds each, gentle eased scroll:
   obsidian-crown.netlify.app, stolenvalour.co.za, saxonwold.netlify.app/?brand=randlord, kingdom-shine.netlify.app.
   Move replaced clips to assets/clips_old/ (never delete anything).
5. Check every clip with ffmpeg contact sheets (look at them), then set honest usable windows in assets/clips.json.
   Drop any clip that is mostly black, blank or loading.
6. Commit and push. Run one test render: gh workflow run reel.yml -f id=sv-006 -f post=no. Wait for it, pull the mp4 from the
   gh-pages branch, make a contact sheet, look at it, and fix anything that looks wrong.
7. Append a dated 5-line note to C:\Users\muwai\OneDrive\Desktop\jarvis-project\ace-context\HANDOFF.md.

## Rules
- No em dashes or en dashes in anything you write. Plain words.
- Never delete files: move to a _to_delete or clips_old folder.
- Do not change Make.com, the posting setup, the schedule, the script bank, or any other repo or website.
- Keep every video under 5 Mbps (Instagram limit through Make).
- Do not spend money or sign up for anything.

## Research: what I chose and why
1. timecut/timesnap only fake JS time (rAF, Date, timers, video). Its README says CSS transitions and animations will not render as intended, which is what we saw.
2. Seeking document.getAnimations() to the virtual clock every frame (the approach Replit and others describe) fixes exactly that gap, and works on top of timecut.
3. HeadlessExperimental.beginFrame with --enable-begin-frame-control is the most deterministic, but it only works in chrome-headless-shell, not new headless Chrome.
4. That mode is also flagged experimental and deprecated, and in practice runs WebGL on software (SwiftShader), so our 3D heroes would be slow and look different.
5. CDP screencast at real time and puppeteer-screen-recorder use the real GPU but drop or double frames whenever the machine stalls, so they fail the "no dropped frames" rule.
6. Choice: keep timecut's virtual clock and GPU Chrome, and add a Web Animations seeker (capture/virtual.cjs) that pauses every CSS transition or animation and sets it to virtual time after each frame.
7. Debugging stolenvalour.co.za found three timeweb bugs that I patch in memory at load time: video.play() returned undefined, a throwing rAF callback dropped every other callback that frame, and waits for off-page video "seeked" froze rAF forever.
8. The biggest find: the bundled Puppeteer 2 treats the screenshot clip as document coordinates, so every capture stayed pinned to the page top once it scrolled. That is why everything below the fold recorded blank in v1, not only the CSS reveals.
9. Skipped intro time is now stepped frame by frame (maximumAnimationFrameDuration 33 ms), so GSAP and rAF intros really finish before recording.
10. Result: deterministic 30 fps, one virtual frame per output frame, real GPU WebGL, CSS reveals and 3D heroes in the same take.
Sources: github.com/tungs/timecut, github.com/tungs/timesnap, replit.com/blog/browsers-dont-want-to-be-cameras, groups.google.com/a/chromium.org/g/headless-dev (BeginFrameControl threads), posthog.com/blog/multimodal-models-need-video.

## Report
(Write the result here when done: what changed, what is now usable, what is still weak.)
