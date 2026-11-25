"""Reel Engine 6.1: cream and navy 2D paper scenes in Remotion, voiced from the first frame to the last, word-synced captions,
music ducked under the voice. Token-free.
Every scene's timing comes from the voice: each beat starts on its first spoken word (faster-whisper word timestamps) and the
reel ends 0.4 s after the last word. Pauses between beats are 0.15 to 0.3 s; long pauses inside a take are shortened; the take
is gently time-stretched into 150 to 165 words a minute.
The voice engine is pluggable: brands/<brand>.json "tts": {"engine": "chatterbox"} picks a function from ENGINES.
Usage: python render/render5.py --brand stolenvalour [--id sv-001] [--out out] [--no-voice] [--preview]
  --preview  no TTS: fake word timings at the target pace so layout can be checked on a laptop without the voice model.
"""
import argparse, datetime, glob, json, os, pathlib, random, re, shutil, subprocess, sys, urllib.request
import numpy as np, soundfile as sf

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "render"))
import scenes as S  # noqa: E402
import beats as B  # noqa: E402

REEL = ROOT / "reel"
PUB = REEL / "public"
SR = 24000
LEAD, TAIL = 0.04, 0.4          # voice starts on frame 1; the video ends 0.4 s after the last word
GAP_SENT, GAP_SOFT = 0.21, 0.15  # pause between beats: after a full stop or question mark, else a breath
MAX_PAUSE, KEEP_PAUSE = 0.32, 0.24  # any pause inside a take longer than MAX_PAUSE is cut down to KEEP_PAUSE
WPM_LO, WPM_HI, WPM_GOAL = 150, 165, 158
DIG = "oh one two three four five six seven eight nine".split()
# no-voice dev mode only: how long a beat stays up
MIN_MUSIC = {"price": 3.6, "timeline": 3.6, "whatsapp": 3.6, "sitebuild": 3.4, "google": 3.4, "beforeafter": 3.4, "checklist": 3.2, "casefile": 3.0, "cta": 4.0}


def write_sfx(path, segs, total, sr=44100):
    """Quiet paper sound design: a soft swoosh on every cut and a light tap when the new scene lands."""
    rng = np.random.default_rng(7)
    out = np.zeros(int((total + 1) * sr), np.float32)
    for i, s in enumerate(segs):
        cut = max(0.0, s.get("cut", s["start"] - 0.12)) if i else 0.0
        if i:
            n = int(0.42 * sr); x = rng.normal(0, 1, n).astype(np.float32)
            env = np.sin(np.linspace(0, np.pi, n)) ** 2.2
            y = np.zeros(n, np.float32); acc = 0.0
            for k in range(n):  # one-pole low-pass sweeping down: air moving past paper
                a = 0.05 + 0.25 * (1 - k / n); acc += a * (x[k] - acc); y[k] = acc
            st = int(max(0, cut - 0.3) * sr); out[st:st + n] += y * env * 0.5
        n = int(0.09 * sr); tt = np.arange(n) / sr
        tap = (np.sin(2 * np.pi * 120 * tt) * np.exp(-tt * 55) * 0.35 + rng.normal(0, 1, n) * np.exp(-tt * 140) * 0.05).astype(np.float32)
        st = int((cut + 0.32) * sr); out[st:st + n] += tap[: max(0, min(n, len(out) - st))]
    out = np.clip(out, -0.9, 0.9)
    sf.write(path, np.stack([out, out], 1), sr, subtype="PCM_16")


def speakable(t):
    t = re.sub(r"\b0(\d{2}) ?(\d{3}) ?(\d{4})\b", lambda m: ", ".join(" ".join(DIG[int(c)] for c in g) for g in (("0" + m.group(1)), m.group(2), m.group(3))), t)
    t = re.sub(r"R ?(\d[\d,]*)", lambda m: m.group(1).replace(",", "") + " rand", t)
    t = t.replace("stolenvalour.co.za", "stolen valour dot co dot za").replace(".co.za", " dot co dot za")
    return t


def pick(bank, override):
    if override:
        return next(s for s in bank if s["id"] == override), 0, 0
    now = datetime.datetime.now(datetime.timezone.utc)
    day = (now.date() - datetime.date(2026, 11, 25)).days
    slot = int(os.environ.get("SLOT") or (0 if now.hour < 8 else 1 if now.hour < 14 else 2)) % 3
    return bank[(day * 3 + slot) % len(bank)], day, slot


