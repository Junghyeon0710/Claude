# -*- coding: utf-8 -*-
"""젖은 노면.

노면 MI를 직접 고치면 주간 원본 레벨까지 젖어버리므로, 프리셋마다
'원본 MI를 부모로 삼는' 사본을 따로 만들고 지면 액터에만 오버라이드한다.
레벨 사본은 서로 독립이라 오버라이드도 프리셋별로 남는다.
"""
import json

MI_DIR = "/Game/IndustrialHarbor_Claude/MaterialInstances"
WET_DIR = "/Game/IndustrialHarbor_Claude/MaterialInstances/Wet"

# 젖게 만들 원본 노면 머티리얼
SOURCES = [
    "MI_CL_Asphalt_Worn", "MI_CL_Asphalt_Cracked", "MI_CL_Asphalt_Road",
    "MI_CL_Concrete_FloorWorn", "MI_CL_Concrete_FloorPaint",
    "MI_CL_Concrete_Aged", "MI_CL_Wood_Worn",
]
# 노면 오버라이드를 적용할 액터 이름 조각
ACTOR_KEYS = ["Ground_", "Road_20m", "Pier_Deck", "Curb_", "SeaWall"]


def wet_path(suffix, src):
    return "%s/%s_%s" % (WET_DIR, src.replace("MI_CL_", "MIW%s_" % suffix), suffix)


def ensure(u, suffix, params, verbose=True):
    """젖은 MI 세트를 만들고 파라미터를 적용한다. (원본이름 -> 사본경로) 맵 반환."""
    mapping = {}
    for src in SOURCES:
        dst = wet_path(suffix, src)
        if not u.asset("exists", path=dst):
            u.mi("create", folder_path=WET_DIR, asset_name=dst.rsplit("/", 1)[1],
                 parent={"refPath": "%s/%s.%s" % (MI_DIR, src, src)})
        ref = {"refPath": dst + "." + dst.rsplit("/", 1)[1]}
        for k, v in params.items():
            if isinstance(v, dict):
                u.mi("set_vector_parameter", instance=ref, name=k, value=v)
            else:
                u.mi("set_scalar_parameter", instance=ref, name=k, value=float(v))
        mapping["%s/%s.%s" % (MI_DIR, src, src)] = ref["refPath"]
        u.asset("save_assets", asset_paths=[dst])
    if verbose:
        print("wet MIs:", len(mapping))
    return mapping


SCRIPT = r'''
import json
MAP = %s
KEYS = %s

def call(tool, payload):
    return execute_tool(tool, json.dumps(payload))["returnValue"]

def run():
    acts = call("editor_toolset.toolsets.scene.SceneTools.find_actors",
                {"name": "", "tag": "", "collision_channels": []})
    touched = 0
    for a in acts:
        lab = call("editor_toolset.toolsets.actor.ActorTools.get_label", {"actor": a})
        if not any(k in lab for k in KEYS):
            continue
        comps = call("editor_toolset.toolsets.actor.ActorTools.get_components",
                     {"actor": a, "component_type": {"refPath": "/Script/Engine.StaticMeshComponent"}})
        if not comps:
            continue
        c = comps[0]
        p = json.loads(call("editor_toolset.toolsets.object.ObjectTools.get_properties",
                            {"instance": c, "properties": ["staticMesh"]}))
        mesh = p["staticMesh"]
        if not mesh or mesh == "None":
            continue
        slots = call("editor_toolset.toolsets.static_mesh.StaticMeshTools.get_material_slots",
                     {"mesh": mesh})
        mats = []
        hit = False
        for s in slots:
            m = call("editor_toolset.toolsets.static_mesh.StaticMeshTools.get_material",
                     {"mesh": mesh, "slot_name": s})
            path = m["refPath"] if m else ""
            if path in MAP:
                mats.append({"refPath": MAP[path]})
                hit = True
            else:
                mats.append({"refPath": path} if path else None)
        if not hit:
            continue
        execute_tool("editor_toolset.toolsets.object.ObjectTools.set_properties",
                     json.dumps({"instance": c, "values": json.dumps({"overrideMaterials": mats})}))
        touched += 1
    return {"touched": touched}
'''


def apply_to_actors(u, mapping, verbose=True):
    code = SCRIPT % (json.dumps(mapping), json.dumps(ACTOR_KEYS))
    r = u.script(code, timeout=2400)
    if verbose:
        print("ground actors overridden:", r)
    return r
