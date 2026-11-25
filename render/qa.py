"""Automatic scorecard for a rendered reel.
python render/qa.py <mp4> [--voice voice.wav] [--props props.json] [--json]
Without --voice / --props it looks for <mp4 stem>.voice.wav and <mp4 stem>.props.json next to the mp4.
Exit code 1 on a hard fail, 0 otherwise.

Hard fails (any one stops the reel being posted):
  silence   longest silence inside the voice region over 0.4 s (voice stem, ffmpeg silencedetect -35 dB, planned tail excluded)
  palette   a region of saturated colour outside cream and navy bigger than 0.6 % of the frame (muted WhatsApp green and the
            blue read ticks inside mock-ups are allowed; site footage windows are masked out)
  duration  under 15 s or over 60 s
  bitrate   over 4.5 Mbps
  blank     black or blank frames
Soft score 0 to 100 (20 each): words a minute in 150 to 165, scene count and variety, motion in every second, text inside the
safe margins, share of cuts on a music beat.
"""
import argparse, json, pathlib, re, subprocess, sys

import numpy as np

W, H = 216, 384                 # analysis size (1080x1920 / 5)
FPS = 6
TAIL = 0.4
PAL_LIMIT = 0.006               # share of the frame that may be off palette
SIL_LIMIT = 0.4


def probe(mp4):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,bit_rate,size", "-of", "json", str(mp4)], capture_output=True, text=True, check=True)
    f = json.loads(r.stdout)["format"]
    dur = float(f["duration"])
    rate = float(f.get("bit_rate") or int(f["size"]) * 8 / dur)
    return dur, rate


def frames(mp4):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, H, W, 3)


def voice_silence(wav, total):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af", "silencedetect=noise=-35dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True)
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    runs = [(a, en[k] if k < len(en) else total) for k, a in enumerate(st)]
    inner = [(a, min(b, total - TAIL)) for a, b in runs if a < total - TAIL - 0.05]
    lon = max(inner, key=lambda r: r[1] - r[0], default=(0.0, 0.0))
    return round(lon[1] - lon[0], 3), round(lon[0], 2)


def off_palette(fr):
    """Mask of saturated pixels that are not navy blue (hue 200 to 240), not the muted WhatsApp green (hue 95 to 170, chroma
    under 120) and not warm cream or kraft (chroma under 60, which covers every paper tone)."""
    x = fr.astype(np.int16)
    mx, mn = x.max(-1), x.min(-1)
    ch = mx - mn
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    safe = np.maximum(ch, 1)
    hue = np.where(mx == r, ((g - b) / safe) % 6, np.where(mx == g, (b - r) / safe + 2, (r - g) / safe + 4)) * 60
    sat = ch > 60
    navy = (hue >= 200) & (hue <= 240)
    green = (hue >= 95) & (hue <= 170) & (ch < 120)
    return sat & ~navy & ~green


def footage_mask(segs, t):
    """The footage polaroid window (Footage scene: 460 wide photo at x 222, y 662, height 500, rotated a little) in analysis pixels."""
    m = np.zeros((H, W), bool)
    for s in segs:
        a = s.get("cut", s["start"] - 0.12)
        if s.get("scene") == "footage" and a - 0.1 <= t <= s["end"] + 0.6:
            m[int(620 / 5): int(1200 / 5), int(180 / 5): int(720 / 5)] = True
    return m


