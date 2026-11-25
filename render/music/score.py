"""Measure how well each music candidate sits under a voice: busy-ness (onsets per second), brightness,
energy share in the speech presence band (1 to 4 kHz, lower is better), and how much the level swings.
Usage: python render/music/score.py  -> table + picks/_raw/music_scores.json"""
import json
import pathlib

import librosa
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "picks" / "_raw" / "music"


def main():
    out = {}
    for f in sorted(RAW.glob("*.mp3")):
        y, sr = librosa.load(f, sr=22050, mono=True, duration=150)
        full = librosa.get_duration(path=str(f))
        S = np.abs(librosa.stft(y, n_fft=2048)) ** 2
        fr = librosa.fft_frequencies(sr=sr, n_fft=2048)
        presence = S[(fr >= 1000) & (fr <= 4000)].sum() / S.sum()
        onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
        tempo = float(np.atleast_1d(librosa.beat.beat_track(y=y, sr=sr)[0])[0])
        cent = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
        rms = librosa.feature.rms(y=y, frame_length=sr * 3, hop_length=sr)[0]
        db = 20 * np.log10(rms[rms > 1e-4] + 1e-9)
        swing = float(np.percentile(db, 95) - np.percentile(db, 10)) if len(db) else 0
        out[f.stem] = {"len_s": round(full), "tempo": round(tempo), "onsets_per_s": round(len(onsets) / (len(y) / sr), 2),
                       "centroid_hz": round(cent), "presence_share": round(float(presence), 3), "swing_db": round(swing, 1)}
        o = out[f.stem]
        print(f"{f.stem:32s} {o['len_s']:4d}s tempo {o['tempo']:3d} onsets/s {o['onsets_per_s']:4.2f} centroid {o['centroid_hz']:5d} presence {o['presence_share']:.3f} swing {o['swing_db']:4.1f}dB")
    (ROOT / "picks" / "_raw" / "music_scores.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
