# Beef brioche box shot: DSCF8645 (wider frame than 8647). The photo crops the plate at both sides,
# so the clipped edges are faded and the box is scaled to 1/3 of the canvas like the other five.
# usage: python beef_fix.py <workdir with beef8645_raw.png from cut2-style matting> <images/cut> <DSCF8645.JPG>
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
sp, cutdir = sys.argv[1], sys.argv[2]
c=Image.open(f"{sp}/beef8645_raw.png").convert("RGBA"); A=np.array(c); a=A[...,3].astype(float); H,W=a.shape
# close holes in the plate (reflections the matting removed): pad left/right so edge-touching holes are enclosed
m=a>128; pad=np.pad(m,((0,0),(1,1)),constant_values=True); filled=ndimage.binary_fill_holes(pad)[:,1:-1]
holes=filled&~m; holes[:1000]=False
a=np.where(holes,255,a)
# soft fade where the photographer's frame cut the plate
x=np.arange(W); ramp=W*.14; g=np.clip(np.minimum(x,W-1-x)/ramp,0,1); g=g*g*(3-2*g)
rows=np.arange(H)[:,None]>=930
a=np.where(rows,a*g[None,:],a)
from PIL import ImageOps
src=ImageOps.exif_transpose(Image.open(sys.argv[3])).convert("RGB"); src.thumbnail((2400,2400),Image.LANCZOS)
S0=np.array(src.crop((0,466,1600,2136)))
A[...,:3]=np.where(holes[...,None],S0,A[...,:3])
A[...,3]=a.astype(np.uint8); c=Image.fromarray(A)
# box 360..1160 = 800px -> make it 1/3 of the 1200 canvas like the other five
f=400/800; c=c.resize((round(W*f),round(H*f)),Image.LANCZOS)
S=1200; can=Image.new("RGBA",(S,S),(0,0,0,0)); bottom=int(S*0.81)
can.paste(c,((S-c.width)//2 - round((760-W/2)*f),bottom-c.height),c)
can.save(f"{sp}/beef-brioche-1.png")
for w in (500,900): can.resize((w,w),Image.LANCZOS).save(f"{sp}/beef-brioche-1-{w}.webp","WEBP",quality=82,method=6)
fs=[f"{sp}/beef-brioche-1-900.webp"]+[f"{cutdir}/{n}-brioche-1-900.webp" for n in ("chicken","pork","salmon","turkey","veg")]
sheet=Image.new('RGB',(6*300,330),(40,60,45)); d=ImageDraw.Draw(sheet)
for k,p in enumerate(fs):
    t=Image.open(p).convert("RGBA").resize((300,300),Image.LANCZOS); sheet.paste(t,(k*300,0),t); d.text((k*300+5,305),p.split('/')[-1],fill=(255,255,255))
sheet.save(f"{sp}/beefprev.png")