def run(mp4, voice=None, props=None):
    mp4 = pathlib.Path(mp4)
    voice = pathlib.Path(voice) if voice else mp4.with_suffix(".voice.wav")
    props = pathlib.Path(props) if props else mp4.with_suffix(".props.json")
    P = json.loads(props.read_text(encoding="utf-8")) if props.exists() else {}
    segs = P.get("segs", [])
    dur, rate = probe(mp4)
    fr = frames(mp4)
    n = len(fr)
    hard, notes = [], []

    # ---- hard checks
    sil = None
    if voice.exists():
        sil, at = voice_silence(voice, P.get("total", dur))
        if sil > SIL_LIMIT:
            hard.append(f"silence {sil:.2f} s at {at:.2f} s")
    elif segs and any(s["words"] for s in segs):
        ws = [w for s in segs for w in s["words"]]
        sil = round(max([b["start"] - a["end"] for a, b in zip(ws, ws[1:])] + [0]), 3)
        notes.append("silence from word timings (no voice stem)")
        if sil > SIL_LIMIT + 0.15:
            hard.append(f"word gap {sil:.2f} s")
    if not 15 <= dur <= 60:
        hard.append(f"duration {dur:.1f} s")
    if rate > 4.5e6:
        hard.append(f"bitrate {rate / 1e6:.2f} Mbps")
    pal_worst, pal_at = 0.0, 0.0
    blank = []
    for k in range(n):
        t = k / FPS
        f = fr[k]
        m = off_palette(f) & ~footage_mask(segs, t)
        share = float(m.mean())
        if share > pal_worst:
            pal_worst, pal_at = share, t
        lum = f.mean()
        if lum < 18 or f.std() < 2.0:
            blank.append(round(t, 2))
    if pal_worst > PAL_LIMIT:
        hard.append(f"off palette {100 * pal_worst:.2f}% of frame at {pal_at:.1f} s")
    if blank:
        hard.append(f"black or blank frames at {blank[:5]}")

    # ---- soft score
    soft = {}
    words = sum(len(s["words"]) for s in segs) or sum(len(s.get("say", "").split()) for s in segs)
    span = (segs[-1]["words"][-1]["end"] - segs[0]["words"][0]["start"]) if segs and segs[0]["words"] and segs[-1]["words"] else max(dur - TAIL, 1)
    wpm = 60 * words / max(span, 1e-6) if words else 0
    soft["wpm"] = 20 if 150 <= wpm <= 165 else round(max(0, 20 - 2 * abs(wpm - (150 if wpm < 150 else 165))), 1)
    scenes = [s.get("scene") for s in segs]
    variety = len(set(scenes)) / max(1, len(scenes))
    soft["scenes"] = round((10 if 4 <= len(scenes) <= 8 else 5 if scenes else 0) + 10 * variety, 1)
    # motion: mean absolute frame difference for every second; a second counts as still when nothing moves
    g = fr.mean(-1)
    diffs = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2)) if n > 1 else np.zeros(1)
    secs = max(1, int(dur))
    still = [s for s in range(secs) if diffs[s * FPS: (s + 1) * FPS].max(initial=0) < 0.15]
    soft["motion"] = round(20 * (1 - len(still) / secs), 1)
    # safe margins: 40 px at the sides, the bottom 300 px (Instagram caption and buttons); top 12 px is the progress line
    mg = np.zeros((H, W), bool)
    mg[:, : 40 // 5] = mg[:, -40 // 5:] = True
    mg[(1920 - 300) // 5:, :] = True
    mg[: 12 // 5, :] = False
    dark = (g < 110)
    bad = [k for k in range(n) if (dark[k] & mg).mean() > 0.002]
    soft["margins"] = round(20 * (1 - len(bad) / max(1, n)), 1)
    beats = P.get("beats") or []
    cuts = [s.get("cut", s["start"] - 0.12) for s in segs[1:]]
    if beats and cuts:
        b = np.asarray(beats)
        on = sum(1 for c in cuts if np.abs(b - c).min() <= 0.035)
        beat_pct = round(100 * on / len(cuts))
        soft["beats"] = round(20 * on / len(cuts), 1)
    else:
        beat_pct = None
        soft["beats"] = 10  # no music: neutral
        notes.append("no beat grid")
    score = round(sum(soft.values()))
    return {"file": mp4.name, "pass": not hard, "hard": hard, "score": score, "soft": soft, "seconds": round(dur, 2),
            "mbps": round(rate / 1e6, 2), "wpm": round(wpm), "longest_silence": sil, "off_palette_pct": round(100 * pal_worst, 3),
            "still_seconds": still, "margin_frames": len(bad), "beat_pct": beat_pct, "cuts": len(cuts), "notes": notes}


def line(q):
    return (f"qa: {'PASS' if q['pass'] else 'FAIL'} score {q['score']}/100 | {q['seconds']} s {q['mbps']} Mbps {q['wpm']} wpm | "
            f"silence {q['longest_silence']} s | off palette {q['off_palette_pct']}% | beats {q['beat_pct']}% of {q['cuts']} cuts | "
            f"soft {q['soft']}" + (f" | HARD: {'; '.join(q['hard'])}" if q["hard"] else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mp4"); ap.add_argument("--voice"); ap.add_argument("--props"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    q = run(a.mp4, a.voice, a.props)
    print(json.dumps(q, indent=1) if a.json else line(q))
    sys.exit(0 if q["pass"] else 1)


if __name__ == "__main__":
    main()
