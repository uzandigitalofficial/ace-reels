# Brief: Voice and music v7 (pick sheet for Uwais)

Owner: Uwais (ACE Sovereign Holdings). Manager: ACE. Written 25 Nov 2026, 14:00.

## What Uwais said
On the new light paper reels: "Much better, needs the most realistic possible human voice, speaking well and clear, the music is
terrible." Earlier: he wants the smoothest, prettiest woman's voice; it must never sound like AI; never say "made with AI".

## Context
Repo C:\Users\muwai\ace-reels. Reels render on GitHub Actions (ubuntu, CPU only, no GPU), 3 a day, no Claude tokens.
Current voice: Chatterbox (render/render5.py, tts_chatterbox) with faster-whisper word timings for captions. Current music:
6 Mixkit tracks listed in brands/stolenvalour.json (he hates them). Another session (design-v6) is editing reel/src and
render5.py right now: do NOT edit those files. Work only in new files under render/voice/, render/music/ and picks/.

## Do this
1. Research first (web, GitHub, Hugging Face, current 2026 TTS leaderboards and blind tests such as TTS Arena):
   which voices sound most like a real, warm, clear woman speaking English. Cover at least: Gemini 2.5 TTS (Flash and Pro,
   free tier via Gemini API key), Microsoft neural voices through edge-tts (including the Multilingual and HD voices),
   Chatterbox tuned (lower exaggeration, other settings), Kokoro, Higgs Audio v2, Orpheus, Dia, F5-TTS, IndexTTS2,
   VibeVoice, Sesame CSM, ElevenLabs. For each: realism, clarity, licence for commercial use, cost, whether it runs on a
   CPU-only GitHub runner or needs a GPU or an API key, speed. Write the table at the end of this brief.
2. Generate the SAME script with every option that can run here without a new account or a key you do not have
   (for example edge-tts voices, Chatterbox with 3 settings, Kokoro, anything on a free public Hugging Face Space that
   allows it). Use this script: "Are you on Google? Search for your business like a customer would. If you can't find
   yourself, neither can they. Set up your free Business Profile tonight." Make at least 8 candidate WAV or MP3 files,
   normalised to the same loudness (-16 LUFS). For options that need a key (Gemini, ElevenLabs), say exactly what Uwais
   would need to do and the cost; do not sign up for anything.
3. Music: research what top informative reels use under voice (often very light music or none, plus subtle sound design:
   soft whooshes on transitions, paper and pop sounds, clicks, a gentle riser). Find 6 genuinely good, free, commercially
   usable background tracks from reputable libraries with clear licences (for example Pixabay Music, Free Music Archive CC0
   or CC-BY with attribution handled, YouTube Audio Library if downloadable without login), favouring calm modern minimal,
   lo-fi or soft piano that sits under a voice. Also build a sound-design-only option (whoosh, paper, pop, click effects
   from a free licence library such as Pixabay or Kenney, CC0). Record source URL and licence for every file.
4. Make a pick sheet: picks/index.html with an audio player for every voice (labelled V1, V2, ...) and every music option
   (M1, M2, ... plus "no music" and "sound design only"), each with one short line on what it is. Also make 3 short mixes:
   the best 3 voices over the best music option at the right level (voice clearly on top, music around -24 dB under it).
   Publish the pick sheet to the gh-pages branch at /picks/ (add files without disturbing reels/, index.html or feed.xml;
   clone gh-pages, add picks/, commit, push), and check https://uzandigitalofficial.github.io/ace-reels/picks/ loads.
5. Write the result here and append a dated 4-line note to
   C:\Users\muwai\OneDrive\Desktop\jarvis-project\ace-context\HANDOFF.md.

## Rules
- No em dashes or en dashes. Plain words. Never mention AI in any audio.
- Only content with licences that allow commercial use on Instagram. Record every licence.
- Do not sign up, spend money, or use any key or password. Do not edit reel/src or render/render5.py.
- Never delete files; move to _to_delete.

## Report
Done 25 Nov 2026. Pick sheet: https://uzandigitalofficial.github.io/ace-reels/picks/ (every source and licence: /picks/LICENCES.md).

