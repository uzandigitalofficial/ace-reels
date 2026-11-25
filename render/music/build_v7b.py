"""Build the final pick sheet audio (v7b): six voices and six music beds at -16 LUFS, mp3 128k mono, plus picks/picks.json.
Reads picks/_raw/v7b (voices) and picks/_raw/music + picks/_raw/sources_raw.json (tracks). Then run sheet_html.py.
Usage: python render/music/build_v7b.py"""
import json
import pathlib
import subprocess
import tempfile

import numpy as np
import pyloudnorm as pyln
import soundfile as sf

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "picks" / "_raw"
OUT = ROOT / "picks"
SR = 44100
meter = pyln.Meter(SR)

# id, raw file, engine label, the "tts" value for brands/stolenvalour.json, one line
VOICES = [
    ("V1", "V1.mp3", "Microsoft Ava Multilingual", {"engine": "edge", "voice": "en-US-AvaMultilingualNeural", "rate": "-4%"},
     "American, warm and natural. Our top pick for a real, human feel."),
    ("V2", "V2.mp3", "Microsoft Emma Multilingual", {"engine": "edge", "voice": "en-US-EmmaMultilingualNeural", "rate": "-4%"},
     "American, bright and chatty. A little younger and quicker."),
    ("V3", "V3.mp3", "Microsoft Sonia", {"engine": "edge", "voice": "en-GB-SoniaNeural", "rate": "-4%"},
     "British, polished and calm. Premium and measured."),
    ("V4", "V4.mp3", "Microsoft Leah", {"engine": "edge", "voice": "en-ZA-LeahNeural", "rate": "-4%"},
     "South African English. Sounds local to your dealers."),
    ("V5", "V5.wav", "Kokoro, Heart", {"engine": "kokoro", "voice": "af_heart", "lang": "a"},
     "American, smooth and clean. Works today, no key and no extra setup."),
    ("V6", "V6.wav", "Chatterbox, calm settings", {"engine": "chatterbox", "chatterbox": {"exaggeration": 0.40, "cfg_weight": 0.50, "temperature": 0.70, "seed": 7}},
     "The voice the reels use now, tuned steadier and less sing-song."),
]
# id, track stem, one line, picks.json music record id from the earlier run
MUSIC = [
    ("M1", "gymnopedie_no_1", "Satie's soft solo piano. Calm, elegant, about one note a second."),
    ("M2", "sincerely", "Slow, warm and low. Almost nothing in the voice range."),
    ("M3", "lightless_dawn", "Very slow ambient piano and texture. Reflective."),
    ("M4", "windswept", "Airy, even ambient bed. Very steady level."),
    ("M5", "fresh_air", "The sparsest bed: long soft tones, hardly any attacks."),
    ("M6", "perspectives", "Gentle and even, a little more motion. Keeps a reel moving."),
]


def ff(*a):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, a)], check=True)


def load(p):
    tmp = pathlib.Path(tempfile.gettempdir()) / f"v7b_{p.stem}.wav"
    ff("-i", p, "-ac", 1, "-ar", SR, "-c:a", "pcm_f32le", tmp)
    return sf.read(tmp, dtype="float32")[0]


def trim(y, pad=0.15):
    e = np.abs(y) > 0.01 * np.max(np.abs(y)); i = np.argmax(e); j = len(e) - np.argmax(e[::-1])
    return y[max(0, i - int(pad * SR)): j + int(pad * SR)]


def save(y, dst, target=-16.0):
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.gettempdir()) / f"v7b_out_{dst.stem}.wav"
    y = y * 10 ** ((target - meter.integrated_loudness(y)) / 20)
    for _ in range(2):  # limiter can eat some level: add it back once
        sf.write(tmp, y, SR, subtype="FLOAT")
        ff("-i", tmp, "-af", "alimiter=limit=0.89:level=false", "-c:a", "libmp3lame", "-b:a", "128k", "-ac", 1, dst)
        got = meter.integrated_loudness(load(dst))
        if abs(got - target) < 0.4:
            break
        y = y * 10 ** ((target - got) / 20)
    return round(got, 1), round(len(y) / SR, 1)


def main():
    rec = {"voices": [], "music": []}
    for vid, f, engine, tts, line in VOICES:
        y = trim(load(RAW / "v7b" / f))
        y[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR)); y[-int(0.06 * SR):] *= np.linspace(1, 0, int(0.06 * SR))
        lufs, secs = save(y, OUT / "voice" / f"{vid}.mp3")
        rec["voices"].append({"id": vid, "file": f"voice/{vid}.mp3", "engine": engine, "line": line, "tts": tts, "lufs": lufs, "secs": secs})
        print(vid, engine, lufs, "LUFS", secs, "s")
    src = {s["file"]: s for s in json.loads((RAW / "sources_raw.json").read_text(encoding="utf-8"))}
    for mid, stem, line in MUSIC:
        y = load(RAW / "music" / f"{stem}.mp3")
        sec = np.array([np.sqrt(np.mean(y[i:i + SR] ** 2) + 1e-12) for i in range(0, len(y) - SR, SR)])
        db = 20 * np.log10(sec); start = int(np.argmax(db >= np.median(db) - 6))  # skip a quiet intro
        y = y[start * SR: (start + 28) * SR]
        y[:SR] *= np.linspace(0, 1, SR); y[-2 * SR:] *= np.linspace(1, 0, 2 * SR)
        lufs, secs = save(y, OUT / "music" / f"{mid}.mp3")
        s = src[f"{stem}.mp3"]
        rec["music"].append({"id": mid, "file": f"music/{mid}.mp3", "title": s["title"] if "title" in s else stem.replace("_", " ").title(),
                             "artist": s["artist"], "line": line, "url": s["source"], "page": s["page"], "licence": s["licence"],
                             "attribution": s["attribution"], "lufs": lufs, "secs": secs})
        print(mid, stem, lufs, "LUFS", secs, "s")
    (OUT / "picks.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
