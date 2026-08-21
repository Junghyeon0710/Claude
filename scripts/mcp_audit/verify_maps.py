# -*- coding: utf-8 -*-
"""에디터 재기동 후 (1) Project.Maps.PIE 재검증 (2) 프로젝트 맵 전수 PIE 순회."""
import json, sys, time, io, os, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "lighting_presets"))
HERE = os.path.dirname(os.path.abspath(__file__))
AT = "AutomationTestToolset.AutomationTestToolset"
EA = "EditorToolset.EditorAppToolset"
MAPS = [
 "/Game/IndustrialHarbor_Claude/Level/L_IndustrialHarbor_Claude",
 "/Game/IndustrialHarbor_Claude/Level/L_IndustrialHarbor_BlueHour",
 "/Game/IndustrialHarbor_Claude/Level/L_IndustrialHarbor_GoldenHour",
 "/Game/IndustrialHarbor_Claude/Level/L_IndustrialHarbor_Night",
 "/Game/PCG_Test/L_PCG_Forest",
 "/Game/VFX_Test/L_VFX_Showcase",
 "/Game/KoreanOldTown/Level/KotreanOldTown",
]

u = None
t0 = time.time()
while time.time() - t0 < 1500:
    try:
        from ue_mcp import UE
        u = UE(); break
    except Exception:
        time.sleep(15)
if u is None:
    print("MCP never came up"); raise SystemExit(1)
print(f"[{int(time.time()-t0)}s] connected", flush=True)

# ---- (1) Project.Maps.PIE 재검증
u.call(AT, "DiscoverTests", {}, timeout=300)
try:
    u.call(AT, "RunTestsByFilter", {"filterExpression": "Project.Maps.PIE"}, timeout=90)
except Exception:
    pass
t1 = time.time()
while time.time() - t1 < 900:
    st = u.call(AT, "GetTestStatus", {}, timeout=120)
    st = json.loads(st) if isinstance(st, str) else st
    if str(st.get("state", "")).lower() in ("ready", "idle", "complete") and time.time() - t1 > 60:
        break
    time.sleep(15)
res = u.call(AT, "GetTestResults", {}, timeout=600)
res = json.loads(res) if isinstance(res, str) else res
for t in res.get("tests", []):
    print(f"[Maps.PIE] {t.get('state')} ({t.get('duration',0):.1f}s)", flush=True)
    for e in (t.get("errors") or [])[:3]:
        m = e.get("message") if isinstance(e, dict) else str(e)
        print("    ERR", str(m)[:180].replace("\n", " "), flush=True)
io.open(os.path.join(HERE, "results_maps2.json"), "w", encoding="utf-8").write(
    json.dumps(res, indent=1, ensure_ascii=False))

# ---- (2) 맵 전수 PIE 순회
print("\n=== 맵 전수 PIE ===", flush=True)
rows = []
for m in MAPS:
    r = {"map": m.rsplit("/", 1)[-1]}
    t2 = time.time()
    try:
        if not u.asset("exists", path=m):
            r["result"] = "MISSING"; rows.append(r); print(f"  {r['map']:32s} MISSING", flush=True); continue
        cur = u.scene("get_current_level")
        for p in (cur, m):
            try:
                if p and u.asset("is_dirty", asset_path=p):
                    u.asset("save_assets", asset_paths=[p])
            except Exception:
                pass
        u.scene("load_level", level_path=m, timeout=1800) if False else u.call(
            "editor_toolset.toolsets.scene.SceneTools", "load_level", {"level_path": m}, timeout=1800)
        r["load_s"] = round(time.time() - t2, 1)
        u.call(EA, "StartPIE", {"options": {}}, timeout=900)
        time.sleep(6)
        running = u.call(EA, "IsPIERunning", {}, timeout=120)
        r["pie"] = bool(running)
        u.call(EA, "StopPIE", {}, timeout=300)
        r["result"] = "OK" if running else "PIE_NOT_RUNNING"
    except Exception as e:
        r["result"] = "ERR"
        r["msg"] = str(e)[:160].replace("\n", " ")
    r["total_s"] = round(time.time() - t2, 1)
    rows.append(r)
    print(f"  {r['map']:32s} {r['result']:16s} {r.get('total_s')}s {r.get('msg','')}", flush=True)

io.open(os.path.join(HERE, "results_mapwalk.json"), "w", encoding="utf-8").write(
    json.dumps(rows, indent=1, ensure_ascii=False))
print("done", flush=True)
