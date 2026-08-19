# -*- coding: utf-8 -*-
"""창문 조명.

건물 메시에 창문이 거의 없어(레벨 전체에 1개) 벽면에 CL_Window_Industrial을
직접 배치하고 발광 유리를 입힌다. 전부 켜면 가짜처럼 보이므로 후보 중
35%만 실제로 세운다.

건물마다 yaw가 제각각인데 get_actor_bounds는 축정렬(AABB)이라 회전한 건물은
실제보다 부풀어 나온다. 그래서 종류별 half-size는 yaw가 0에 가까운 인스턴스에서
구하고, 벽면 위치는 AABB 중심 + yaw 회전으로 계산한다.
"""
import json
import math
import random

WINDOW_MESH = "/Game/IndustrialHarbor_Claude/Modular/CL_Window_Industrial"
GLASS_SRC = "/Game/IndustrialHarbor_Claude/MaterialInstances/MI_CL_Glass.MI_CL_Glass"
FRAME = "/Game/IndustrialHarbor_Claude/MaterialInstances/MI_CL_Metal_Rust03.MI_CL_Metal_Rust03"
WIN_DIR = "/Game/IndustrialHarbor_Claude/MaterialInstances/Wet"

WIN_HALF_W = 97.5      # 창문 메시 가로 반폭
ROWS = (330.0, 720.0)  # 창문 높이 두 줄
STEP = 520.0           # 가로 간격


def kind_of(label):
    k = label.replace("CLH_", "")
    return k.rsplit("_", 1)[0] if k.rsplit("_", 1)[-1].isdigit() else k


def local_sizes(buildings):
    """종류별 half-size를 yaw가 0/180에 가장 가까운 인스턴스에서 뽑는다."""
    best = {}
    for b in buildings:
        k = kind_of(b["label"])
        yaw = b["yaw"] % 180
        err = min(yaw, 180 - yaw)
        if k not in best or err < best[k][0]:
            mn, mx = b["bounds"]["min"], b["bounds"]["max"]
            best[k] = (err, ((mx["x"] - mn["x"]) / 2.0,
                             (mx["y"] - mn["y"]) / 2.0,
                             mx["z"] - mn["z"]))
    # yaw 90/270 인스턴스에서 뽑혔다면 X/Y가 뒤집혀 있다
    return {k: v[1] for k, v in best.items()}


def candidates(buildings, sizes):
    """(위치, yaw) 후보 목록. 벽면을 따라 두 줄로 늘어놓는다."""
    out = []
    for b in buildings:
        k = kind_of(b["label"])
        hx, hy, h = sizes[k]
        yaw = b["yaw"]
        # 90도 계열로 놓인 인스턴스는 표준 half-size의 X/Y를 맞바꾼다
        if abs(((yaw % 180) - 90)) < 45:
            hx, hy = hy, hx
        mn, mx = b["bounds"]["min"], b["bounds"]["max"]
        cx, cy = (mn["x"] + mx["x"]) / 2.0, (mn["y"] + mx["y"]) / 2.0
        rad = math.radians(yaw)
        cs, sn = math.cos(rad), math.sin(rad)
        rows = [z for z in ROWS if z < h - 120]
        for side in (-1, 1):                     # 남/북 벽
            n = max(1, int((hx - 260) * 2 // STEP))
            for i in range(n):
                u = -((n - 1) * STEP) / 2.0 + i * STEP
                v = side * (hy + 10.0)
                for z in rows:
                    wx = cx + u * cs - v * sn
                    wy = cy + u * sn + v * cs
                    out.append((b["label"], (wx, wy, z), yaw))
        for side in (-1, 1):                     # 동/서 벽
            n = max(1, int((hy - 260) * 2 // STEP))
            for i in range(n):
                v = -((n - 1) * STEP) / 2.0 + i * STEP
                u = side * (hx + 10.0)
                for z in rows:
                    wx = cx + u * cs - v * sn
                    wy = cy + u * sn + v * cs
                    out.append((b["label"], (wx, wy, z), yaw + 90.0))
    return out


def ensure_material(u, suffix, emissive, tint):
    name = "MI_Win_%s" % suffix
    path = "%s/%s" % (WIN_DIR, name)
    if not u.asset("exists", path=path):
        u.mi("create", folder_path=WIN_DIR, asset_name=name, parent={"refPath": GLASS_SRC})
    ref = path + "." + name
    u.mi("set_scalar_parameter", instance={"refPath": ref}, name="EmissiveAmount", value=float(emissive))
    u.mi("set_vector_parameter", instance={"refPath": ref}, name="BaseColorTint", value=tint)
    u.mi("set_scalar_parameter", instance={"refPath": ref}, name="RoughnessMultiplier", value=0.35)
    u.asset("save_assets", asset_paths=[path])
    return ref


SCRIPT = r'''
import json
ROWS = %s
GLASS = %s
FRAME = %s
MESH = %s

def call(tool, payload):
    return execute_tool(tool, json.dumps(payload))["returnValue"]

def run():
    made = 0
    for name, x, y, z, yaw in ROWS:
        a = call("editor_toolset.toolsets.scene.SceneTools.add_to_scene_from_asset",
                 {"asset_path": MESH, "name": name,
                  "xform": {"location": {"x": x, "y": y, "z": z},
                            "rotation": {"pitch": 0.0, "yaw": yaw, "roll": 0.0}}})
        if not a:
            continue
        comps = call("editor_toolset.toolsets.actor.ActorTools.get_components",
                     {"actor": a, "component_type": {"refPath": "/Script/Engine.StaticMeshComponent"}})
        if comps:
            execute_tool("editor_toolset.toolsets.object.ObjectTools.set_properties",
                         json.dumps({"instance": comps[0], "values": json.dumps(
                             {"overrideMaterials": [{"refPath": GLASS}, {"refPath": FRAME}]})}))
        made += 1
    return {"made": made}
'''


def build(u, buildings, glass_ref, ratio=0.35, seed=7, verbose=True):
    if u.scene("find_actors", name="LPWin_", tag="", collision_channels=[]):
        if verbose:
            print("windows already placed, skip")
        return 0
    sizes = local_sizes(buildings)
    cands = candidates(buildings, sizes)
    rnd = random.Random(seed)
    picked = [c for c in cands if rnd.random() < ratio]
    rows = [["LPWin_%04d" % i, round(p[0], 1), round(p[1], 1), round(p[2], 1), round(yaw, 1)]
            for i, (lab, p, yaw) in enumerate(picked)]
    code = SCRIPT % (json.dumps(rows), json.dumps(glass_ref), json.dumps(FRAME), json.dumps(WINDOW_MESH))
    r = u.script(code, timeout=2400)
    if verbose:
        print("window candidates:", len(cands), "-> placed:", r)
    return r
