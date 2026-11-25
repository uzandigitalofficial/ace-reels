"""Pick sheet voices (v7b): the same Stolen Valour script read by six engines. Raw files go to picks/_raw/v7b/.
Usage: python render/voice/gen_v7b.py edge | kokoro | chatterbox"""
import asyncio
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "picks" / "_raw" / "v7b"
RAW.mkdir(parents=True, exist_ok=True)
SCRIPT = ("Most car buyers choose a dealership before they ever make a call. "
          "They search on their phone, and they pick the site that looks clear and trustworthy. "
          "Stolen Valour builds that website for your dealership in seven days. "
          "Message us on WhatsApp tonight, and be the one they find.")
EDGE = [("V1", "en-US-AvaMultilingualNeural"), ("V2", "en-US-EmmaMultilingualNeural"),
        ("V3", "en-GB-SoniaNeural"), ("V4", "en-ZA-LeahNeural")]


def edge():
    import edge_tts

    async def run():
        for vid, voice in EDGE:
            for attempt in range(4):
                try:
                    await edge_tts.Communicate(SCRIPT, voice, rate="-4%").save(str(RAW / f"{vid}.mp3"))
                    print("ok", vid, voice); break
                except Exception as e:
                    print("retry", vid, repr(e)[:150]); await asyncio.sleep(2 * (attempt + 1))
    asyncio.run(run())


def kokoro():
    import numpy as np
    import soundfile as sf
    from kokoro import KPipeline
    pipe = KPipeline(lang_code="a")
    a = np.concatenate([np.asarray(r.audio, dtype=np.float32) for r in pipe(SCRIPT.replace("Valour", "Valor"), voice="af_heart", speed=1.0)])
    sf.write(RAW / "V5.wav", a, 24000); print("ok V5", len(a) / 24000)


def chatterbox():
    import soundfile as sf
    import torch
    from chatterbox.tts import ChatterboxTTS
    m = ChatterboxTTS.from_pretrained(device="cpu")
    torch.manual_seed(7); t0 = time.time()
    w = m.generate(SCRIPT, exaggeration=0.40, cfg_weight=0.50, temperature=0.70)
    sf.write(RAW / "V6.wav", w.squeeze().numpy(), m.sr); print("ok V6", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    globals()[sys.argv[1]]()
