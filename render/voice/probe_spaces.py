"""Print the Gradio API of candidate public Hugging Face Spaces so we know how to call them."""
import sys

from gradio_client import Client

SPACES = sys.argv[1:] or [
    "ResembleAI/Chatterbox", "ResembleAI/chatterbox-turbo-demo", "hexgrad/Kokoro-TTS",
    "IndexTeam/IndexTTS-2-Demo", "mrfakename/E2-F5-TTS", "nari-labs/Dia-1.6B",
    "sesame/csm-1b", "smola/higgs_audio_v2", "canopylabs/orpheus-tts", "microsoft/VibeVoice",
]
for s in SPACES:
    print("=" * 30, s)
    try:
        c = Client(s, verbose=False)
        c.view_api(print_info=True)
    except Exception as e:
        print("ERR", repr(e)[:300])