def music_for(brand, day, slot, pillar):
    """The one music entry point: a URL or local file for this reel, or None. Selection lives here only, so a new picker
    (per pillar, per mood) replaces this function without touching the beat sync or the scenes."""
    music = brand.get("music") or []
    if isinstance(music, dict):  # optional {"pain": [...], "value": [...], "default": [...]}
        music = music.get(pillar) or music.get("default") or []
    return music[(day * 3 + slot) % len(music)] if music else None


def fetch_music(src, dst):
    if str(src).startswith("http"):
        urllib.request.urlretrieve(src, dst)
    else:
        shutil.copy(ROOT / src if not os.path.isabs(src) else src, dst)


# ------------------------------------------------------------------ voice engines
# Each engine takes (texts, cfg) and returns (list of mono float32 takes, sample rate). Nothing else in the pipeline
# knows which engine ran: trimming, pacing and word timing are shared, so a new voice drops in as one function here
# plus "tts": {"engine": "<name>"} in the brand file.

def eng_kokoro(texts, cfg):
    from kokoro import KPipeline
    pipe = KPipeline(lang_code=cfg.get("lang", "a"))
    out = []
    for t in texts:
        parts = []
        for r in pipe(t, voice=cfg.get("voice", "af_heart"), speed=cfg.get("speed", 1.0)):
            a = r.audio.detach().cpu().numpy() if hasattr(r.audio, "detach") else np.asarray(r.audio)
            parts.append(a.astype(np.float32))
        out.append(np.concatenate(parts))
    return out, 24000


def eng_chatterbox(texts, cfg):
    """Chatterbox (MIT, Resemble AI)."""
    import torch
    from chatterbox.tts import ChatterboxTTS
    torch.manual_seed(cfg.get("seed", 7))
    m = ChatterboxTTS.from_pretrained(device="cpu")
    out = []
    for t in texts:
        wav = m.generate(t, exaggeration=cfg.get("exaggeration", 0.62), cfg_weight=cfg.get("cfg_weight", 0.42), temperature=cfg.get("temperature", 0.75))
        out.append(wav.squeeze().detach().cpu().numpy().astype(np.float32))
    return out, m.sr


ENGINES = {"chatterbox": eng_chatterbox, "kokoro": eng_kokoro}


def _frames_db(a, sr, hop=0.01):
    h = max(1, int(sr * hop)); n = len(a) // h
    if n == 0:
        return np.array([-120.0]), h
    e = np.sqrt(np.mean(a[: n * h].reshape(n, h) ** 2, axis=1) + 1e-12)
    return 20 * np.log10(e / (np.max(e) + 1e-12)), h


def tidy(a, sr):
    """Trim the silence before and after a take and cut any long pause inside it down to KEEP_PAUSE."""
    db, h = _frames_db(a, sr)
    on = db > -38
    if not on.any():
        return a
    i0, i1 = np.argmax(on), len(on) - np.argmax(on[::-1])
    a = a[max(0, i0 * h - int(0.02 * sr)): min(len(a), i1 * h + int(0.06 * sr))]
    db, h = _frames_db(a, sr); on = db > -38
    keep, k, n = [], 0, len(on)
    while k < n:
        if on[k]:
            keep.append((k, k + 1)); k += 1; continue
        j = k
        while j < n and not on[j]:
            j += 1
        run = (j - k) * h / sr
        if run > MAX_PAUSE:  # keep the edges of the pause so the cut is inaudible
            half = int(KEEP_PAUSE / 2 * sr / h)
            keep += [(k, k + half), (j - half, j)]
        else:
            keep.append((k, j))
        k = j
    out = [a[s * h: e * h] for s, e in keep]
    tail = a[n * h:]
    return np.concatenate(out + [tail]).astype(np.float32)


