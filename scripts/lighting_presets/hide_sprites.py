# -*- coding: utf-8 -*-
"""에디터 전용 스프라이트(빌보드/화살표)를 숨긴다.

CaptureViewport는 PIE 없이 에디터 뷰포트를 렌더하므로 라이트 아이콘이 그대로
찍힌다. bShowUI 플래그로는 사라지지 않아 컴포넌트 가시성을 직접 끈다.
"""
CLASSES = [
    "/Script/Engine.Light", "/Script/Engine.SkyLight",
    "/Script/Engine.ExponentialHeightFog", "/Script/Engine.SkyAtmosphere",
    "/Script/Engine.VolumetricCloud", "/Script/Engine.PostProcessVolume",
    "/Script/Engine.PlayerStart", "/Script/Engine.Note",
]
SPRITE_COMPS = ["/Script/Engine.BillboardComponent", "/Script/Engine.ArrowComponent"]


def run(u, verbose=True):
    n = 0
    seen = set()
    for cls in CLASSES:
        for a in u.scene("find_actors", name="", tag="", collision_channels=[],
                         actor_type={"refPath": cls}) or []:
            if a["refPath"] in seen:
                continue
            seen.add(a["refPath"])
            for ct in SPRITE_COMPS:
                for c in u.actor("get_components", actor=a,
                                 component_type={"refPath": ct}) or []:
                    try:
                        u.set_props(c, {"bVisible": False, "bHiddenInGame": True})
                        n += 1
                    except Exception:
                        pass
    if verbose:
        print("sprites hidden:", n, "on", len(seen), "actors")
    return n


if __name__ == "__main__":
    from ue_mcp import UE
    run(UE())
