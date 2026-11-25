"""Build the pick sheet audio: every voice and music candidate normalised to -16 LUFS, a sound-design kit,
a sound-design-only demo and 3 mixes (voice on top, music about 24 dB under it).
Usage: python render/music/build_picks.py   (reads picks/_raw, writes picks/voice, picks/music, picks/sfx, picks/mix)"""
import json
import pathlib
import subprocess
import tempfile

import librosa
import numpy as np
import pyloudnorm as pyln
import soundfile as sf

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "picks" / "_raw"
OUT = ROOT / "picks"
SR = 48000
TARGET = -16.0
MUSIC_UNDER = 24.0  # dB the music bed sits under the voice
meter = pyln.Meter(SR)

# id, raw stem, engine, one line for the sheet
VOICES = [
    ("V1", "edge_ava_multi", "Microsoft Ava Multilingual (edge-tts)", "US, warm and expressive, the most natural Microsoft voice. Free, no key, runs anywhere."),
    ("V2", "edge_emma_multi", "Microsoft Emma Multilingual (edge-tts)", "US, bright, clear and chatty. Free, no key."),
    ("V3", "edge_ava", "Microsoft Ava (edge-tts)", "Same speaker as V1, older model, a touch flatter."),
    ("V4", "edge_jenny", "Microsoft Jenny (edge-tts)", "US, friendly and even, classic assistant style."),
    ("V5", "edge_aria", "Microsoft Aria (edge-tts)", "US, confident newsreader style."),
    ("V6", "edge_sonia_gb", "Microsoft Sonia (edge-tts)", "British, polished and calm."),
    ("V7", "edge_libby_gb", "Microsoft Libby (edge-tts)", "British, soft and young."),
    ("V8", "edge_leah_za", "Microsoft Leah (edge-tts)", "South African English, local accent."),
    ("V9", "cb_current", "Chatterbox, current settings", "What the reels use now (exaggeration 0.62, cfg 0.42). For comparison."),
    ("V10", "cb_calm", "Chatterbox, calm", "Exaggeration 0.40, cfg 0.50: steadier, less sing-song."),
    ("V11", "cb_warm_slow", "Chatterbox, warm and slow", "Exaggeration 0.30, cfg 0.30, temperature 0.60: slowest and softest Chatterbox."),
    ("V12", "cb_turbo", "Chatterbox Turbo", "Resemble's newer, faster model with its built-in voice."),
    ("V13", "kokoro_af_heart", "Kokoro, Heart", "The current backup voice. Tiny, fast, clean, slightly smooth."),
    ("V14", "kokoro_af_bella", "Kokoro, Bella", "Kokoro's other top US female voice, a bit brighter."),
    ("V15", "kokoro_af_nicole", "Kokoro, Nicole", "Breathy, close-mic, slow. Intimate, not for every reel."),
    ("V16", "kokoro_bf_emma", "Kokoro, Emma (British)", "British Kokoro voice, crisp."),
]

# id, raw stem, start seconds, title, one line
MUSIC = [
    # Chosen from 21 downloads by measurement (render/music/score.py): least energy in the 1 to 4 kHz speech band,
    # few note attacks per second, and a steady level, so the voice stays on top.
    ("M1", "gymnopedie_no_1", None, "Gymnopedie No 1", "Satie's soft solo piano. About one note a second, calm and elegant."),
    ("M2", "sincerely", None, "Sincerely", "Slow, warm and low. Almost nothing in the voice range."),
    ("M3", "lightless_dawn", None, "Lightless Dawn", "Very slow ambient piano and texture, reflective."),
    ("M4", "windswept", None, "Windswept", "Airy, even ambient bed with very steady level."),
    ("M5", "fresh_air", None, "Fresh Air", "The sparsest track tested: long soft tones, hardly any attacks."),
    ("M6", "perspectives", None, "Perspectives", "Gentle, even, slightly more motion. Keeps a reel moving."),
]
MUSIC_BY_STEM = {m[1]: m for m in MUSIC}


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, args)], check=True)


def load(path, sr=SR, mono=True):
    tmp = pathlib.Path(tempfile.gettempdir()) / f"bp_{path.stem}.wav"
    ff("-i", path, "-ac", 1 if mono else 2, "-ar", sr, "-c:a", "pcm_f32le", tmp)
    y, _ = sf.read(tmp, dtype="float32")
    return y


def to_lufs(y, target):
    g = target - meter.integrated_loudness(y)
    return y * (10 ** (g / 20))


