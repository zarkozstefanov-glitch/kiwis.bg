import sys, numpy as np
from PIL import Image, ImageFilter
A, B, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
for n in sys.argv[4:]:
    O = Image.open(f"{A}/{n}.jpg").convert("RGB"); E = Image.open(f"{B}/{n}.jpg").convert("RGB")
    Os = O.resize(E.size, Image.LANCZOS)
    r = 6
    bo = np.asarray(Os.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) + 4
    be = np.asarray(E.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) + 4
    R = np.clip(be / bo, 0.4, 3.0)
    Rimg = [Image.fromarray(R[..., c]).resize(O.size, Image.BICUBIC) for c in range(3)]
    Rf = np.stack([np.asarray(x) for x in Rimg], -1)
    out = np.clip(np.asarray(O, dtype=np.float32) * Rf, 0, 255).astype(np.uint8)
    Image.fromarray(out).save(f"{OUT}/{n}.jpg", quality=92); print(n, O.size)
