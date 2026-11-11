import sys, numpy as np
from pathlib import Path
from PIL import Image, ImageOps
from rembg import remove, new_session
from scipy import ndimage
src=Path(sys.argv[1]); out=Path(sys.argv[2]); master=Path(sys.argv[3])
# 1 = sandwich in the branded box (primary), 2 = side view, cleaned to the biggest piece
M={"beef-brioche":["8647","8656"],"chicken-brioche":["8669","8676"],"turkey-brioche":["8699","8705"],
   "salmon-brioche":["8735","8738"],"pork-brioche":["8743","8747"],"veg-brioche":["8759","8761"]}
sess=new_session("isnet-general-use")
for name,files in M.items():
    for i,n in enumerate(files,1):
        im=ImageOps.exif_transpose(Image.open(src/f"DSCF{n}.JPG")).convert("RGB"); im.thumbnail((2200,2200),Image.LANCZOS)
        cut=remove(im,session=sess,post_process_mask=True)
        a=np.array(cut.getchannel("A"))
        lab,k=ndimage.label(a>40)
        if k>1:
            sizes=ndimage.sum(np.ones_like(a),lab,range(1,k+1)); keep=1+int(np.argmax(sizes))
            mask=ndimage.binary_dilation(lab==keep,iterations=3)
            a=np.where(mask,a,0).astype(np.uint8); cut.putalpha(Image.fromarray(a))
        bb=cut.getchannel("A").point(lambda v:255 if v>24 else 0).getbbox(); cut=cut.crop(bb)
        S=1200; pad=0.06; f=min(S*(1-2*pad)/cut.width,S*(1-2*pad)/cut.height); cut=cut.resize((round(cut.width*f),round(cut.height*f)),Image.LANCZOS)
        can=Image.new("RGBA",(S,S),(0,0,0,0)); can.paste(cut,((S-cut.width)//2,(S-cut.height)//2),cut)
        can.save(master/f"{name}-{i}.png")
        for w in (500,900): can.resize((w,w),Image.LANCZOS).save(out/f"{name}-{i}-{w}.webp","WEBP",quality=82,method=6)
        print(name,i,n,"parts",k,flush=True)
