# -*- coding: utf-8 -*-
"""프리셋 레벨 하나를 처음부터 구성한다(라이트 + 창문 + 젖은 노면 + 라이팅 값)."""
import json
import sys
from ue_mcp import UE
import apply as ap
import presets, wet, windows
from cameras import LEVEL_OF

# 프리셋별 노면 젖음 / 창문 설정
WET = {
    "BlueHour":   ("BH", {"RoughnessMultiplier": 0.30, "Specular": 1.0, "MetallicMultiplier": 0.12,
                          "BaseColorTint": {"r": 0.62, "g": 0.66, "b": 0.74, "a": 1.0}}),
    "GoldenHour": ("GH", {"RoughnessMultiplier": 0.46, "Specular": 0.9, "MetallicMultiplier": 0.06,
                          "BaseColorTint": {"r": 0.80, "g": 0.78, "b": 0.76, "a": 1.0}}),
    "Night":      ("NT", {"RoughnessMultiplier": 0.22, "Specular": 1.0, "MetallicMultiplier": 0.16,
                          "BaseColorTint": {"r": 0.52, "g": 0.56, "b": 0.66, "a": 1.0}}),
}
WIN = {
    "BlueHour":   (32.0, {"r": 1.0, "g": 0.70, "b": 0.38, "a": 1.0}, 0.35, 7),
    "GoldenHour": (10.0, {"r": 1.0, "g": 0.78, "b": 0.48, "a": 1.0}, 0.18, 11),
    "Night":      (40.0, {"r": 1.0, "g": 0.68, "b": 0.34, "a": 1.0}, 0.38, 3),
}


def setup(u, name):
    ap.load(u, name)
    blds = json.load(open("building_bounds.json"))
    suffix, params = WET[name]
    mapping = wet.ensure(u, suffix, params)
    wet.apply_to_actors(u, mapping)
    emis, tint, ratio, seed = WIN[name]
    ref = windows.ensure_material(u, suffix, emis, tint)
    windows.build(u, blds, ref, ratio=ratio, seed=seed)
    ap.apply(u, getattr(presets, name.upper()))
    return u


if __name__ == "__main__":
    setup(UE(), sys.argv[1])
    print("setup done")
