"""Voice candidates from free public Hugging Face Spaces (no account, no key).
Writes raw audio to picks/_raw/voice/. Run one job: python render/voice/gen_spaces.py chatterbox
Jobs: ref, chatterbox, turbo, higgs, csm, dia, kokoro"""
import pathlib
import shutil
import sys
import time

from gradio_client import Client, handle_file

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "picks" / "_raw" / "voice"
RAW.mkdir(parents=True, exist_ok=True)
SCRIPT = ("Are you on Google? Search for your business like a customer would. "
          "If you can't find yourself, neither can they. Set up your free Business Profile tonight.")
# Reference clip: the built-in Chatterbox voice (MIT) reading a neutral line, so cloning models copy a voice we own.
REF_TEXT = ("Hi, thanks for stopping by. Today I want to show you one small change that brings in more customers, "
            "and it only takes a few minutes.")
REF = RAW / "_ref_chatterbox.wav"


def keep(result, stem):
    src = result[-1] if isinstance(result, (list, tuple)) else result
    if isinstance(src, dict):
        src = src.get("path") or src.get("value")
    src = pathlib.Path(src)
    dst = RAW / f"{stem}{src.suffix or '.wav'}"
    shutil.copy(src, dst)
    print("ok", stem, dst.stat().st_size)


def retry(fn, tries=3):
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            print("retry", i + 1, repr(e)[:300])
            time.sleep(8 * (i + 1))
    print("FAILED")


def chatterbox():
    c = Client("ResembleAI/Chatterbox", verbose=False)
    # (stem, exaggeration, temperature, cfg_weight): production settings, calmer, slow and warm
    for stem, ex, tp, cfg in [("cb_current", 0.62, 0.75, 0.42), ("cb_calm", 0.40, 0.70, 0.50), ("cb_warm_slow", 0.30, 0.60, 0.30)]:
        retry(lambda: keep(c.predict(SCRIPT, None, ex, tp, 7, cfg, True, api_name="/generate_tts_audio"), stem))


def ref():
    c = Client("ResembleAI/Chatterbox", verbose=False)
    retry(lambda: keep(c.predict(REF_TEXT, None, 0.45, 0.7, 7, 0.5, True, api_name="/generate_tts_audio"), "_ref_chatterbox"))


def turbo():
    c = Client("ResembleAI/chatterbox-turbo-demo", verbose=False)
    retry(lambda: keep(c.predict(SCRIPT, handle_file(str(REF)), 0.7, 7, 0.0, 0.95, 1000, 1.2, True, api_name="/generate"), "cb_turbo"))


def higgs():
    c = Client("smola/higgs_audio_v2", verbose=False)
    for stem, preset in [("higgs_en_woman", "en_woman"), ("higgs_belinda", "belinda")]:
        retry(lambda: keep(c.predict(SCRIPT, preset, None, None, 1024, 0.8, 0.95, 50, api_name="/generate_speech"), stem))


def csm():
    c = Client("sesame/csm-1b", verbose=False)
    for spk in ["read_speech_a", "read_speech_b", "read_speech_c", "read_speech_d", "conversational_a", "conversational_b"]:
        a = c.predict(spk, api_name="/update_audio"); t = c.predict(spk, api_name="/update_text")
        shutil.copy(a, RAW / f"_csm_prompt_{spk}.wav"); print(spk, t[:80])
    spk = sys.argv[2] if len(sys.argv) > 2 else "read_speech_a"
    a = c.predict(spk, api_name="/update_audio"); t = c.predict(spk, api_name="/update_text")
    retry(lambda: keep(c.predict(t, t, handle_file(a), handle_file(a), SCRIPT, api_name="/infer"), f"csm_{spk}"))


def dia():
    c = Client("nari-labs/Dia-1.6B", verbose=False)
    retry(lambda: keep(c.predict("[S1] " + REF_TEXT + " [S1] " + SCRIPT, handle_file(str(REF)), "[S1] " + REF_TEXT,
                                 3072, 3.0, 1.3, 0.95, 45, 0.94, api_name="/generate_audio"), "dia"))


def kokoro():
    c = Client("remsky/Kokoro-TTS-Zero", verbose=False)
    c.view_api(print_info=True)


if __name__ == "__main__":
    globals()[sys.argv[1]]()
