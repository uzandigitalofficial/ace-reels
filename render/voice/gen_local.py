"""Local CPU voice candidates (same as a GitHub runner would do). Writes raw WAVs to picks/_raw/voice/.
Usage: python render/voice/gen_local.py kokoro | chatterbox"""
import pathlib
import sys
import time

import numpy as np
import soundfile as sf

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "picks" / "_raw" / "voice"
RAW.mkdir(parents=True, exist_ok=True)
SCRIPT = ("Are you on Google? Search for your business like a customer would. "
          "If you can't find yourself, neither can they. Set up your free Business Profile tonight.")


def kokoro():
    from kokoro import KPipeline
    pipe = KPipeline(lang_code="a")
    # af_heart is the production fallback; af_bella and af_nicole are the other top-graded US female voices
    for voice in ["af_heart", "af_bella", "af_nicole"]:
        t0 = time.time()
        parts = [np.asarray(r.audio, dtype=np.float32) for r in pipe(SCRIPT, voice=voice, speed=1.0)]
        a = np.concatenate(parts)
        sf.write(RAW / f"kokoro_{voice}.wav", a, 24000)
        print("ok", voice, f"{len(a) / 24000:.1f}s audio in {time.time() - t0:.1f}s")
    pipe_b = KPipeline(lang_code="b")
    a = np.concatenate([np.asarray(r.audio, dtype=np.float32) for r in pipe_b(SCRIPT, voice="bf_emma", speed=1.0)])
    sf.write(RAW / "kokoro_bf_emma.wav", a, 24000); print("ok bf_emma")


def chatterbox():
    import torch
    from chatterbox.tts import ChatterboxTTS
    torch.manual_seed(7)
    m = ChatterboxTTS.from_pretrained(device="cpu")
    for stem, ex, cfg, tp in [("cb_current", 0.62, 0.42, 0.75), ("cb_calm", 0.40, 0.50, 0.70), ("cb_warm_slow", 0.30, 0.30, 0.60)]:
        if (RAW / f"{stem}.wav").exists():
            continue
        t0 = time.time(); torch.manual_seed(7)
        w = m.generate(SCRIPT, exaggeration=ex, cfg_weight=cfg, temperature=tp)
        sf.write(RAW / f"{stem}.wav", w.squeeze().numpy(), m.sr); print("ok", stem, f"{time.time() - t0:.1f}s")


def turbo():
    """Chatterbox Turbo (350M, MIT) with its built-in voice; faster on CPU than the original."""
    import torch
    from chatterbox.tts_turbo import ChatterboxTurboTTS
    m = ChatterboxTurboTTS.from_pretrained(device="cpu")
    for stem, tp in [("cb_turbo", 0.7)]:
        t0 = time.time(); torch.manual_seed(7)
        w = m.generate(SCRIPT, temperature=tp)
        a = w.squeeze().numpy()
        sf.write(RAW / f"{stem}.wav", a, m.sr); print("ok", stem, f"{len(a) / m.sr:.1f}s audio in {time.time() - t0:.1f}s")


def cb_timing():
    """Time the original Chatterbox on this CPU for the speed column."""
    import torch
    from chatterbox.tts import ChatterboxTTS
    m = ChatterboxTTS.from_pretrained(device="cpu")
    t0 = time.time(); torch.manual_seed(7)
    w = m.generate(SCRIPT, exaggeration=0.4, cfg_weight=0.5, temperature=0.7)
    a = w.squeeze().numpy()
    sf.write(RAW / "_cb_calm_cpu.wav", a, m.sr); print("cpu", f"{len(a) / m.sr:.1f}s audio in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    globals()[sys.argv[1]]()
