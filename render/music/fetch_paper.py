"""Download CC0 paper and page-flip sounds from OpenGameArt into picks/_raw/sfx_dl (audio files only are extracted)."""
import io
import json
import pathlib
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
DL = ROOT / "picks" / "_raw" / "sfx_dl"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0"
OGA = "https://opengameart.org/sites/default/files/"
ITEMS = [
    ("book_flips_-_starninjas.zip", "https://opengameart.org/node/123492", "10 Book Page Flips, by starninjas"),
    ("RPGsounds_Kenney.zip", "https://opengameart.org/content/50-rpg-sound-effects", "50 RPG sound effects, by Kenney"),
    ("paper_sound_-_1.mp3", "https://opengameart.org/node/127323", "Various Paper Sound Effects"),
    ("paper_sound_-_2.mp3", "https://opengameart.org/node/127323", "Various Paper Sound Effects"),
    ("paper_sound_-_3.mp3", "https://opengameart.org/node/127323", "Various Paper Sound Effects"),
    ("paper_sound_-_4.mp3", "https://opengameart.org/node/127323", "Various Paper Sound Effects"),
]


def main():
    DL.mkdir(parents=True, exist_ok=True)
    rec = []
    for name, page, title in ITEMS:
        data = urllib.request.urlopen(urllib.request.Request(OGA + name, headers={"User-Agent": UA}), timeout=60).read()
        if name.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for m in z.namelist():
                    if m.lower().endswith((".wav", ".ogg", ".mp3")) and ".." not in m:
                        dst = DL / (pathlib.Path(name).stem + "__" + pathlib.Path(m).name)
                        dst.write_bytes(z.read(m)); rec.append({"file": dst.name, "source": OGA + name, "page": page, "title": title, "licence": "CC0 1.0"})
        else:
            dst = DL / name; dst.write_bytes(data)
            rec.append({"file": dst.name, "source": OGA + name, "page": page, "title": title, "licence": "CC0 1.0"})
        print("ok", name, len(data))
    (DL / "sources.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print("\n".join(r["file"] for r in rec))


if __name__ == "__main__":
    main()
