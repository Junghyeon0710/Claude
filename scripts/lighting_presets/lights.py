# -*- coding: utf-8 -*-
"""프리셋 공용 인공광 배치.

램프 메시 위치에 아래를 향한 SpotLight를 달고, 부두·야적장에는 작업등을 세운다.
전부 균일하면 지루하므로 밝기에 리듬을 주고 일부는 꺼 둔다.
이름은 모두 LP_ 접두어를 쓰고, 이미 있으면 만들지 않는다(멱등).
"""

SPOT_CLS = {"refPath": "/Script/Engine.SpotLight"}
SPOT_COMP = "/Script/Engine.SpotLightComponent"
POINT_CLS = {"refPath": "/Script/Engine.PointLight"}
POINT_COMP = "/Script/Engine.PointLightComponent"

# 램프 메시(CLH_LampIndustrial / CL_Lamp) 위치 — 도로·구역 가로등
LAMP_POSTS = [
    (-7000, 2380, 430), (-4400, 1830, 540), (-1800, 1870, 520),
    ( 600, 2050, 600), ( 5800, 2320, 540),
    (-2600,-1310, 480), ( 1600,-1500, 440),
    (-400, -4700, 440), (-1300,-4900, 430), ( 4400,  400, 460),
    # 도로 남쪽(연석 Y≈250) — 북쪽 램프만 있으면 도로 한쪽이 통째로 검게 뭉갠다.
    # 양쪽에 걸어야 빛 웅덩이가 소실점까지 이어진다.
    (-4600,  250, 500), (-1900,  250, 500), (  900,  250, 500), ( 3800,  250, 500),
]

# 부두를 따라 늘어선 작업등 — E 구도의 소실점을 따라 빛 웅덩이가 이어진다
PIER_LAMPS = [
    ( 2000,-5760, 780), (  800,-5760, 780), ( -400,-5760, 780),
    (-1600,-5760, 780), (-2800,-5760, 780), (-4000,-5760, 780),
    (-5200,-5760, 780),
    # 부두 서쪽 화물 구역 — 이게 없으면 E 구도의 왼쪽 절반이 통째로 검게 죽는다
    ( 1000,-6550, 720), (-1200,-6850, 720), (-3200,-6400, 720),
]

# 컨테이너 협로(Y=1100) 위 조명탑 — C 구도의 협로에 리듬을 준다
# 협로 중앙(Y=1100) 위. 옆으로 옮기면 컨테이너 위로 올라가 협로가 어두워지므로
# 위치는 통로에 두고 각도만 좌우로 기울여 양쪽 벽을 번갈아 비춘다.
YARD_LAMPS = [
    ( 4400, 1100, 980), ( 6400, 1100, 980), ( 8100, 1100, 980),
    ( 4400, -400, 980), ( 6400, 2700, 980), ( 2350, 1100, 980),
]
YARD_AIM = {0: (-62.0, 92.0), 1: (-62.0, -88.0), 2: (-80.0, 90.0),
            3: (-80.0, 0.0), 4: (-80.0, 0.0), 5: (-58.0, -85.0)}

# 크레인 작업등 — 시선이 머물 강한 하이라이트
CRANE_LAMPS = [
    ( 4400,-5450, 1750, -55,  150),   # 갠트리 크레인(동)
    (-5400,-5450, 1750, -55,   30),   # 갠트리 크레인(서)
    (-1850,-7000,  900, -35,   80),   # 소형 크레인
    ( -200,-7600,  900, -35, -100),
]


def _exists(u, name):
    r = u.scene("find_actors", name=name, tag="", collision_channels=[])
    return bool(r)


def _spawn_spot(u, name, loc, pitch=-88.0, yaw=0.0):
    return u.scene("add_to_scene_from_class", actor_type=SPOT_CLS, name=name,
                   xform={"location": {"x": loc[0], "y": loc[1], "z": loc[2]},
                          "rotation": {"pitch": pitch, "yaw": yaw, "roll": 0.0}})


def _comp(u, actor, ctype):
    c = u.actor("get_components", actor=actor, component_type={"refPath": ctype})
    return c[0] if c else None


def build(u, verbose=True):
    """LP_ 스팟라이트를 만들고 (이름 -> 컴포넌트 refPath) 맵을 돌려준다."""
    made = {}
    # 부두 조명은 바다 쪽(-Y)으로 기울여 수면에 빛이 길게 떨어지게 한다.
    groups = [("LP_Street", LAMP_POSTS, -88.0, None), ("LP_Pier", PIER_LAMPS, -76.0, -52.0),
              ("LP_Yard", YARD_LAMPS, -80.0, None)]
    for prefix, positions, pitch, fixed_yaw in groups:
        for i, p in enumerate(positions):
            name = "%s_%02d" % (prefix, i)
            yaw = fixed_yaw if fixed_yaw is not None else (i * 37) % 360
            if _exists(u, name):
                if fixed_yaw is not None:
                    f = u.scene("find_actors", name=name, tag="", collision_channels=[])
                    u.actor("set_actor_transform", actor=f[0], worldspace=True,
                            xform={"location": {"x": p[0], "y": p[1], "z": p[2]},
                                   "rotation": {"pitch": pitch, "yaw": yaw, "roll": 0.0}})
                continue
            _spawn_spot(u, name, p, pitch=pitch, yaw=yaw)
    for i, (x, y, z, pitch, yaw) in enumerate(CRANE_LAMPS):
        name = "LP_Crane_%02d" % i
        if not _exists(u, name):
            _spawn_spot(u, name, (x, y, z), pitch=pitch, yaw=yaw)

    for a in u.scene("find_actors", name="LP_", tag="", collision_channels=[]) or []:
        lab = u.actor("get_label", actor=a)
        c = _comp(u, a, SPOT_COMP)
        if c:
            made[lab] = c["refPath"]
    if verbose:
        print("spots:", len(made))
    return made


def rhythm(i, base):
    """균일하지 않게 — 4개마다 하나는 꺼지고, 나머지도 밝기를 갈라 놓는다."""
    if i % 7 == 3:
        return 0.0
    return base * (0.55, 1.0, 0.78, 1.25, 0.9, 1.4, 0.68)[i % 7]


def apply(u, spots, cfg):
    """cfg: {"street": {...}, "pier": {...}, "yard": {...}, "crane": {...}}"""
    n = 0
    for name in sorted(spots):
        kind = name.split("_")[1].lower()
        c = cfg.get(kind)
        if not c:
            continue
        i = int(name.split("_")[-1])
        vals = dict(c)
        vals["intensity"] = rhythm(i, c["intensity"]) if kind != "crane" else c["intensity"]
        u.set_props(spots[name], vals)
        n += 1
    return n


def apply_points(u, vals):
    """램프 메시에 이미 붙어 있는 PointLight 12개(빛무리 담당)."""
    n = 0
    for a in u.scene("find_actors", name="", tag="", collision_channels=[],
                     actor_type=POINT_CLS) or []:
        c = _comp(u, a, POINT_COMP)
        if not c:
            continue
        u.set_props(c, vals)
        n += 1
    return n
