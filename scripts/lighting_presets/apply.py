# -*- coding: utf-8 -*-
"""프리셋 하나를 레벨에 적용한다."""
import json
from ue_mcp import UE
from rig import Rig
import lights, hide_sprites
from cameras import LEVEL_OF


def load(u, preset):
    """프리셋 레벨로 전환한다.

    저장하지 않은 변경이 남아 있으면 load_level이 "has unsaved changes"로 거절하므로
    현재 레벨을 먼저 저장한다.
    """
    cur = u.scene("get_current_level")
    if cur == LEVEL_OF[preset]:
        return cur
    # 현재 레벨뿐 아니라 '로드할 대상'이 dirty해도 거절당한다(에러 문구가 가리키는 건 대상 쪽).
    for path in (cur, LEVEL_OF[preset]):
        if not path:
            continue
        try:
            if u.asset("is_dirty", asset_path=path):
                u.asset("save_assets", asset_paths=[path])
        except Exception as e:
            print("warn: could not save", path, str(e)[:120])
    print("loading", preset, "...")
    u.scene("load_level", level_path=LEVEL_OF[preset])
    return u.scene("get_current_level")


def apply(u, P, build_lights=True):
    r = Rig(u)
    r.set_actor_rot("dir", P["sun_rot"][0], P["sun_rot"][1])
    r.set_comp("dir", P["dir"])
    r.set_comp("sky", P["sky"])
    r.set_comp("fog", P["fog"])
    if P.get("atmo"):
        r.set_comp("atmo", P["atmo"])
    spots = lights.build(u, verbose=False) if build_lights else json.load(open("_spots.json"))
    json.dump(spots, open("_spots.json", "w"), indent=1)
    print("spots:", lights.apply(u, spots, P["spots"]),
          "points:", lights.apply_points(u, P["points"]))
    r.patch_ppv(P["ppv"])
    hide_sprites.run(u, verbose=False)
    return r


if __name__ == "__main__":
    import sys, presets
    u = UE()
    name = sys.argv[1]
    print(load(u, name))
    apply(u, getattr(presets, name.upper()))
    print("applied", name)
