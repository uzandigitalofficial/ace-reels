"""Local preview loop: render scripts without the voice model, then make contact sheets.
python render/preview.py sv-092 sv-001 sv-008 [--out tmp/p2] [--voice]
"""
import argparse, glob, os, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+"); ap.add_argument("--out", default="tmp/p2"); ap.add_argument("--at", type=float, nargs="*", default=[])
    a = ap.parse_args()
    for i in a.ids:
        r = subprocess.run([sys.executable, str(ROOT / "render" / "render5.py"), "--id", i, "--preview", "--out", a.out], cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            print(i, "FAILED", r.stderr[-2000:]); continue
        mp4 = max(glob.glob(str(ROOT / a.out / f"*-{i}.mp4")), key=os.path.getmtime)
        subprocess.run([sys.executable, str(ROOT / "render" / "sheet.py"), mp4, "--fps", "1.5", "--cols", "7", "--w", "300", "--at", *map(str, a.at)], cwd=ROOT, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
