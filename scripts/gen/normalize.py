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
    ys = list(range(int(H * .45), int(H * .66)))
    rows = [(a[y] > 128).sum() for y in ys]
    yb = ys[int(np.argmin(rows))]
    box = max(min(rows), W * .2)                      # narrowest row between sandwich and plate = the box
    xs = np.where(a[yb] > 128)[0]
    cx = (xs[0] + xs[-1]) / 2 if len(xs) else W / 2  # centre of the box, not of the photo
    x = np.abs(np.arange(W) - cx)
    inner, outer = box * .85, box * 1.15
    g = np.clip((outer - x) / (outer - inner), 0, 1); g = g * g * (3 - 2 * g)
    plate = np.arange(H)[:, None] > H * .55
    a = np.where(plate, a * g[None, :], a)
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im.crop(im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox())

def largest_part(im):
    """Drop loose pieces the matting left next to the dish (bits of a second plate, crumbs)."""
    from scipy import ndimage
    a = np.array(im.getchannel("A"))
    lab, k = ndimage.label(a > 40)
    if k > 1:
        sizes = ndimage.sum(np.ones_like(a), lab, range(1, k + 1))
        keep = [i + 1 for i, sz in enumerate(sizes) if sz >= sizes.max() * 0.08]   # keep sauce cups etc.
        mask = ndimage.binary_dilation(np.isin(lab, keep), iterations=3)
        im.putalpha(Image.fromarray(np.where(mask, a, 0).astype(np.uint8)))
        im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox())
    return im


def trim_side_plate(im):
    """Sandwich side shots: plate and paper card make the photo wide, so the sandwich looks small.
    The sandwich's own width comes from the top 35% (bun + lettuce only); the picture is kept within
    that width (+3% each side) — width measured on coloured food pixels only and everything further out fades away softly."""
    a = np.array(im.getchannel("A")).astype(float)
    H, W = a.shape
    rgb = np.array(im.convert("RGB")).astype(float)
    mx, mn = rgb.max(2), rgb.min(2)
    r, g_, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    food = (a > 128) & ((mx - mn) / np.maximum(mx, 1) > .28) & (b < np.maximum(r, g_) - 12)   # warm/green food; not the white card or blue-grey plate
    counts = food.sum(0)
    cols = np.where(counts > max(3, counts.max() * .12))[0]
    if not len(cols):
        return im
    x0, x1 = cols[0], cols[-1]
    card = (a > 0) & ((mx - mn) / np.maximum(mx, 1) < .14) & (mn > 150)
    card[:, : int(x0 + (x1 - x0) * .7)] = False        # only on the far side of the sandwich
    a = np.where(card, 0, a)
    pad, ramp = (x1 - x0) * .03, (x1 - x0) * .09
    x = np.arange(W)
    d = np.maximum(x0 - pad - x, x - x1 - pad)
    g = np.clip(1 - d / ramp, 0, 1); g = g * g * (3 - 2 * g)
    a = a * g[None, :]
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im.crop(im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox())

FIXED = {}
# photos the photographer cropped on the left: fade that straight edge (fraction of the width)
SOFT_LEFT = {"salmon-salad-1": .07}
for p in sorted(src.glob("*.png")):
    if only and p.stem not in only:
        continue
    im = Image.open(p).convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    im = im.crop(bb)
    im = largest_part(im)
    if p.stem in SOFT_LEFT:
        a = np.array(im.getchannel("A")).astype(float)
        x = np.arange(a.shape[1]); g = np.clip(x / (a.shape[1] * SOFT_LEFT[p.stem]), 0, 1); g = g * g * (3 - 2 * g)
        im.putalpha(Image.fromarray((a * g[None, :]).astype(np.uint8)))
    if p.stem.endswith("-brioche-1"):
        im = trim_plate(im)
    elif p.stem.endswith("-brioche-2"):
        im = trim_side_plate(im)
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
