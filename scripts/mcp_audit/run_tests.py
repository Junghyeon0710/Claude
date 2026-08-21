# -*- coding: utf-8 -*-
"""자동화 테스트를 필터로 돌리고 결과를 집계한다."""
import json, sys, time, io, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "lighting_presets"))
from ue_mcp import UE

AT = "AutomationTestToolset.AutomationTestToolset"
HERE = os.path.dirname(os.path.abspath(__file__))


def unwrap(r):
    return json.loads(r) if isinstance(r, str) else r


def run(u, names=None, flt=None, poll=10, budget=3600, label="run"):
    u.call(AT, "DiscoverTests", {})
    if flt is not None:
        u.call(AT, "RunTestsByFilter", {"filterExpression": flt})
    else:
        u.call(AT, "RunTests", {"testNames": names})
    t0 = time.time()
    last = None
    while time.time() - t0 < budget:
        st = unwrap(u.call(AT, "GetTestStatus", {}))
        s = json.dumps(st, ensure_ascii=False)[:160]
        if s != last:
            print(f"  [{int(time.time()-t0):5d}s] {s}")
            last = s
        state = (st or {}).get("state") or (st or {}).get("status")
        if state and str(state).lower() in ("complete", "completed", "idle", "ready", "finished"):
            break
        time.sleep(poll)
    res = unwrap(u.call(AT, "GetTestResults", {}))
    io.open(os.path.join(HERE, "results_%s.json" % label), "w", encoding="utf-8").write(
        json.dumps(res, indent=1, ensure_ascii=False))
    return res


def summarize(res):
    rows = (res.get("tests") or res.get("results")) if isinstance(res, dict) else res
    if not isinstance(rows, list):
        print("  (unexpected shape)", str(res)[:300]); return
    c = collections.Counter()
    fails = []
    for r in rows:
        state = str(r.get("state") or r.get("result") or "?")
        c[state] += 1
        if state.lower() not in ("success", "passed"):
            fails.append(r)
    print("  ", dict(c))
    return fails


if __name__ == "__main__":
    u = UE()
    label = sys.argv[1]
    flt = sys.argv[2]
    print("== filter:", flt)
    res = run(u, flt=flt, label=label)
    summarize(res)
