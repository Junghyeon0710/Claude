import json
from ue_mcp import UE
u = UE()
print("level:", u.scene("get_current_level"))
KEYS = ["Warehouse_A","Warehouse_B","Warehouse_C","SmallFactory_A","SmallFactory_B",
        "HarborOffice","UtilityBuilding","MaintenanceBuilding"]
out = []
for a in u.scene("find_actors", name="", tag="", collision_channels=[]) or []:
    lab = u.actor("get_label", actor=a)
    if not any(k in lab for k in KEYS):
        continue
    b = u.actor("get_actor_bounds", actor=a)
    t = u.actor("get_actor_transform", actor=a)
    out.append({"label": lab, "bounds": b, "yaw": round(t["rotation"]["yaw"])})
json.dump(out, open("building_bounds.json","w"), indent=1)
for o in out:
    b = o["bounds"]
    mn, mx = b.get("min") or b.get("origin"), b.get("max")
    print(o["label"], o["yaw"], json.dumps(b))
