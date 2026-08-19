# -*- coding: utf-8 -*-
"""프리셋용 레벨 사본을 만든다. duplicate 직후 저장하지 않으면 load_level이 실패한다."""
from ue_mcp import UE
from cameras import LEVEL_BASE, LEVEL_OF

u = UE()
for name, path in LEVEL_OF.items():
    if u.asset("exists", path=path):
        print("skip (exists):", path)
        continue
    u.asset("duplicate", path=LEVEL_BASE, new_path=path)
    u.asset("save_assets", asset_paths=[path])
    print("created:", path)
print("done")
