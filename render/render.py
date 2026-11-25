"""Render one 9:16 reel from a script bank. Free and token-free: Kokoro voice, Playwright frames, ffmpeg.
Usage: python render/render.py --brand stolenvalour [--id sv-001] [--out out]
"""
import argparse, datetime, io, json, os, pathlib, subprocess, sys
import numpy as np, soundfile as sf

ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS, W, H, SR = 30, 1080, 1920, 24000
LEAD, GAP, TAIL = 0.45, 0.30, 2.2


def pick(bank, override):
    if override:
        return next(s for s in bank if s["id"] == override)
    now = datetime.datetime.now(datetime.timezone.utc)
    day = (now.date() - datetime.date(2026, 11, 25)).days
    slot = int(os.environ.get("SLOT") or (0 if now.hour < 8 else 1 if now.hour < 14 else 2)) % 3
    return bank[(day * 3 + slot) % len(bank)], day, slot


import re
DIG = "oh one two three four five six seven eight nine".split()


def speakable(t):
    t = re.sub(r"\b0(\d{2}) ?(\d{3}) ?(\d{4})\b", lambda m: ", ".join(" ".join(DIG[int(c)] for c in g) for g in (("0" + m.group(1)), m.group(2), m.group(3))), t)
    t = re.sub(r"R ?(\d[\d,]*)", lambda m: m.group(1).replace(",", "") + " rand", t)
    t = re.sub(r"US\$ ?(\d+)", r"\1 US dollars", t)
    t = t.replace("stolenvalour.co.za", "stolen valour dot co dot za").replace(".co.za", " dot co dot za")
    return t


def tts(texts, voice, lang):
    from kokoro import KPipeline
    pipe = KPipeline(lang_code=lang)
    out = []
    for t in texts:
        parts = []
        for r in pipe(t, voice=voice, speed=1.0):
            a = r[2] if isinstance(r, tuple) else r.audio
            parts.append(a.detach().cpu().numpy() if hasattr(a, "detach") else np.asarray(a))
        out.append(np.concatenate(parts).astype(np.float32))
    return out


def pad(total):
    """Very quiet ambient bed: detuned sines on a soft minor-9 chord, slow swells."""
    n = int(total * SR)
    t = np.arange(n) / SR
    bed = np.zeros(n, np.float32)
    for f in (110.0, 164.81, 220.0, 261.63, 329.63, 493.88):
        for d in (-0.6, 0.6):
            bed += np.sin(2 * np.pi * (f + d) * t + f) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.07 * t + f))
    bed /= np.max(np.abs(bed)) + 1e-9
    env = np.minimum(1, t / 2.5) * np.minimum(1, (total - t) / 2.0)
    return (bed * env * 0.045).astype(np.float32)


def shoot(browser, url, path):
    pg = browser.new_page(viewport={"width": 393, "height": 852}, device_scale_factor=2, is_mobile=True, has_touch=True)
    pg.goto(url, wait_until="load", timeout=60000)
    pg.wait_for_timeout(4500)
    from PIL import Image
    tiles = []
    for y in (0, 820, 1640, 2460):
        pg.evaluate(f"window.scrollTo(0,{y})")
        pg.wait_for_timeout(1400)
        tiles.append(Image.open(io.BytesIO(pg.screenshot(type="png"))).convert("RGB"))
    pg.close()
    w = tiles[0].width
    img = Image.new("RGB", (w, sum(t.height for t in tiles)))
    yy = 0
    for t in tiles:
        img.paste(t, (0, yy)); yy += t.height
    img.save(path, quality=88)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", default="stolenvalour")
    ap.add_argument("--id")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    brand = json.load(open(ROOT / "brands" / f"{a.brand}.json", encoding="utf-8"))
    bank = json.load(open(ROOT / "content" / f"{a.brand}.json", encoding="utf-8"))
    if a.id:
        s, day, slot = pick(bank, a.id), 0, 9
    else:
        s, day, slot = pick(bank, None)
    out = ROOT / a.out; out.mkdir(exist_ok=True)
    tmp = ROOT / "tmp"; tmp.mkdir(exist_ok=True)
    segs = [s["hook"]] + s["lines"] + [s["cta"]]
    audio = tts([speakable(g["say"]) for g in segs], brand.get("voice", "af_heart"), brand.get("lang", "a"))
    t, chunks, tl = LEAD, [np.zeros(int(LEAD * SR), np.float32)], []
    for g, au in zip(segs, audio):
        d = len(au) / SR
        tl.append({"show": g["show"], "say": g["say"], "start": round(t, 3), "end": round(t + d, 3)})
        chunks += [au, np.zeros(int(GAP * SR), np.float32)]
        t += d + GAP
    total = t + TAIL
    voice = np.concatenate(chunks)
    voice = np.pad(voice, (0, max(0, int(total * SR) - len(voice))))[: int(total * SR)]
    peak = np.max(np.abs(voice)) + 1e-9
    mix = voice / peak * 0.89 + pad(total)
    wav = tmp / "mix.wav"; sf.write(wav, np.clip(mix, -1, 1), SR)

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M")
    name = f"{stamp}-{s['id']}"
    mp4, cover = out / f"{name}.mp4", out / f"{name}.jpg"
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--allow-file-access-from-files", "--disable-web-security"])
        shot = None
        if s.get("visual") == "site" and brand.get("shots"):
            url = brand["shots"][(day * 3 + slot) % len(brand["shots"])]
            try:
                sp = tmp / "site.jpg"; shoot(b, url, sp); shot = sp.as_uri()
            except Exception as e:
                print("site shot failed, typographic fallback:", e)
        cfg = {"brand": brand["name"], "url": brand["url"], "contact": brand.get("contact", ""),
               "colors": brand.get("colors", {}), "canvas": brand.get("canvas", {}), "kicker": brand.get("kicker", ""),
               "visual": s.get("visual", "type"), "shot": shot, "segs": tl, "total": total}
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto((ROOT / "render" / "template.html").as_uri())
        pg.evaluate("c=>window.setup(c)", cfg)
        pg.wait_for_function("window.__ready===true", timeout=60000)
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                               "-i", str(wav), "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p",
                               "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(mp4)],
                              stdin=subprocess.PIPE)
        frames = int(total * FPS)
        for i in range(frames):
            pg.evaluate(f"window.renderAt({i / FPS})")
            ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
            if i % 150 == 0:
                print(f"frame {i}/{frames}", flush=True)
        ff.stdin.close(); ff.wait()
        pg.evaluate(f"window.renderAt({tl[0]['end'] - 0.1})")
        pg.screenshot(path=str(cover), type="jpeg", quality=90)
        b.close()
    if ff.returncode != 0:
        sys.exit("ffmpeg failed")
    repo = os.environ.get("GITHUB_REPOSITORY", "uzandigitalofficial/ace-reels")
    owner, rn = repo.split("/")
    base = f"https://{owner.lower()}.github.io/{rn}/reels/"
    caption = s["caption"].strip() + "\n\n" + " ".join(s.get("hashtags", []))
    meta = {"id": s["id"], "brand": a.brand, "file": mp4.name, "video_url": base + mp4.name, "cover_url": base + cover.name,
            "caption": caption, "seconds": round(total, 1), "made": stamp}
    (out / f"{name}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
