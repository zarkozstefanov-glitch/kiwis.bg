"""Small touch-up of the live pork brioche photos (images/cut, 900 px), nothing else:
 - side shot (-2): remove the white paper card and the plate edge right of the sandwich
   (only low-saturation / bluish pixels in the right-hand band — the bun and the meat stay)
 - box shot (-1): remove the piece of plate sticking out to the right under the box
Writes the -900 and -500 files back. usage: python fix_pork.py images/cut"""
import sys
import numpy as np
from PIL import Image

cut = sys.argv[1]


def save(im, name):
    im.save(f"{cut}/{name}-900.webp", "WEBP", quality=84, method=6)
    im.resize((500, 500), Image.LANCZOS).save(f"{cut}/{name}-500.webp", "WEBP", quality=84, method=6)


# side shot
im = Image.open(f"{cut}/pork-brioche-2-900.webp").convert("RGBA")
A = np.array(im).astype(float); H, W = A.shape[:2]
rgb, a = A[..., :3], A[..., 3]
mx, mn = rgb.max(2), rgb.min(2)
sat = (mx - mn) / np.maximum(mx, 1)
bluish = rgb[..., 2] >= np.maximum(rgb[..., 0], rgb[..., 1]) - 6
x = np.arange(W)[None, :].repeat(H, 0)
band = x > W * .80
kill = band & ((sat < .22) | bluish)
a = np.where(kill, 0, a)
a = a * np.clip((W * .985 - x) / (W * .04), 0, 1)          # soft right edge
A[..., 3] = a
save(Image.fromarray(A.astype(np.uint8)), "pork-brioche-2")

# box shot
im = Image.open(f"{cut}/pork-brioche-1-900.webp").convert("RGBA")
A = np.array(im).astype(float); H, W = A.shape[:2]
y = np.arange(H)[:, None].repeat(W, 1); x = np.arange(W)[None, :].repeat(H, 0)
plate = y > H * .80
g = np.clip((W * .74 - x) / (W * .06), 0, 1); g = g * g * (3 - 2 * g)
A[..., 3] = np.where(plate, A[..., 3] * g, A[..., 3])
save(Image.fromarray(A.astype(np.uint8)), "pork-brioche-1")
print("pork ok")
