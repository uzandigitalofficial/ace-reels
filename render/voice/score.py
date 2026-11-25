"""Objective checks on every voice candidate: Whisper word error rate (clarity), pace, pitch, loudness.
Usage: python render/voice/score.py  -> prints a table and writes picks/_raw/voice_scores.json"""
import json
import pathlib
import re
import subprocess
import tempfile

import librosa
import numpy as np
import pyloudnorm as pyln
from faster_whisper import WhisperModel

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "picks" / "_raw" / "voice"
SCRIPT = ("Are you on Google? Search for your business like a customer would. "
          "If you can't find yourself, neither can they. Set up your free Business Profile tonight.")


def norm(s):
    return re.sub(r"[^a-z' ]", " ", s.lower().replace("can't", "cant").replace("’", "'")).split()


def wer(ref, hyp):
    r, h = norm(ref), norm(hyp)
    d = np.zeros((len(r) + 1, len(h) + 1), int); d[:, 0] = range(len(r) + 1); d[0, :] = range(len(h) + 1)
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + (r[i - 1] != h[j - 1]))
    return d[-1, -1] / len(r)


def main():
    wm = WhisperModel("small.en", device="cpu", compute_type="int8")
    out = {}
    for f in sorted(RAW.iterdir()):
        if f.name.startswith("_") or f.suffix not in (".wav", ".mp3"):
            continue
        tmp = pathlib.Path(tempfile.gettempdir()) / f"score_{f.stem}.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-ac", "1", "-ar", "24000", str(tmp)], check=True)
        y, sr = librosa.load(tmp, sr=24000)
        yt, _ = librosa.effects.trim(y, top_db=35)
        dur = len(yt) / sr
        f0, vf, _ = librosa.pyin(yt, fmin=70, fmax=400, sr=sr)
        segs, _ = wm.transcribe(librosa.resample(y, orig_sr=sr, target_sr=16000), language="en", beam_size=5)
        text = " ".join(s.text.strip() for s in segs)
        lufs = pyln.Meter(sr).integrated_loudness(y)
        out[f.stem] = {"dur": round(dur, 2), "wpm": round(len(norm(SCRIPT)) / dur * 60), "f0": round(float(np.nanmedian(f0)), 1),
                       "f0_spread": round(float(np.nanstd(f0)), 1), "wer": round(wer(SCRIPT, text), 3), "lufs": round(lufs, 1), "heard": text}
        o = out[f.stem]
        print(f"{f.stem:20s} dur {o['dur']:5.2f}s  {o['wpm']:3d} wpm  f0 {o['f0']:5.1f}Hz +-{o['f0_spread']:4.1f}  wer {o['wer']:.3f}  | {text}")
    (ROOT / "picks" / "_raw" / "voice_scores.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
