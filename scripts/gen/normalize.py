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
        keep = [i + 1 for i, sz in enumerate(sizes) if sz >= sizes.max() * 0.015]   # keep sauce cups etc.
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

def _fit_ellipse(x, y):
    """Least-squares ellipse (Fitzgibbon). Returns centre, axes, angle."""
    D = np.c_[x * x, x * y, y * y, x, y, np.ones_like(x)]
    S = D.T @ D
    C = np.zeros((6, 6)); C[0, 2] = C[2, 0] = 2; C[1, 1] = -1
    w, v = np.linalg.eig(np.linalg.solve(S, C))
    A, B, Cc, Dd, E, F = np.real(v[:, np.argmax(np.real(w))])
    den = B * B - 4 * A * Cc
    x0 = (2 * Cc * Dd - B * E) / den; y0 = (2 * A * E - B * Dd) / den
    th = .5 * np.arctan2(-B, Cc - A)
    num = 2 * (A * E * E + Cc * Dd * Dd - B * Dd * E + den * F)
    r1 = -np.sqrt(num * (A + Cc + np.sqrt((A - Cc) ** 2 + B * B))) / den
    r2 = -np.sqrt(num * (A + Cc - np.sqrt((A - Cc) ** 2 + B * B))) / den
    return x0, y0, r1, r2, th