### Top recommendation
V1, Microsoft Ava Multilingual, over M1 (Gymnopedie No 1) with light sound design. That is MIX1 on the sheet.
- It speaks at 177 words a minute, which is natural narration pace. Its pitch is warm and varied (median 201 Hz). A Whisper transcription check got every word right.
- It is free, needs no key, runs on the GitHub runner in seconds and gives word timings for captions.
- The current Chatterbox setup (V9) rushes at 234 words a minute. Chatterbox has no speed control, and the rush is a big part of why it sounds made. It also takes about 85 s of CPU per 7 s line.
- Chatterbox Turbo (V12) is the best of the local models: 182 words a minute, bright female voice, about 6x faster than the original on CPU. It is the pick if Uwais wants to stay fully self-hosted.
- The most human option overall is Gemini TTS, voice Sulafat, Achernar or Vindemiatrix. It needs a key, so it is not on the sheet (see below).
- Music: keep it at about 24 dB under the voice. If he dislikes all 6 beds, use "Sound design only".

### What each option is (all 16 voices read the same script at -16 LUFS, within 0.4 dB)
| ID | What | Pace (words a minute) |
|---|---|---|
| V1 | Microsoft Ava Multilingual (edge-tts), US, warm, expressive | 177 |
| V2 | Microsoft Emma Multilingual, US, bright, chatty | 173 |
| V3 | Microsoft Ava (older model) | 185 |
| V4 | Microsoft Jenny, US, even | 153 |
| V5 | Microsoft Aria, US, newsreader | 147 |
| V6 | Microsoft Sonia, British | 156 |
| V7 | Microsoft Libby, British, soft | 139 |
| V8 | Microsoft Leah, South African | 140 |
| V9 | Chatterbox, current reel settings (exaggeration 0.62, cfg 0.42) | 234 |
| V10 | Chatterbox, calm (0.40 / 0.50) | 215 |
| V11 | Chatterbox, warm slow (0.30 / 0.30, temperature 0.6) | 204 |
| V12 | Chatterbox Turbo, built-in voice | 182 |
| V13 | Kokoro Heart (the current backup) | 194 |
| V14 | Kokoro Bella | 185 |
| V15 | Kokoro Nicole, breathy | 120 |
| V16 | Kokoro Emma, British | 207 |

- M1 to M6: Kevin MacLeod (incompetech.com), CC-BY 4.0. Each is a 30 s excerpt at -16 LUFS:
  - M1 Gymnopedie No 1
  - M2 Sincerely
  - M3 Lightless Dawn
  - M4 Windswept
  - M5 Fresh Air
  - M6 Perspectives
- How the 6 were chosen: 21 tracks were measured (render/music/score.py). These 6 have the least energy in the 1 to 4 kHz speech band, few note attacks and a steady level.
- "No music" is V1 alone.
- "Sound design only" is V1 plus effects placed on the voice's own word timings: a soft whoosh in, a page flip on "Search", a pop on "If", and a riser and click into "Set up".
- MIX1, MIX2, MIX3: V1, V12 and V2 over M1 with the same sound design. Music sits 24 dB under the voice (LUFS-integrated).

