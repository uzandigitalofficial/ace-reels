"""Reel Engine 5: real site footage + Remotion edit + word-synced captions + music. Token-free.
Usage: python render/render5.py --brand stolenvalour [--id sv-001] [--out out] [--no-voice]
"""
import argparse, datetime, glob, json, os, pathlib, random, re, shutil, subprocess, sys, urllib.request
import numpy as np, soundfile as sf

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "reel"
PUB = REEL / "public"
SR, LEAD, GAP, TAIL = 24000, 0.35, 0.22, 1.9
DIG = "oh one two three four five six seven eight nine".split()


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


def tts(texts, voice, lang):
    from kokoro import KPipeline
    pipe = KPipeline(lang_code=lang)
    res = []
    for t in texts:
        parts, words, off = [], [], 0.0
        for r in pipe(speakable(t), voice=voice, speed=1.06):
            a = r.audio.detach().cpu().numpy() if hasattr(r.audio, "detach") else np.asarray(r.audio)
            for tk in getattr(r, "tokens", None) or []:
                if getattr(tk, "start_ts", None) is not None and getattr(tk, "end_ts", None) is not None and any(c.isalnum() for c in tk.text):
                    words.append((off + tk.start_ts, off + tk.end_ts))
            parts.append(a.astype(np.float32)); off += len(a) / SR
        res.append((np.concatenate(parts), words))
    return res


def tts_chatterbox(texts):
    """Chatterbox (MIT, Resemble AI): far more human than Kokoro. Word times come from Whisper on the real audio."""
    global SR
    import torch
    from chatterbox.tts import ChatterboxTTS
    from faster_whisper import WhisperModel
    torch.manual_seed(7)
    m = ChatterboxTTS.from_pretrained(device="cpu")
    SR = m.sr
    wm = WhisperModel("base.en", device="cpu", compute_type="int8")
    res = []
    for t in texts:
        wav = m.generate(speakable(t), exaggeration=0.62, cfg_weight=0.42, temperature=0.75)
        a = wav.squeeze().detach().cpu().numpy().astype(np.float32)
        a = a / (np.max(np.abs(a)) + 1e-9) * 0.95
        tmp = ROOT / "tmp" / "seg.wav"; tmp.parent.mkdir(exist_ok=True); sf.write(tmp, a, SR)
        segs, _ = wm.transcribe(str(tmp), word_timestamps=True, language="en", beam_size=1)
        words = [(w.start, w.end) for s in segs for w in (s.words or [])]
        res.append((a, words))
    return res


def tts_any(texts, brand):
    try:
        out = tts_chatterbox(texts); print("voice: chatterbox"); return out
    except Exception as e:
        print("chatterbox unavailable, falling back to kokoro:", repr(e)[:300])
        return tts(texts, brand.get("voice", "af_heart"), brand.get("lang", "a"))


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
    ap.add_argument("--no-voice", action="store_true")
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
    devices = ["phone", "laptop", "full", "phone"]
    voice_on = not a.no_voice and os.environ.get("FORMAT") != "music"
    if not a.id and slot == 2:
        voice_on = False  # every evening reel is a music-only edit
    segs, t = [], LEAD
    if voice_on:
        audio = tts_any([g["say"] for _, g in segs_src], brand)
        chunks = [np.zeros(int(LEAD * SR), np.float32)]
    for i, (kind, g) in enumerate(segs_src):
        dev = "full" if kind in ("hook", "cta") else devices[(i - 1) % len(devices)]
        if voice_on:
            au, spoken = audio[i]; d = len(au) / SR
            chunks += [au, np.zeros(int(GAP * SR), np.float32)]
        else:
            spoken, d = [], max(1.9, 0.42 * len(g["show"].split()) + 0.9)
        c = clip(dev)
        a0, a1 = man.get(c, [0, 0]) if c else (0, 0)
        frm = rnd.randint(a0, max(a0, a1 - int((d + GAP) * 30)))
        segs.append({"kind": kind, "show": g["show"], "say": g["say"], "start": round(t, 3), "end": round(t + d, 3),
                     "words": align(g["say"], spoken, t, d), "device": dev, "clip": ("clips/" + c) if c else None, "clipFrom": frm, "n": i if kind == "line" else 0})
        t += d + GAP
    total = round(t + TAIL, 3)
    kick = {"pain": "STOP SCROLLING", "value": "READ THIS FIRST", "niche": "OWNERS, WATCH THIS"}.get(s.get("pillar"), "STOP SCROLLING")
    wa = "whatsapp" in s["cta"]["say"].lower() and "dm" not in s["cta"]["say"].lower().split()
    props = {"fps": 30, "total": total, "voice": None, "music": None, "segs": segs, "kicker": kick,
             "cta": {"channel": "whatsapp" if wa else "dm", "text": "Hi, I'd like a free mock-up" if wa else "SITE"},
             "brand": {"name": brand["name"], "url": brand["url"], "contact": brand.get("contact_short", "WhatsApp 065 027 6518"), "accent": brand.get("accent", "#B8F2D6")}}
    if voice_on:
        v = np.concatenate(chunks); v = v / (np.max(np.abs(v)) + 1e-9) * 0.92
        sf.write(PUB / "voice.wav", v, SR); props["voice"] = "voice.wav"
    music = brand.get("music") or []
    if music:
        url = music[(day * 3 + slot) % len(music)]
        try:
            urllib.request.urlretrieve(url, PUB / "music.mp3"); props["music"] = "music.mp3"
        except Exception as e:
            print("music download failed:", e)
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
            "caption": caption, "v": 2, "engine": 5, "test": os.environ.get("REEL_TEST") == "true", "seconds": total, "made": stamp}
    (out / f"{name}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