def fill_plate(im, close_r=6):
    """Plates and bowls are ellipses (seen from above): the matting sometimes eats part of a bright
    rim against the white background. Fit an ellipse to the plate's outline (sauce cups and food
    sticking out are dropped as outliers) and make everything inside it opaque, using the photo's
    own pixels; pieces outside the plate (sauce cups) stay as they are."""
    from scipy import ndimage
    a = np.array(im.getchannel("A")).astype(float)
    f = 500 / max(im.size)
    small = np.array(im.getchannel("A").resize((max(1, round(im.width * f)), max(1, round(im.height * f))))) > 128
    small = ndimage.binary_fill_holes(small)
    def robust(x, y):
        keep = np.ones_like(x, bool)
        for _ in range(8):
            x0, y0, r1, r2, th = _fit_ellipse(x[keep], y[keep])
            c, s_ = np.cos(th), np.sin(th)
            u = ((x - x0) * c + (y - y0) * s_) / r1; v = (-(x - x0) * s_ + (y - y0) * c) / r2
            d = np.sqrt(u * u + v * v)                   # 1 = on the ellipse, >1 outside (cups, food)
            keep = d < np.quantile(d[keep], .8) + .01
        return x0, y0, r1, r2, th, d
    edge = small & ~ndimage.binary_erosion(small)
    ys, xs = np.nonzero(edge)
    x0, y0, r1, r2, th, d = robust(xs.astype(float), ys.astype(float))
    # drop pieces lying outside the rough plate (sauce cups), then use the convex hull of the rest:
    # it bridges the places where the rim was eaten by the matting
    lab, k = ndimage.label(small)
    yy, xx = np.mgrid[0:small.shape[0], 0:small.shape[1]].astype(float)
    u = ((xx - x0) * np.cos(th) + (yy - y0) * np.sin(th)) / r1
    v = (-(xx - x0) * np.sin(th) + (yy - y0) * np.cos(th)) / r2
    inside = np.sqrt(u * u + v * v) < 1.05
    plate = small & inside
    from scipy.spatial import ConvexHull
    py, px_ = np.nonzero(plate)
    hv = np.c_[px_, py][ConvexHull(np.c_[px_, py]).vertices].astype(float)
    pts = []
    for i in range(len(hv)):                             # densely sample the hull outline
        a0, a1 = hv[i], hv[(i + 1) % len(hv)]
        n = max(2, int(np.hypot(*(a1 - a0))))
        pts.append(a0 + (a1 - a0) * np.linspace(0, 1, n, endpoint=False)[:, None])
    pts = np.vstack(pts)
    x0, y0, r1, r2, th, d = robust(pts[:, 0], pts[:, 1])
    grow = min(np.quantile(d[d < 1.05], .9), 1.015)       # reach the real outer rim, never the background
    r1, r2 = r1 * grow, r2 * grow
    x0, y0, r1, r2 = x0 / f, y0 / f, r1 / f, r2 / f
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    u = ((xx - x0) * np.cos(th) + (yy - y0) * np.sin(th)) / r1
    v = (-(xx - x0) * np.sin(th) + (yy - y0) * np.cos(th)) / r2
    d = np.sqrt(u * u + v * v)
    px = 1.5 / min(r1, r2)                                # ~1.5 px soft edge
    # sauce cups: solid pieces outside the fitted plate, bigger than 0.5% of the image
    out_solid = (a > 200) & (d > 1.0)
    lab2, k2 = ndimage.label(ndimage.binary_opening(out_solid, iterations=3))
    cups = np.zeros_like(out_solid)
    if k2:
        sz = ndimage.sum(np.ones_like(a), lab2, range(1, k2 + 1))
        cups = ndimage.binary_dilation(np.isin(lab2, [i + 1 for i, z in enumerate(sz) if z > a.size * .005]), iterations=4)
    # grow the ellipse to the real outer rim: per direction, the farthest plate pixel (rim line
    # included) within 12% of the fit; the median over all directions is the true size
    plate = (a > 100) & ~cups
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    ang = np.arctan2(v, u)
    sel = plate & (d < 1.12)
    bins = ((ang[sel] + np.pi) / (2 * np.pi) * 180).astype(int).clip(0, 179)
    far = np.zeros(180)
    np.maximum.at(far, bins, d[sel])
    grow = float(np.median(far[far > 0])) if (far > 0).any() else 1.0
    d2 = d / grow
    m = np.clip((1 - d2) / px, 0, 1) * 255
    # plates are not perfect ellipses: also close the gap between the plate and its thin outer
    # rim line (both kept by the matting) and fill everything they enclose
    fsm = 600 / max(W, H)
    sm = np.array(Image.fromarray((plate * 255).astype(np.uint8)).resize((round(W * fsm), round(H * fsm)))) > 100
    yy2, xx2 = np.mgrid[-24:25, -24:25]; disk = xx2 * xx2 + yy2 * yy2 <= 576
    sm = ndimage.binary_fill_holes(ndimage.binary_closing(np.pad(sm, 30), structure=disk))[30:-30, 30:-30]
    sm = ndimage.binary_erosion(sm, iterations=1)
    big = np.array(Image.fromarray((sm * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float)
    big = np.where(d2 < (1.25 if close_r > 6 else 1.1), big, 0)
    m = np.maximum(m, big)
    # outside the plate (not the cups): leftover studio white goes away
    rgb = np.array(im.convert("RGB")).astype(float)
    mx, mn = rgb.max(2), rgb.min(2)
    stray = (m < 128) & ~cups & (mn > 140) & ((mx - mn) / np.maximum(mx, 1) < .2)
    a = np.where(stray, 0, a)
    im.putalpha(Image.fromarray(np.maximum(a, m).astype(np.uint8)))
    return im

def fill_lower_rim(im):
    """Beef portion: the bright lower rim of the plate was lost between the rice and the thin dark
    outer rim line. In the lower half of the plate, every direction from the plate centre is made
    opaque out to the farthest kept pixel (= the rim line). The sauce cup on the left is left alone."""
    from scipy import ndimage
    a = np.array(im.getchannel("A")).astype(float)
    H, W = a.shape
    solid = a > 100
    lab, k = ndimage.label(solid)
    sizes = ndimage.sum(np.ones_like(a), lab, range(1, k + 1))
    plate = lab == 1 + int(np.argmax(sizes))
    ys, xs = np.nonzero(plate)
    cx, cy = xs.mean(), ys.mean()
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    ang = np.arctan2(yy - cy, xx - cx); r = np.hypot(xx - cx, yy - cy)
    nb = 720
    bins = ((ang + np.pi) / (2 * np.pi) * nb).astype(int).clip(0, nb - 1)
    far = np.zeros(nb); np.maximum.at(far, bins[plate], r[plate])
    far = ndimage.median_filter(far, size=9, mode="wrap")        # ignore single stray pixels
    lower = (ang > np.deg2rad(-10)) & (ang < np.deg2rad(115))   # bottom-right to bottom (not the sauce cup on the left)
    fill = lower & (r <= far[bins] - 1.5)
    edge = lower & (r > far[bins] - 1.5) & (r < far[bins])
    a = np.where(fill, 255, a)
    a = np.where(edge & (a < 128), 128, a)
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im

FIXED = {}
# beef portion: the white plate rim between the rice and the thin outer rim line was lost in the
# matting (up to ~65 px); a wider closing bridges it
CLOSE_R = {"beef-portion-1": 24}
# photos the photographer cropped on the left: fade that straight edge (fraction of the width)
SOFT_LEFT = {}
# masters already cleaned by hand (card and plate removed), no automatic side trimming
CLEAN = {"pulled-pork-brioche-2", "pork-brioche-2"}   # pork-brioche-2 = DSCF8690 side shot, card + plate faded by hand
for p in sorted(src.glob("*.png")):
    if only and p.stem not in only:
        continue
    im = Image.open(p).convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    im = im.crop(bb)
    im = largest_part(im)
    if "portion" in p.stem or "salad" in p.stem:
        im = fill_plate(im, CLOSE_R.get(p.stem, 6))
        if p.stem == "beef-portion-1":
            im = fill_lower_rim(im)
    if p.stem in SOFT_LEFT:
        a = np.array(im.getchannel("A")).astype(float)
        x = np.arange(a.shape[1]); g = np.clip(x / (a.shape[1] * SOFT_LEFT[p.stem]), 0, 1); g = g * g * (3 - 2 * g)
        im.putalpha(Image.fromarray((a * g[None, :]).astype(np.uint8)))
    if p.stem.endswith("-brioche-1"):
        im = trim_plate(im)
    elif p.stem.endswith("-brioche-2") and p.stem not in CLEAN:
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
