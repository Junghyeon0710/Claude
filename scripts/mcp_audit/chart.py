# -*- coding: utf-8 -*-
"""툴셋별 통과/실패를 가로 막대로 그린다."""
import json, io, os, collections, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r"D:\Unreal Projects\Claude\docs\images\mcp_01_testmatrix.jpg"

def font(sz, bold=False):
    for p in (r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
              r"C:\Windows\Fonts\malgun.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

raw = os.path.join(HERE, "results_mcp.json")
agg = collections.defaultdict(lambda: [0, 0])
if os.path.exists(raw):
    res = json.load(io.open(raw, encoding="utf-8"))
    for t in res.get("tests", []):
        parts = t.get("name", "").split(".")
        if len(parts) > 2 and parts[1] == "Toolsets":
            g = parts[2]
        elif len(parts) > 1 and parts[0] == "AI":
            g = parts[1]
        else:
            g = ".".join(parts[:2])
        ok = str(t.get("state", "")).lower() in ("success", "passed")
        agg[g][0 if ok else 1] += 1
else:
    # run_tests.py 원본 결과가 없으면 커밋된 요약으로 그린다
    s2 = json.load(io.open(os.path.join(HERE, "summary_toolsets.json"), encoding="utf-8"))
    for g, v in s2["groups"].items():
        agg[g] = [v["pass"], v["fail"]]

rows = sorted(agg.items(), key=lambda kv: -(kv[1][0] + kv[1][1]))
W, RH, PAD, LBL = 1180, 34, 26, 300
H = PAD * 2 + 78 + RH * len(rows)
BG, FG, DIM = (17, 18, 21), (232, 230, 226), (120, 122, 130)
PASS, FAIL = (74, 158, 116), (198, 78, 72)
im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)
f, fb, fs = font(15), font(19, True), font(13)

d.text((PAD, PAD - 4), "MCP 툴셋 자동화 테스트 — 2,494건", fill=FG, font=fb)
tp = sum(v[0] for v in agg.values()); tf = sum(v[1] for v in agg.values())
d.text((PAD, PAD + 26), f"통과 {tp}   실패 {tf}   ({tp*100.0/(tp+tf):.1f}%)", fill=DIM, font=fs)

barx = PAD + LBL
barw = W - barx - PAD - 96
mx = max(v[0] + v[1] for v in agg.values())
y = PAD + 70
for name, (p, fl) in rows:
    d.text((PAD, y + 8), name[:34], fill=FG if fl else DIM, font=f)
    tot = p + fl
    wpx = max(2, int(barw * tot / mx))
    pw = int(wpx * p / tot) if tot else 0
    d.rectangle([barx, y + 7, barx + pw, y + 23], fill=PASS)
    if fl:
        d.rectangle([barx + pw, y + 7, barx + wpx, y + 23], fill=FAIL)
    txt = f"{p}" + (f" / {fl} 실패" if fl else "")
    d.text((barx + wpx + 10, y + 8), txt, fill=FAIL if fl else DIM, font=fs)
    y += RH
im.save(OUT, quality=94)
print(OUT, im.size)