def stretch(takes, sr, rate):
    """Time-stretch every take by the same rate (pitch kept) with ffmpeg atempo."""
    if abs(rate - 1) < 0.015:
        return takes
    tmp = ROOT / "tmp"; tmp.mkdir(exist_ok=True)
    out = []
    for k, a in enumerate(takes):
        src, dst = tmp / f"take{k}.wav", tmp / f"take{k}.st.wav"
        sf.write(src, a, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter:a", f"atempo={rate:.4f}", "-ar", str(sr), "-ac", "1", str(dst)], check=True)
        b, _ = sf.read(dst, dtype="float32"); out.append(b)
    return out


def silences(wav, total, noise="-35dB"):
    """ffmpeg silencedetect on the voice stem. The planned 0.4 s tail after the last word is reported apart."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af", f"silencedetect=noise={noise}:d=0.12", "-f", "null", "-"], capture_output=True, text=True)
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    runs = [(a, en[k] if k < len(en) else total) for k, a in enumerate(st)]
    inner = [(a, b) for a, b in runs if a < total - TAIL - 0.05]
    inner = [(a, min(b, total - TAIL)) for a, b in inner]
    lon = max(inner, key=lambda r: r[1] - r[0], default=(0.0, 0.0))
    return {"longest": lon[1] - lon[0], "at": lon[0], "runs": inner}


def tts(texts, brand):
    """The one voice entry point: engine from the brand file, then shared tidy, pacing and Whisper word timings.
    Returns (takes, words per take as (start, end) seconds within the take, sample rate)."""
    global SR
    cfg = dict(brand.get("tts") or {})
    name = os.environ.get("TTS_ENGINE") or cfg.get("engine", "chatterbox")
    spoken = [speakable(t) for t in texts]
    try:
        takes, sr = ENGINES[name](spoken, cfg.get(name, {}) | {k: v for k, v in cfg.items() if not isinstance(v, dict)})
        print("voice:", name)
    except Exception as e:
        print(f"{name} unavailable, falling back to kokoro:", repr(e)[:300])
        takes, sr = eng_kokoro(spoken, {"voice": brand.get("voice", "af_heart"), "lang": brand.get("lang", "a")})
    SR = sr
    takes = [tidy(a / (np.max(np.abs(a)) + 1e-9) * 0.95, sr) for a in takes]
    from faster_whisper import WhisperModel
    wm = WhisperModel("base.en", device="cpu", compute_type="int8")

    def words_of(takes):
        res = []
        for k, a in enumerate(takes):
            # hand Whisper a 16 kHz array directly (no file decode, so no PyAV version issues)
            x16 = np.interp(np.arange(0, len(a) / sr, 1 / 16000), np.arange(len(a)) / sr, a).astype(np.float32)
            segs, _ = wm.transcribe(x16, word_timestamps=True, language="en", beam_size=1)
            res.append([(w.start, w.end) for s in segs for w in (s.words or [])])
        return res

    words = words_of(takes)
    n = sum(len(w) for w in words)
    secs = sum(len(a) for a in takes) / sr + sum(GAP_SENT for _ in takes[:-1])
    wpm = 60 * n / max(secs, 1e-6)
    total_rate = 1.0
    for _ in range(2):  # a fast take (Chatterbox can read at 190+ wpm) may need a second, smaller pass to reach the range
        if WPM_LO <= wpm <= WPM_HI:
            break
        rate = float(np.clip(WPM_GOAL / wpm, 0.86, 1.16))
        rate = float(np.clip(rate, 0.78 / total_rate, 1.2 / total_rate))
        if abs(rate - 1) < 0.015:
            break
        total_rate *= rate
        print(f"pace {wpm:.0f} wpm, stretching by {rate:.3f}")
        takes = [tidy(a, sr) for a in stretch(takes, sr, rate)]
        words = words_of(takes)
        secs = sum(len(a) for a in takes) / sr + sum(GAP_SENT for _ in takes[:-1])
        wpm = 60 * sum(len(w) for w in words) / secs
    print(f"pace {wpm:.0f} wpm over {secs:.1f} s")
    return takes, words, sr


def align(display, spoken, start, dur):
    """Times for the words as written: token timings when counts match, else spread by character length."""
    ws = display.split()
    if len(spoken) == len(ws):
        return [{"w": w, "start": round(start + a, 3), "end": round(start + b, 3)} for w, (a, b) in zip(ws, spoken)]
    if spoken:
        s0, s1 = spoken[0][0], spoken[-1][1]
    else:
        s0, s1 = 0.0, dur
    tot = sum(len(w) + 1 for w in ws)
    out, acc = [], 0
    for w in ws:
        a = s0 + (s1 - s0) * acc / tot; acc += len(w) + 1; b = s0 + (s1 - s0) * acc / tot
        out.append({"w": w, "start": round(start + a, 3), "end": round(start + b, 3)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", default="stolenvalour"); ap.add_argument("--id"); ap.add_argument("--out", default="out")
    ap.add_argument("--no-voice", action="store_true"); ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    brand = json.load(open(ROOT / "brands" / f"{a.brand}.json", encoding="utf-8"))
    bank = json.load(open(ROOT / "content" / f"{a.brand}.json", encoding="utf-8"))
    s, day, slot = pick(bank, a.id)
    rnd = random.Random(f"{s['id']}-{day}-{slot}")
    out = ROOT / a.out; out.mkdir(exist_ok=True)
    (PUB / "clips").mkdir(parents=True, exist_ok=True)
    for c in glob.glob(str(ROOT / "assets" / "clips" / "*.mp4")):
        dst = PUB / "clips" / os.path.basename(c)
        if not dst.exists():
            shutil.copy(c, dst)
    (PUB / "paper").mkdir(parents=True, exist_ok=True)
    for c in glob.glob(str(ROOT / "assets" / "paper" / "*.jpg")):
        shutil.copy(c, PUB / "paper" / os.path.basename(c))
    man = {k: v for k, v in json.load(open(ROOT / "assets" / "clips.json", encoding="utf-8")).items() if not k.startswith("_")}
    have = {os.path.basename(c) for c in glob.glob(str(PUB / "clips" / "*.mp4"))}
    mobile = sorted(c for c in man if c in have and c.endswith("-mobile.mp4"))
    desktop = sorted(c for c in man if c in have and c.endswith("-desktop.mp4"))
    lead_site = rnd.choice(mobile).split("-")[0] if mobile else None

    def clip(kind):
        pool = mobile if kind != "laptop" else desktop
        if not pool:
            return None
        same = [c for c in pool if c.startswith(lead_site or "")]
        return rnd.choice(same) if same and rnd.random() < 0.7 else rnd.choice(pool)

    segs_src = [("hook", s["hook"])] + [("line", x) for x in s["lines"]] + [("cta", s["cta"])]
    picks = S.assign(s)
    scene_of = [g.get("scene") or picks[i] for i, (_, g) in enumerate(segs_src)]
    pillar = s.get("pillar", "pain")
    niche = S.niche_of(" ".join(g["say"] for _, g in segs_src))
    voice_on = not a.no_voice and not a.preview  # every slot is voiced; there is no music-only format any more
    segs, t = [], LEAD
    if voice_on:
        takes, takes_words, _ = tts([g["say"] for _, g in segs_src], brand)
        chunks = [np.zeros(int(LEAD * SR), np.float32)]
    for i, (kind, g) in enumerate(segs_src):
        sc = scene_of[i]
        gap = (GAP_SENT if re.search(r"[.?!]\s*$", g["say"]) else GAP_SOFT) if i < len(segs_src) - 1 else 0.0
        if voice_on:
            au, spoken = takes[i], takes_words[i]; d = len(au) / SR
            chunks += [au, np.zeros(int(gap * SR), np.float32)]
        elif a.preview:
            spoken, d = [], len(speakable(g["say"]).split()) * 60 / WPM_GOAL + 0.1
        else:
            spoken, d, gap = [], max(MIN_MUSIC.get(sc, 2.8), 0.42 * len(g["show"].split()) + 1.8), 0.25
        c, frm = (clip("phone"), 0) if sc == "footage" else (None, 0)
        if c:
            need = int((d + gap) * 30)
            wins = man.get(c, [0, 0])
            wins = wins if wins and isinstance(wins[0], list) else [wins]  # [a, b] or [[a, b], [c, d], ...]
            fit = [w for w in wins if w[1] - w[0] >= need] or [max(wins, key=lambda w: w[1] - w[0])]
            a0, a1 = rnd.choice(fit)
            frm = rnd.randint(a0, max(a0, a1 - need))
        mood = S.mood_of(g["show"] + " " + g["say"], pillar, kind)
        segs.append({"kind": kind, "show": g["show"], "say": g["say"], "start": round(t, 3), "end": round(t + d, 3),
                     "words": align(g["say"], spoken, t, d), "scene": sc, "mood": mood,
                     "clip": ("clips/" + c) if c else None, "clipFrom": frm, "n": i if kind == "line" else 0})
        t += d + gap
    total = round(t + TAIL, 3)
    kick = {"pain": "STOP SCROLLING", "value": "READ THIS FIRST", "niche": "OWNERS, WATCH THIS", "teach": "QUICK TIP"}.get(pillar, "STOP SCROLLING")
    wa = "whatsapp" in s["cta"]["say"].lower() and "dm" not in s["cta"]["say"].lower().split()
    props = {"fps": 30, "total": total, "voice": None, "music": None, "sfx": None, "segs": segs, "kicker": kick, "pillar": pillar,
             "niche": niche, "plans": brand.get("plans", []), "captions": bool(a.preview), "palette": brand.get("colors"),
             "cta": {"channel": "whatsapp" if wa else "dm", "text": "Hi, I'd like a free mock-up" if wa else "SITE"},
             "brand": {"name": brand["name"], "url": brand["url"], "contact": brand.get("contact_short", "WhatsApp 065 027 6518"), "accent": brand.get("accent", "#14213D"),
                       "phone": brand.get("phone", "065 027 6518"), "handle": brand.get("handle", "@stolenvalour.co.za")}}
    gaps = None
    if voice_on:
        v = np.concatenate(chunks + [np.zeros(int(TAIL * SR), np.float32)]); v = v / (np.max(np.abs(v)) + 1e-9) * 0.92
        sf.write(PUB / "voice.wav", v, SR); props["voice"] = "voice.wav"
        gaps = silences(PUB / "voice.wav", total)
        print(f"voice check: first word at {segs[0]['words'][0]['start'] if segs[0]['words'] else LEAD:.2f} s, longest silence {gaps['longest']:.2f} s "
              f"(at {gaps['at']:.2f} s), tail {TAIL:.2f} s, total {total:.2f} s")
    # music, then the beat grid: voice timing stays as it is, only the visual cuts and small accents move onto beats
    props["beats"], props["musicFrom"] = [], 0.0
    beat_share, music_src = None, music_for(brand, day, slot, pillar)
    if music_src:
        try:
            fetch_music(music_src, PUB / "music.mp3"); props["music"] = "music.mp3"
        except Exception as e:
            print("music download failed:", e)
    if props["music"]:
        try:
            g = B.grid(music_src, local=PUB / "music.mp3")
            cta_at = segs[-1]["start"] - B.CUT_LEAD
            off, drop = B.choose_offset(g, total, cta_at, segs)
            bts = B.in_reel(g, off, total)
            beat_share = B.snap_cuts(segs, bts)
            props["beats"], props["musicFrom"] = bts, off
            where = f"phrase change at {drop:.2f} s, CTA cut at {cta_at:.2f} s" if drop is not None else "no drop near the CTA, phrase grid used"
            print(f"beats: {g['tempo']:.0f} bpm, music from {off:.2f} s, {where}, {100 * beat_share:.0f}% of cuts on a beat")
        except Exception as e:
            print("beat sync skipped:", repr(e)[:300])
    write_sfx(PUB / "sfx.wav", segs, total); props["sfx"] = "sfx.wav"
    (ROOT / "tmp").mkdir(exist_ok=True)
    pp = ROOT / "tmp" / "props.json"; pp.write_text(json.dumps(props), encoding="utf-8")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M")
    name = f"{stamp}-{s['id']}"
    mp4, cover = out / f"{name}.mp4", out / f"{name}.jpg"
    npx = "npx.cmd" if os.name == "nt" else "npx"
    subprocess.run([npx, "remotion", "render", "src/index.ts", "Reel", str(mp4), f"--props={pp}", "--video-bitrate=4M",
                    "--audio-bitrate=160k", "--log=warn"], cwd=REEL, check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0.5, segs[0]['end'] - 0.3)}", "-i", str(mp4), "-frames:v", "1", "-q:v", "3", str(cover)], check=True)
    repo = os.environ.get("GITHUB_REPOSITORY", "uzandigitalofficial/ace-reels")
    owner, rn = repo.split("/")
    base = f"https://{owner.lower()}.github.io/{rn}/reels/"
    caption = s["caption"].strip() + "\n\n" + " ".join(s.get("hashtags", []))
    meta = {"id": s["id"], "brand": a.brand, "file": mp4.name, "video_url": base + mp4.name, "cover_url": base + cover.name,
            "caption": caption, "v": 2, "engine": 6.1, "test": os.environ.get("REEL_TEST") == "true", "seconds": total, "made": stamp}
    if gaps:
        meta["voice_longest_silence"] = round(gaps["longest"], 3)
    if beat_share is not None:
        meta["beat_cuts"] = round(beat_share, 3)
        meta["music_from"] = props["musicFrom"]
    # automatic scorecard: a hard fail keeps the reel off the feed and off Instagram, it never stops the workflow
    try:
        import qa as Q
        q = Q.run(mp4, PUB / "voice.wav" if voice_on else None, pp)
        print(Q.line(q))
    except Exception as e:
        q = {"pass": True, "error": repr(e)[:300]}
        print("qa: skipped,", q["error"])
    meta["qa"] = q
    if not q.get("pass", True):
        meta["qa_fail"] = True
        print("qa: hard fail, this reel stays off the feed and is not posted")
    (out / f"{name}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