def save_mp3(y, dst, limit=True):
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.gettempdir()) / f"bp_out_{dst.stem}.wav"
    sf.write(tmp, y.astype(np.float32), SR, subtype="FLOAT")
    af = ["-af", "alimiter=limit=0.89:level=false:attack=2:release=60"] if limit else []
    ff("-i", tmp, *af, "-c:a", "libmp3lame", "-b:a", "192k", dst)
    chk = load(dst)
    if len(chk) <= SR * 0.5:
        return None
    got = meter.integrated_loudness(chk)
    if limit and abs(got - TARGET) > 0.3 and abs(meter.integrated_loudness(y) - TARGET) < 0.3:
        return save_mp3(y * 10 ** ((TARGET - got) / 20), dst, limit)  # the limiter ate some level: add it back once
    return round(got, 1)


def trim(y, pad=0.12):
    _, (a, b) = librosa.effects.trim(y, top_db=40)
    p = int(pad * SR)
    return y[max(0, a - p):min(len(y), b + p)]


def fade(y, fin=0.02, fout=0.05):
    y = y.copy(); i, o = int(fin * SR), int(fout * SR)
    if i: y[:i] *= np.linspace(0, 1, i)
    if o: y[-o:] *= np.linspace(1, 0, o)
    return y


# ---------- sound design kit: CC0 files plus two made here from scratch (no licence needed)
def synth_whoosh(dur=0.55, seed=1):
    rng = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n).astype(np.float32)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2.2
    out = np.zeros(n, np.float32); state = 0.0
    cut = 600 + 3400 * np.sin(np.pi * t / dur)  # filter sweeps up then down, like air moving past
    a = np.exp(-2 * np.pi * cut / SR)
    for k in range(n):
        state = (1 - a[k]) * noise[k] + a[k] * state; out[k] = state
    out = out - np.convolve(out, np.ones(64) / 64, "same")  # take out rumble
    return fade((out * env / (np.max(np.abs(out * env)) + 1e-9)).astype(np.float32), 0.005, 0.05)


def synth_riser(dur=1.6, seed=2):
    rng = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    env = (t / dur) ** 2.5
    f = 220 * (2 ** (2.0 * t / dur)); ph = 2 * np.pi * np.cumsum(f) / SR
    tone = 0.35 * np.sin(ph) + 0.2 * np.sin(2 * ph) + 0.1 * np.sin(3.01 * ph)
    noise = rng.standard_normal(n); hp = noise - np.convolve(noise, np.ones(24) / 24, "same")
    y = (tone + 0.25 * hp * (t / dur)) * env
    return fade((y / np.max(np.abs(y))).astype(np.float32), 0.01, 0.03)


SFX = {  # name: (source, gain dB relative to voice when used)
    "whoosh": ("synth", -14), "riser": ("synth", -20), "paper": ("sfx_dl/RPGsounds_Kenney__bookFlip2.ogg", -12),
    "paper2": ("sfx_dl/book_flips_-_starninjas__book_flip.3.ogg", -12), "pop": ("sfx/kenney_drop_002.wav", -12),
    "click": ("sfx/kenney_click_001.wav", -14),
}


def sfx_bank():
    bank = {}
    for name, (src, _) in SFX.items():
        if src == "synth":
            y = synth_whoosh() if name == "whoosh" else synth_riser()
        else:
            y = trim(load(RAW / src), 0.01)
        bank[name] = to_lufs(fade(y, 0.002, 0.03), -16) if len(y) > SR * 0.4 else y / (np.max(np.abs(y)) + 1e-9) * 0.5
        save_mp3(bank[name], OUT / "sfx" / f"{name}.mp3")
    return bank


def words(y):
    from faster_whisper import WhisperModel
    wm = WhisperModel("base.en", device="cpu", compute_type="int8")
    segs, _ = wm.transcribe(librosa.resample(y, orig_sr=SR, target_sr=16000), word_timestamps=True, language="en")
    return [(w.word.strip(" ,.?!").lower(), w.start, w.end) for s in segs for w in s.words]


def place(bed, clip, at, gain_db):
    i = int(max(0, at) * SR); j = min(len(bed), i + len(clip))
    if j > i:
        bed[i:j] += clip[:j - i] * (10 ** (gain_db / 20))


def design(voice, lead, bank):
    """Sound design cues from the voice's own word times: whoosh in, paper on the second idea, pop on the turn,
    a soft riser into the call to action and a click on it."""
    w = words(voice)
    def at(word, default):
        return next((s for x, s, _ in w if x == word), default)
    n = len(voice) + int((lead + 1.5) * SR)
    fx = np.zeros(n, np.float32)
    vg = meter.integrated_loudness(voice)
    rel = lambda clip, dbrel: dbrel + (vg - meter.integrated_loudness(clip) if len(clip) > SR * 0.4 else -6)
    place(fx, bank["whoosh"], lead - 0.35, rel(bank["whoosh"], SFX["whoosh"][1]))
    place(fx, bank["paper"], lead + at("search", 1.2) - 0.08, rel(bank["paper"], SFX["paper"][1]))
    place(fx, bank["pop"], lead + at("if", 3.5) - 0.03, rel(bank["pop"], SFX["pop"][1]))
    s = at("set", 6.0)
    place(fx, bank["riser"], lead + s - len(bank["riser"]) / SR, rel(bank["riser"], SFX["riser"][1]))
    place(fx, bank["click"], lead + s - 0.02, rel(bank["click"], SFX["click"][1]))
    return fx