### Research table
| Option | Realism | Clarity | Licence / commercial | Cost | CPU runner? | Key | Speed |
|---|---|---|---|---|---|---|---|
| Gemini TTS (3.8 Flash, 3.1 Flash preview, 2.5 Pro preview) | Top 10 on the Artificial Analysis arena (3.8 Flash Elo about 1285) | Very good | Outputs usable commercially. Free-tier data is used by Google for training | Free tier, small daily quota (reports of about 10 requests a day on some models) | Yes, it is an API call | Yes | Seconds |
| ElevenLabs (v4) | Number 1 on the arena (about 1345) | Best | Commercial use from the Starter plan only. Free plan is non-commercial with attribution | About $5 to $6 a month | Yes, API | Yes | Seconds |
| Microsoft neural via edge-tts (Ava, Emma Multilingual) | Good, clearly below the top tier | Very good | Grey area: an unofficial Edge Read Aloud endpoint. Clean route is Azure Speech (free 0.5M characters a month, key needed) | Free | Yes | No | Faster than real time |
| Microsoft Dragon HD voices | Better than standard | Very good | Azure only, not reachable through edge-tts | Azure pricing | API | Yes | Seconds |
| Chatterbox (original) | Arena about 1021 | Good, but rushes | MIT, inaudible watermark | Free | Yes, but slow: about 12x real time measured here | No | 85 s for a 7 s line |
| Chatterbox Turbo (350M) | Newer, more natural pacing | Good | MIT | Free | Yes: about 6x real time measured here | No | 56 s for a 9 s line |
| Kokoro-82M | Arena about 1061, top small model | Very good, slightly smooth | Apache 2.0 | Free | Yes, about 1.2x real time here | No | 12 s for 9 s |
| Higgs Audio v2 / v3 | v3 about 1036 | Good | Boson community licence (v2). v3 is non-commercial research | Free | Heavy (3B to 4B) | No | Below real time |
| Orpheus 3B | Good | Good | Apache 2.0 code on a Llama base | Free | Poor, about 40x real time on CPU | No | Very slow |
| Dia 1.6B / Dia2 | Dialogue-focused | Fair | Apache 2.0 | Free | Poor | No | Slow |
| F5-TTS | Good clone quality | Good | Weights CC-BY-NC: not allowed commercially | Free | Slow | No | Slow |
| IndexTTS2 | Good | Good | bilibili model licence, commercial terms unclear | Free | Slow | No | Slow |
| VibeVoice 1.5B | About 955 | Fair | Not verified, check before use | Free | Heavy | No | Slow |
| Sesame CSM-1B | Conversational | Good | Apache 2.0 | Free | Poor | No | Slow |
| Fish Audio Drama 3 (2026 newcomer) | Top open model, about 1277 | Very good | Free commercial use under $500k revenue, credit needed | Free | No, needs about 48 GB of GPU memory | No | GPU only |

Sources: artificialanalysis.ai/text-to-speech/leaderboard, aistudio.google.com/docs/speech-generation, huggingface.co/ResembleAI/chatterbox-turbo, huggingface.co/hexgrad/Kokoro-82M, huggingface.co/bosonai/higgs-audio-v3-tts-4b, github.com/rany2/edge-tts, learn.microsoft.com (Azure HD voices), elevenlabs.io pricing.

### Options needing a key (nothing signed up)
- **Gemini, free:**
  1. Go to aistudio.google.com and sign in with Google.
  2. Click Get API key, then Create API key. No card is needed.
  3. Add the key as GitHub secret GEMINI_API_KEY.
  - Cost R0 on the free tier.
  - Catch 1: the daily quota is small, so send one request per reel.
  - Catch 2: Google may use free-tier audio for training.
  - The paid tier costs cents per reel.
- **ElevenLabs:** Starter plan, about $5 to $6 a month, for commercial rights. Then add the API key as a GitHub secret.
- **Azure Speech (clean licence for the V1 to V8 voices):** a free Azure account (card required for signup) gives 0.5M characters a month free.

### Music research
- Under informative voiceover, guides converge on music 18 to 24 dB under speech: W3C G56 says 20 dB, Descript and Soundstripe give similar figures.
- Use short sound effects only on transitions and reveals.
- Pixabay blocks scripted downloads (403), so its tracks could not go into an automated pipeline. Free Music Archive needs JavaScript or a login. Mixkit was excluded.
- Incompetech gives direct MP3 links under CC-BY 4.0. The caption must carry: "<Title>" Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution 4.0 License. http://creativecommons.org/licenses/by/4.0/
- Sound effects:
  - Kenney Interface Sounds and RPG sounds, CC0
  - starninjas page flips, CC0
  - a whoosh and riser made from scratch in code (render/music/build_picks.py), so they need no licence

### Decisions made
- Every free public Hugging Face Space ran out of its anonymous GPU quota after 3 clips. Using Uwais's HF token would break the no-keys rule. So Chatterbox, Turbo and Kokoro were rendered locally on CPU, the same way the runner does it.
- The 3 Space-made Chatterbox clips are in picks/_raw/_to_delete.
- Higgs, Dia, CSM, IndexTTS2 and F5 were not generated. Reasons: Space quota, and F5 / IndexTTS2 licences do not allow commercial use.
- No reel code was touched: reel/src and render5.py were left alone.
- New code is in render/voice/ (gen_edge, gen_local, gen_spaces, score) and render/music/ (fetch, fetch_paper, score, build_picks, sheet_html).
