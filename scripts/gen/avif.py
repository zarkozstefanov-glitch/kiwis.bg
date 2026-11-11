"""Makes an .avif next to every .webp / .jpg in images/ (same pixels, much smaller file).
Apache serves the .avif automatically to browsers that accept it (see .htaccess), so the HTML
does not change. Only (re)encodes when the source is newer than its .avif.
usage (venv with Pillow): python avif.py images"""
import sys
from pathlib import Path
from PIL import Image

root = Path(sys.argv[1])
done = saved = 0
for src in sorted(list(root.rglob("*.webp")) + list(root.rglob("*.jpg"))):
    out = src.with_suffix(src.suffix + ".avif")          # hero-800.webp -> hero-800.webp.avif
    if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
        continue
    im = Image.open(src)
    im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
    im.save(out, "AVIF", quality=58, speed=4)
    if out.stat().st_size >= src.stat().st_size:          # no gain: don't serve it
        out.unlink(); continue
    done += 1; saved += src.stat().st_size - out.stat().st_size
print(f"avif: {done} files, {saved / 1e6:.1f} MB smaller")
