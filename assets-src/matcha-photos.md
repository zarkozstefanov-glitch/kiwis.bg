# Matcha product photos — 17 November 2026

Background extraction used the built-in imagegen tool, with genuine alpha transparency.

| Owner's source in `../../Images/Google Images/` | Transparent master in `cutouts/` | Website files in `../images/cut/` |
| --- | --- | --- |
| SCAN-1.JPG | cloud-matcha-1.png | cloud-matcha-1-{500,900}.webp |
| SCAN-2.JPG | cloud-matcha-2.png | cloud-matcha-2-{500,900}.webp |
| SCAN-5.JPG | cloud-blueberry-1.png | cloud-blueberry-1-{500,900}.webp |
| SCAN-6.JPG | cloud-blueberry-2.png | cloud-blueberry-2-{500,900}.webp |

The front views are the default photos; the overhead views use the existing photo-switch button. `scripts/gen/normalize.py` applies the same framing and baseline as the other products. AVIF variants are regenerated from the updated WebP files so Apache cannot serve an older image.

## Final prompt

One imagegen edit call per source file, with that original as the only reference and `transparent_background: true`. Replace `{file}` with the corresponding source filename:

> Use case: background-extraction. Edit target: the single product cup in the attached photograph {file}. Remove only the studio background, floor, and cast shadow. Output a clean photorealistic transparent PNG cutout of this exact cup, fully visible, centered with modest transparent padding. Preserve the exact camera angle, cup proportions, transparent plastic rim, foam, toppings, drink layers and colors, and kiwi bird logo exactly as photographed. Keep every part of the cup and topping intact, especially the white foam and clear rim. Do not redesign, retouch the drink, add objects, invent text, or change the logo. Genuine alpha transparency outside the cup, no white matte and no cast shadow.
