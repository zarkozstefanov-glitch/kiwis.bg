"""Plated dishes: BiRefNet keeps food edges clean but drops the metal plate, isnet keeps the plate
but bites holes into the food. The union of both masks gives the whole plate with clean food.
usage: python recut_union.py <photos dir> <assets-src/cutouts> name=DSCFnumber ..."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
from rembg import remove, new_session
from scipy import ndimage

src, out = Path(sys.argv[1]), Path(sys.argv[2])
s1, s2 = new_session("birefnet-general"), new_session("isnet-general-use")
for pair in sys.argv[3:]:
    name, n = pair.split("=")
    im = ImageOps.exif_transpose(Image.open(src / f"DSCF{n}.JPG")).convert("RGB"); im.thumbnail((2200, 2200), Image.LANCZOS)
    a1 = np.array(remove(im, session=s1, only_mask=True)).astype(float)
    a2 = np.array(remove(im, session=s2, only_mask=True, post_process_mask=True)).astype(float)
    a = np.maximum(a1, a2)
    a = np.where(ndimage.binary_fill_holes(a > 128), np.maximum(a, 255), a)   # no holes inside the plate
    rgba = im.convert("RGBA"); rgba.putalpha(Image.fromarray(a.astype(np.uint8)))
    rgba = rgba.crop(rgba.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox())
    rgba.save(out / f"{name}.png"); print(name, rgba.size, flush=True)
