"""Contact sheets for checking a reel frame by frame.
python render/sheet.py out/x.mp4 [--fps 2] [--cols 8] [--at 1.2 3.4 ...]
Writes x.sheet.jpg (thumbnails) and x.at-<t>.jpg full frames for each --at time.
"""
import argparse, pathlib, subprocess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mp4"); ap.add_argument("--fps", type=float, default=2); ap.add_argument("--cols", type=int, default=8)
    ap.add_argument("--w", type=int, default=270); ap.add_argument("--at", type=float, nargs="*", default=[])
    a = ap.parse_args()
    src = pathlib.Path(a.mp4)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout)
    rows = int(dur * a.fps / a.cols) + 1
    sheet = src.with_suffix(".sheet.jpg")
    vf = f"fps={a.fps},scale={a.w}:-1,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.5,tile={a.cols}x{rows}:padding=4:color=white"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", vf, "-frames:v", "1", "-q:v", "3", str(sheet)], check=True)
    print(sheet)
    for t in a.at:
        out = src.with_name(f"{src.stem}.at-{t:05.2f}.jpg")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1", "-q:v", "3", "-vf", "scale=540:-1", str(out)], check=True)
        print(out)


if __name__ == "__main__":
    main()
