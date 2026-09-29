#!/usr/bin/env python3
"""Generate web-ready images from the masters in assets-src/images/.

For every photo: WebP at several widths + one JPG fallback.
Also generates favicons, touch icons and the Open Graph share image.

Usage:  python3 scripts/optimize_images.py      (requires Pillow)
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets-src" / "images"
OUT = ROOT / "images"

PHOTO_WIDTHS = [600, 1000, 1600]
HERO_WIDTHS = [800, 1400, 2000]
FALLBACK_WIDTH = 1000
HERO_FALLBACK_WIDTH = 1600

# Masters that are not used on the site
SKIP = {"coffee", "dessert-can", "kiwi-icon", "logo"}


def resize(im, width):
    if im.width <= width:
        return im
    h = round(im.height * width / im.width)
    return im.resize((width, h), Image.LANCZOS)


def save_photo(im, name, widths, fallback):
    for w in widths:
        if w > im.width:
            continue
        resize(im, w).save(OUT / f"{name}-{w}.webp", "WEBP", quality=80, method=6)
    resize(im, fallback).save(OUT / f"{name}.jpg", "JPEG", quality=80, optimize=True, progressive=True)


def main():
    OUT.mkdir(exist_ok=True)
    for src in sorted(SRC.glob("*.jpg")):
        name = src.stem
        if name in SKIP:
            continue
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        if name == "hero":
            save_photo(im, name, HERO_WIDTHS, HERO_FALLBACK_WIDTH)
        else:
            save_photo(im, name, PHOTO_WIDTHS, FALLBACK_WIDTH)

    # Brand icon (round kiwi)
    icon = Image.open(SRC / "kiwi-icon.jpg").convert("RGB")
    side = min(icon.size)
    icon = ImageOps.fit(icon, (side, side), Image.LANCZOS)
    icon.resize((160, 160), Image.LANCZOS).save(OUT / "kiwi-icon.jpg", "JPEG", quality=85, optimize=True)
    icon.resize((32, 32), Image.LANCZOS).save(ROOT / "favicon-32.png", optimize=True)
    icon.resize((180, 180), Image.LANCZOS).save(ROOT / "apple-touch-icon.png", optimize=True)
    icon.resize((192, 192), Image.LANCZOS).save(OUT / "icon-192.png", optimize=True)
    icon.resize((512, 512), Image.LANCZOS).save(OUT / "icon-512.png", optimize=True)
    icon.resize((48, 48), Image.LANCZOS).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    # Full logo (used in structured data)
    logo = Image.open(SRC / "logo.png").convert("RGBA")
    resize(logo, 512).save(OUT / "logo.png", optimize=True)

    # Open Graph share image 1200x630
    hero = ImageOps.exif_transpose(Image.open(SRC / "hero.jpg")).convert("RGB")
    ImageOps.fit(hero, (1200, 630), Image.LANCZOS).save(
        OUT / "og-image.jpg", "JPEG", quality=82, optimize=True, progressive=True)


if __name__ == "__main__":
    main()
