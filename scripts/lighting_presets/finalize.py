# -*- coding: utf-8 -*-
"""세 프리셋에 최종 조명 구성을 일괄 반영하고 대표 구도를 다시 찍는다."""
import sys
from ue_mcp import UE
from cameras import LEVEL_OF, PRESETS
import apply as ap, presets, shoot, gameview

TAG = {"BlueHour": "bh", "GoldenHour": "gh", "Night": "nt"}

def run(u, names):
    for name in names:
        ap.load(u, name)
        ap.apply(u, getattr(presets, name.upper()))
        u.asset("save_assets", asset_paths=[LEVEL_OF[name]])
        if "--gv" in sys.argv:
            gameview.toggle(u)
        out, _ = shoot.shoot(u, "final_" + TAG[name])
        print(name, "->", out)

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    run(UE(), args or PRESETS)
