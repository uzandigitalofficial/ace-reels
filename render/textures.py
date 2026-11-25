"""Paper and cork textures for Reel Engine 6. Run once; outputs are committed in assets/paper/.
Usage: python render/textures.py
"""
import pathlib
import numpy as np
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "paper"


def blur(a, r):
    im = Image.fromarray(np.clip(a * 127 + 128, 0, 255).astype(np.uint8))
    return (np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) - 128) / 127


def paper(w, h, base, seed):
    g = np.random.default_rng(seed)
    grain = g.normal(0, 1, (h, w)).astype(np.float32)
    fine = blur(grain, 0.6) * 0.9
    cloud = blur(g.normal(0, 1, (h // 8, w // 8)).astype(np.float32), 6)
    cloud = np.asarray(Image.fromarray(np.clip(cloud * 127 + 128, 0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32)
    cloud = (cloud - 128) / 127
    fib = np.zeros((h, w), np.float32)
    for _ in range(900):
        x, y = g.integers(0, w), g.integers(0, h)
        ang, ln = g.uniform(0, np.pi), g.integers(8, 40)
        xs = (x + np.cos(ang) * np.arange(ln)).astype(int) % w
        ys = (y + np.sin(ang) * np.arange(ln)).astype(int) % h
        fib[ys, xs] += g.uniform(-1, 1)
    fib = blur(fib, 0.7)
    yy, xx = np.mgrid[0:h, 0:w]
    vig = ((xx / w - 0.5) ** 2 + (yy / h - 0.5) ** 2 * 0.6)
    lum = fine * 2.2 + cloud * 5.0 + fib * 6.0 - vig * 22
    img = np.clip(np.array(base, np.float32)[None, None, :] + lum[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(img)


def cork(s, seed):
    g = np.random.default_rng(seed)
    base = np.array([196, 150, 104], np.float32)
    a = np.zeros((s, s), np.float32)
    for r, k in ((0.8, 1.0), (1.8, 1.6), (4, 1.2)):
        a += blur(g.normal(0, 1, (s, s)).astype(np.float32), r) * k
    spots = (g.random((s, s)) > 0.985).astype(np.float32)
    a -= blur(spots, 1.2) * 18
    img = np.clip(base[None, None, :] + a[..., None] * np.array([26, 22, 18]) , 0, 255).astype(np.uint8)
    return Image.fromarray(img)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # design-v6b: one warm cream paper (#F2EBDD) for every reel; navy ink sits on it
    paper(1080, 1920, (242, 235, 221), 4).save(OUT / "paper-cream.jpg", quality=86)
    print("textures written to", OUT)


if __name__ == "__main__":
    main()
