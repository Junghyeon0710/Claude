# -*- coding: utf-8 -*-
"""파라미터 조합을 순서대로 적용하며 한 구도를 찍어 비교 시트를 만든다."""
from ue_mcp import UE
from rig import Rig
import grid_util

def sweep(u, r, tag, variants, cam, w=640, cols=2):
    """variants: [(label, {"dir":{...},"sky":{...},"fog":{...},"ppv":{...}}), ...]"""
    paths, labels = [], []
    for label, ch in variants:
        for key in ("dir", "sky", "fog", "atmo"):
            if ch.get(key):
                r.set_comp(key, ch[key])
        if ch.get("rot"):
            r.set_actor_rot("dir", *ch["rot"])
        if ch.get("ppv"):
            r.patch_ppv(ch["ppv"])
        if ch.get("hook"):
            ch["hook"](u, r)
        name, loc, rot = cam
        p = u.capture("shots/%s_%s.png" % (tag, label), loc, rot)
        paths.append(p); labels.append(label)
        print("  ", label)
    out = "shots/%s_sheet.jpg" % tag
    grid_util.montage(paths, out, cols=cols, w=w, labels=labels)
    return out