def mix(voice, music, bank, with_fx=True, lead=0.6, tail=1.6):
    v = np.concatenate([np.zeros(int(lead * SR), np.float32), voice, np.zeros(int(tail * SR), np.float32)])
    out = v.copy()
    if music is not None:
        m = np.resize(music, len(v)).astype(np.float32)
        vl = meter.integrated_loudness(voice)
        m = to_lufs(m, vl - MUSIC_UNDER)
        m[: int(0.8 * SR)] *= np.linspace(0, 1, int(0.8 * SR)); m[-int(1.4 * SR):] *= np.linspace(1, 0, int(1.4 * SR))
        out += m
    if with_fx:
        fx = design(voice, lead, bank); out[: len(fx)] += fx[: len(out)]
    return to_lufs(out, TARGET)


def main():
    rec = {"voices": [], "music": [], "sfx": [], "mixes": []}
    voices = {}
    for vid, stem, engine, line in VOICES:
        f = next((RAW / "voice" / f"{stem}{e}" for e in (".wav", ".mp3") if (RAW / "voice" / f"{stem}{e}").exists()), None)
        if not f:
            print("skip missing", stem); continue
        y = fade(trim(load(f)))
        y = to_lufs(y, TARGET); voices[vid] = y
        lufs = save_mp3(y, OUT / "voice" / f"{vid}.mp3")
        rec["voices"].append({"id": vid, "file": f"voice/{vid}.mp3", "engine": engine, "line": line, "raw": f.name, "lufs": lufs, "secs": round(len(y) / SR, 1)})
        print(vid, stem, lufs, "LUFS")
    src = {s["file"]: s for s in json.loads((RAW / "sources_raw.json").read_text(encoding="utf-8"))}
    music = {}
    for mid, stem, start, title, line in MUSIC:
        y = load(RAW / "music" / f"{stem}.mp3")
        if start is None:  # skip a quiet intro: start at the first second within 6 dB of the track's typical level
            sec = np.array([np.sqrt(np.mean(y[i:i + SR] ** 2) + 1e-12) for i in range(0, len(y) - SR, SR)])
            db = 20 * np.log10(sec); start = int(np.argmax(db >= np.median(db) - 6))
        y = y[int(start * SR): int((start + 30) * SR)]
        y[: SR] *= np.linspace(0, 1, SR); y[-3 * SR:] *= np.linspace(1, 0, 3 * SR)
        y = to_lufs(y, TARGET); music[mid] = y
        lufs = save_mp3(y, OUT / "music" / f"{mid}.mp3")
        s = src[f"{stem}.mp3"]
        rec["music"].append({"id": mid, "file": f"music/{mid}.mp3", "title": title, "artist": s["artist"], "line": line, "source": s["source"],
                             "page": s["page"], "licence": s["licence"], "attribution": s["attribution"], "lufs": lufs})
        print(mid, title, lufs, "LUFS")
    bank = sfx_bank()
    best = json.loads((RAW / "best.json").read_text(encoding="utf-8")) if (RAW / "best.json").exists() else {"voices": ["V1", "V2", "V13"], "music": "M1"}
    v0 = best["voices"][0]
    lufs = save_mp3(mix(voices[v0], None, bank, with_fx=True), OUT / "music" / "M_sfx.mp3")
    rec["music"].append({"id": "Sound design only", "file": "music/M_sfx.mp3", "title": f"No music, sound design only (with {v0})",
                         "line": "Soft whoosh in, page flip, a pop on the turn, a gentle riser and click into the call to action.", "lufs": lufs})
    lufs = save_mp3(mix(voices[v0], None, bank, with_fx=False), OUT / "music" / "M_none.mp3")
    rec["music"].append({"id": "No music", "file": "music/M_none.mp3", "title": f"No music, voice only ({v0})", "line": "Just the voice. Clean and direct.", "lufs": lufs})
    for k, vid in enumerate(best["voices"], 1):
        lufs = save_mp3(mix(voices[vid], music[best["music"]], bank), OUT / "mix" / f"MIX{k}.mp3")
        rec["mixes"].append({"id": f"MIX{k}", "file": f"mix/MIX{k}.mp3", "voice": vid, "music": best["music"], "lufs": lufs})
        print("MIX", k, vid, lufs)
    rec["sfx_sources"] = {k: v[0] for k, v in SFX.items()}
    (OUT / "picks.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
