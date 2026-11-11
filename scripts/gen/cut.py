import sys
from pathlib import Path
from PIL import Image, ImageOps
from rembg import remove, new_session
src=Path(sys.argv[1]); out=Path(sys.argv[2]); master=Path(sys.argv[3]); out.mkdir(parents=True,exist_ok=True); master.mkdir(parents=True,exist_ok=True)
M={"beef-brioche":["8656","8645"],"chicken-brioche":["8676","8669"],"turkey-brioche":["8705","8699"],"salmon-brioche":["8738","8735"],"pork-brioche":["8747","8743"],"veg-brioche":["8761","8759"],"cloud-caramel":["8625","8641"],"cloud-tiramisu":["8642","8643"],"cloud-pumpkin":["8708","8714"],
   "cloud-mango":["8723","8721"],"cloud-strawberry":["8726","8728"],"cloud-matcha":["8717"],"cloud-blueberry":["8720"],
   "dessert-hazelnut":["8619"],"dessert-oreo":["8620"],"dessert-caramel":["8621"],"dessert-berry":["8623"],"dessert-mango":["8624"],
   "caesar-salad":["8576"],"veg-salad":["8577"],"salmon-salad":["8586"],
   "beef-portion":["8770"],"salmon-portion":["8785"],"turkey-portion":["8792"],"chicken-portion":["8796"],"veg-portion":["8811"]}
only=sys.argv[4:] 
sess=new_session("isnet-general-use")
for name,files in M.items():
    if only and name not in only: continue
    for i,n in enumerate(files,1):
        im=ImageOps.exif_transpose(Image.open(src/f"DSCF{n}.JPG")).convert("RGB"); im.thumbnail((2200,2200),Image.LANCZOS)
        cut=remove(im,session=sess,post_process_mask=True)
        bb=cut.getchannel("A").point(lambda v:255 if v>24 else 0).getbbox(); cut=cut.crop(bb)
        S=1200; pad=0.06; f=min(S*(1-2*pad)/cut.width,S*(1-2*pad)/cut.height); cut=cut.resize((round(cut.width*f),round(cut.height*f)),Image.LANCZOS)
        can=Image.new("RGBA",(S,S),(0,0,0,0)); can.paste(cut,((S-cut.width)//2,(S-cut.height)//2),cut)
        can.save(master/f"{name}-{i}.png")
        for w in (500,900): can.resize((w,w),Image.LANCZOS).save(out/f"{name}-{i}-{w}.webp","WEBP",quality=82,method=6)
        print(name,i,n,flush=True)
