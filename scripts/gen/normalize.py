"""Re-frames every cut-out the same way so all dishes look equally big on the podium:
tight crop to the dish, longest side = 94% of the square, centred horizontally, standing on the
same baseline (2% from the bottom). Masters: assets-src/cutouts/*.png (1200 px).
usage (venv with Pillow): python normalize.py <assets-src/cutouts> <images/cut>"""
import sys
from pathlib import Path
from PIL import Image

src, out = Path(sys.argv[1]), Path(sys.argv[2])
only = set(sys.argv[3:])
S, FILL, TALL, BASE = 1200, 0.94, 0.84, 0.02
import numpy as np


def trim_plate(im):
    """Sandwich box shots: the wide plate made the sandwich look small next to cups and plates.
    Keep the plate only around the box (1.7x its width) and fade it out softly at the sides."""
    a = np.array(im.getchannel("A")).astype(float)
    H, W = a.shape
    rows = [(a[y] > 128).sum() for y in range(int(H * .45), int(H * .66))]
    box = max(min(rows), W * .2)                      # narrowest row between sandwich and plate = the box
    cx = W / 2
    x = np.abs(np.arange(W) - cx)
    inner, outer = box * .85, box * 1.15
    g = np.clip((outer - x) / (outer - inner), 0, 1); g = g * g * (3 - 2 * g)
    plate = np.arange(H)[:, None] > H * .55
    a = np.where(plate, a * g[None, :], a)
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im.crop(im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox())

FIXED = {}
for p in sorted(src.glob("*.png")):
    if only and p.stem not in only:
        continue
    im = Image.open(p).convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    im = im.crop(bb)
    if p.stem.endswith("-brioche-1"):
        im = trim_plate(im)
    if p.stem in FIXED:
        f = FIXED[p.stem]
    elif im.height > im.width * 1.15:      # cups and cans: a bit lower, so they don't tower over plates
        f = S * TALL / im.height
    else:
        f = S * FILL / max(im.size)
    im = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
    can = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    can.paste(im, ((S - im.width) // 2, round(S * (1 - BASE)) - im.height), im)
    for w in (500, 900):
        can.resize((w, w), Image.LANCZOS).save(out / f"{p.stem}-{w}.webp", "WEBP", quality=84, method=6)
    print(p.stem, im.size)
