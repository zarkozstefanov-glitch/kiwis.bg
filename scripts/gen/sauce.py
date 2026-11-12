"""Recolour the dip in a portion cut-out so it matches the menu (the photo shoot used the same
orange sauce for several bowls). Keeps the light and shading of the original sauce.
usage: python sauce.py <in.png> <out.png> <colour: cheddar|white|herb|smoked> x0 x1 y0 y1   (box around the dip cup)"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

TARGET = {"cheddar": (247, 176, 32), "white": (246, 243, 234), "herb": (232, 236, 214), "smoked": (247, 201, 163)}   # smoked = the beef photo's original dip
src, dst, colour = sys.argv[1], sys.argv[2], sys.argv[3]
im = Image.open(src).convert("RGBA"); a = np.asarray(im).astype(float)
r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
h, w = al.shape
# the dip sits in the lower-left quarter: orange pixels there, largest blob
cand = (al > 200) & (r > 150) & (r - b > 45) & (r - g > 20)
x0, x1, y0, y1 = map(int, sys.argv[4:8])
keep = np.zeros_like(cand); keep[y0:y1, x0:x1] = True; cand &= keep
lab, n = ndimage.label(cand)
k = int(np.argmax(ndimage.sum(cand, lab, range(1, n + 1)))) + 1
blob = lab == k
blob = ndimage.binary_closing(blob, iterations=6)
blob = ndimage.binary_fill_holes(blob)
# only sauce-coloured pixels inside the blob (keeps the metal rim / reflections)
sauce = blob & (r - b > 25)
m = Image.fromarray((sauce * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
m = np.asarray(m).astype(float) / 255
L = 0.3 * r + 0.59 * g + 0.11 * b
s = L / np.median(L[sauce])
t = np.array(TARGET[colour], float)
new = np.clip(t[None, None, :] * s[..., None] ** (1.25 if colour in ("white", "herb") else 1.0), 0, 255)
out = a.copy()
out[..., :3] = a[..., :3] * (1 - m[..., None]) + new * m[..., None]
Image.fromarray(out.astype(np.uint8), "RGBA").save(dst)
ys, xs = np.nonzero(sauce); print(dst, "recoloured", int(sauce.sum()), "px, bbox", xs.min(), xs.max(), ys.min(), ys.max())
