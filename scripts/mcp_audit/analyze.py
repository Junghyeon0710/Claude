# -*- coding: utf-8 -*-
"""테스트 결과 JSON을 그룹별 통과/실패로 집계하고 실패 원인을 뽑는다."""
import json, io, sys, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "results_mcp.json")
res = json.load(io.open(path, encoding="utf-8"))
tests = res.get("tests", res if isinstance(res, list) else [])
print("total results:", len(tests))

def group(name, depth=3):
    return ".".join(name.split(".")[:depth])

agg = collections.defaultdict(lambda: [0, 0])
fails = []
for t in tests:
    st = str(t.get("state", "?"))
    g = group(t.get("name", "?"))
    ok = st.lower() in ("success", "passed")
    agg[g][0 if ok else 1] += 1
    if not ok:
        fails.append(t)

print("\n%-52s %6s %6s" % ("group", "pass", "FAIL"))
for g, (p, f) in sorted(agg.items(), key=lambda kv: (-kv[1][1], kv[0])):
    if f or "--all" in sys.argv:
        print("%-52s %6d %6d" % (g, p, f))

print("\n실패 %d건 — 원인 상위" % len(fails))
reasons = collections.Counter()
for t in fails:
    errs = t.get("errors") or []
    msg = (errs[0].get("message") if errs and isinstance(errs[0], dict) else (errs[0] if errs else "")) or "(no message)"
    reasons[str(msg)[:150]] += 1
for m, n in reasons.most_common(15):
    print(f"  [{n:3d}] {m}")

io.open(os.path.join(HERE, "fails.json"), "w", encoding="utf-8").write(
    json.dumps(fails, indent=1, ensure_ascii=False))
