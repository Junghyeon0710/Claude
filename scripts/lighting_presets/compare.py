# -*- coding: utf-8 -*-
"""구역마다 세 시간대를 가로로 이어 붙인 비교 이미지를 만든다."""
import os
from PIL import Image, ImageDraw, ImageFont

SHOTS = "shots"
OUT = "../../docs/images"
ORDER = [("bh", "BLUE HOUR"), ("gh", "GOLDEN HOUR"), ("nt", "NIGHT")]
ZONES = [("B_warehouse", "04_cmp_warehouse"), ("C_yard", "05_cmp_yard"), ("E_pier", "06_cmp_pier")]
BAR = 34


def font(size):
    for p in (r"C:\Windows\Fonts\malgun.ttf", r"C:\Windows\Fonts\arial.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def strip(zone, out_path, width=900):
    ims = [Image.open("%s/final_%s_%s.png" % (SHOTS, tag, zone)).convert("RGB") for tag, _ in ORDER]
    h = int(ims[0].height * width / ims[0].width)
    canvas = Image.new("RGB", (width * len(ims), h + BAR), (14, 14, 16))
    d = ImageDraw.Draw(canvas)
    f = font(19)
    for i, (im, (_, label)) in enumerate(zip(ims, ORDER)):
        canvas.paste(im.resize((width, h), Image.LANCZOS), (i * width, BAR))
        d.text((i * width + 14, 8), label, fill=(235, 232, 226), font=f)
        if i:
            d.line([(i * width, 0), (i * width, h + BAR)], fill=(40, 40, 44), width=2)
    canvas.save(out_path, quality=92)
    return canvas.size


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for zone, stem in ZONES:
        p = "%s/lighting_%s.jpg" % (OUT, stem)
        print(p, strip(zone, p))
    # 섹션 대표컷 + 프리셋 단독컷
    from PIL import Image
    for src, dst in [("final_gh_B_warehouse", "01_hero"),
                     ("final_bh_C_yard", "02_bluehour"),
                     ("final_nt_B_warehouse", "03_night")]:
        Image.open("%s/%s.png" % (SHOTS, src)).convert("RGB").save(
            "%s/lighting_%s.jpg" % (OUT, dst), quality=93)
        print("%s/lighting_%s.jpg" % (OUT, dst))
