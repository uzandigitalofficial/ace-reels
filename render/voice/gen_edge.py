"""Voice candidates from Microsoft neural voices (edge-tts). Writes raw MP3s to picks/_raw/voice/.
Usage: python render/voice/gen_edge.py"""
import asyncio
import pathlib

import edge_tts

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "picks" / "_raw" / "voice"
SCRIPT = ("Are you on Google? Search for your business like a customer would. "
          "If you can't find yourself, neither can they. Set up your free Business Profile tonight.")

# (file stem, voice, rate, pitch)
VOICES = [
    ("edge_ava_multi", "en-US-AvaMultilingualNeural", "-4%", "+0Hz"),
    ("edge_emma_multi", "en-US-EmmaMultilingualNeural", "-4%", "+0Hz"),
    ("edge_ava", "en-US-AvaNeural", "-4%", "+0Hz"),
    ("edge_jenny", "en-US-JennyNeural", "-4%", "+0Hz"),
    ("edge_aria", "en-US-AriaNeural", "-4%", "+0Hz"),
    ("edge_sonia_gb", "en-GB-SoniaNeural", "-4%", "+0Hz"),
    ("edge_libby_gb", "en-GB-LibbyNeural", "-4%", "+0Hz"),
    ("edge_leah_za", "en-ZA-LeahNeural", "-4%", "+0Hz"),
]


async def one(stem, voice, rate, pitch):
    out = RAW / f"{stem}.mp3"
    for attempt in range(3):
        try:
            await edge_tts.Communicate(SCRIPT, voice, rate=rate, pitch=pitch).save(str(out))
            print("ok", stem, out.stat().st_size)
            return
        except Exception as e:  # network blips: retry with backoff
            print("retry", stem, repr(e)[:200])
            await asyncio.sleep(1.5 * (attempt + 1))
    print("FAILED", stem)


async def main():
    RAW.mkdir(parents=True, exist_ok=True)
    for v in VOICES:
        await one(*v)


if __name__ == "__main__":
    asyncio.run(main())
