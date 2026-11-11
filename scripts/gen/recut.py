import sys
from pathlib import Path
from PIL import Image, ImageOps
from rembg import remove, new_session
src, out, model = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
out.mkdir(parents=True, exist_ok=True)
sess = new_session(model)
for pair in sys.argv[4:]:
    name, n = pair.split("=")
    im = ImageOps.exif_transpose(Image.open(src / f"DSCF{n}.JPG")).convert("RGB"); im.thumbnail((2200, 2200), Image.LANCZOS)
    cut = remove(im, session=sess)
    bb = cut.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox(); cut = cut.crop(bb)
    cut.save(out / f"{name}.png"); print(name, n, cut.size, flush=True)
