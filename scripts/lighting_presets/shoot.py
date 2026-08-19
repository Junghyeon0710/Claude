# -*- coding: utf-8 -*-
"""고정 카메라 3곳(+옵션 보조)을 찍고 몽타주를 만든다."""
import sys
from ue_mcp import UE
from cameras import CAMERAS, EXTRA  # noqa: F401
import grid_util

def shoot(u, tag, cams=None, out=None, cols=3, w=620):
    cams = cams or CAMERAS
    paths, labels = [], []
    for name, loc, rot in cams:
        p = u.capture("shots/%s_%s.png" % (tag, name), loc, rot)
        paths.append(p); labels.append(name)
    if out is None:
        out = "shots/%s_grid.jpg" % tag
    grid_util.montage(paths, out, cols=cols, w=w, labels=labels)
    return out, paths

if __name__ == "__main__":
    u = UE()
    tag = sys.argv[1]
    cams = CAMERAS + EXTRA if "--extra" in sys.argv else CAMERAS
    out, _ = shoot(u, tag, cams)
    print(out)
