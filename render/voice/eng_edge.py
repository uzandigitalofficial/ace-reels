"""Microsoft neural voices through edge-tts, shaped like the engines in render/render5.py: (texts, cfg) -> (takes, sr).
Not registered yet. To switch on, add to render5.py:  from voice.eng_edge import eng_edge ; ENGINES["edge"] = eng_edge
(or paste the function next to eng_kokoro) and set "tts": {"engine": "edge", "voice": "en-US-AvaMultilingualNeural"}."""
import asyncio
import os
import subprocess
import tempfile

import numpy as np
import soundfile as sf


def eng_edge(texts, cfg):
    import edge_tts
    voice = cfg.get("voice", "en-US-AvaMultilingualNeural")
    rate = cfg.get("rate", "-4%")
    out = []
    with tempfile.TemporaryDirectory() as d:
        for k, t in enumerate(texts):
            mp3, wav = os.path.join(d, f"t{k}.mp3"), os.path.join(d, f"t{k}.wav")
            for attempt in range(4):  # the service drops a request now and then
                try:
                    asyncio.run(edge_tts.Communicate(t, voice, rate=rate).save(mp3)); break
                except Exception:
                    if attempt == 3:
                        raise
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ac", "1", "-ar", "24000", wav], check=True)
            a, _ = sf.read(wav, dtype="float32"); out.append(np.asarray(a, dtype=np.float32))
    return out, 24000
