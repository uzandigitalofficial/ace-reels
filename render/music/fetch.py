"""Download candidate music beds (Incompetech, Kevin MacLeod, CC-BY 4.0) and CC0 sound effects (Kenney)
into picks/_raw/music and picks/_raw/sfx. Records every source URL and licence in picks/_raw/sources_raw.json."""
import json
import pathlib
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "picks" / "_raw"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0"

MUSIC = ["Meditation Impromptu 01", "Gymnopedie No 1", "Floating Cities", "Dream Culture", "Windswept",
         "Heart of Nowhere", "Easy Lemon", "Carefree", "Dreamer", "Lightless Dawn", "Bathed in the Light",
         "Reaching Out", "Perspectives", "Cipher", "Touching Moments Two - Higher", "Healing", "Wholesome",
         "Clean Soul", "Ethereal Relaxation", "Inspired", "Fresh Air", "Sincerely"]
INC = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/"
KENNEY = "https://raw.githubusercontent.com/Calinou/kenney-interface-sounds/master/addons/kenney_interface_sounds/"
SFX = ["click_001", "click_002", "click_003", "tick_001", "drop_001", "drop_002", "drop_003", "pluck_001", "pluck_002",
       "select_001", "scroll_001", "scroll_002", "scroll_003", "minimize_001", "minimize_005", "maximize_001",
       "maximize_005", "switch_001", "switch_002", "glass_001", "bong_001", "confirmation_001"]


def get(url, dst):
    for i in range(3):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read()
            if len(data) < 2000:
                raise ValueError(f"too small: {len(data)}")
            dst.write_bytes(data)
            return True
        except Exception as e:
            print("  retry", i + 1, url[-60:], repr(e)[:120])
            time.sleep(2 * (i + 1))
    return False


def main():
    (RAW / "music").mkdir(parents=True, exist_ok=True); (RAW / "sfx").mkdir(parents=True, exist_ok=True)
    rec = []
    for t in MUSIC:
        url = INC + urllib.parse.quote(t) + ".mp3"
        dst = RAW / "music" / (t.lower().replace(" ", "_").replace("-", "") + ".mp3")
        if dst.exists() or get(url, dst):
            print("ok", t, dst.stat().st_size)
            rec.append({"kind": "music", "file": dst.name, "title": t, "artist": "Kevin MacLeod", "source": url,
                        "page": "https://incompetech.com/music/royalty-free/music.html", "licence": "CC-BY 4.0",
                        "attribution": f'"{t}" Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution 4.0 License. http://creativecommons.org/licenses/by/4.0/'})
        else:
            print("MISSING", t)
    for s in SFX:
        dst = RAW / "sfx" / f"kenney_{s}.wav"
        if dst.exists() or get(KENNEY + s + ".wav", dst):
            rec.append({"kind": "sfx", "file": dst.name, "title": s, "artist": "Kenney (kenney.nl), Interface Sounds",
                        "source": KENNEY + s + ".wav", "page": "https://kenney.nl/assets/interface-sounds", "licence": "CC0 1.0"})
            print("ok", s)
        else:
            print("MISSING", s)
    (RAW / "sources_raw.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
