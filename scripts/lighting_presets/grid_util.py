import sys, os
from PIL import Image, ImageDraw
def montage(paths, out, cols=3, w=640, labels=None):
    ims = [Image.open(p).convert("RGB") for p in paths]
    h = int(ims[0].height * w / ims[0].width)
    rows = (len(ims)+cols-1)//cols
    canvas = Image.new("RGB", (cols*w, rows*(h+18)), (20,20,20))
    d = ImageDraw.Draw(canvas)
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        canvas.paste(im.resize((w,h), Image.LANCZOS), (c*w, r*(h+18)+18))
        d.text((c*w+6, r*(h+18)+4), (labels[i] if labels else os.path.basename(paths[i])), fill=(255,255,0))
    canvas.save(out)
    return canvas.size
if __name__ == "__main__":
    print(montage(sys.argv[2:], sys.argv[1]))
