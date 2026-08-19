# -*- coding: utf-8 -*-
"""에디터 뷰포트를 게임 뷰로 전환한다.

CaptureViewport는 PIE 없이 에디터 뷰포트를 렌더하므로 라이트 아이콘, 그리드,
좌하단 축 기즈모가 그대로 찍힌다. bShowUI 플래그로도, 컴포넌트 가시성으로도
전부 없앨 수는 없어서 뷰포트 자체를 게임 뷰(단축키 G)로 돌린다.
콘솔 CVar 경로는 입력란에 텍스트는 들어가지만 Enter 커밋이 먹지 않아 쓸 수 없었다.
"""
import json
import re

S = "SlateInspectorToolset.SlateInspectorToolset"


def viewport_ref(u):
    snap = u.call(S, "Snapshot", {"ref": "", "maxDepth": 30})
    s = snap if isinstance(snap, str) else json.dumps(snap)
    best = None
    for m in re.finditer(r'splitter \[pos=\d+,\d+ size=(\d+),(\d+)\] \[ref=(sp\d+)\]', s):
        w, h = int(m.group(1)), int(m.group(2))
        if 800 < w < 1800 and h > 600:
            best = m.group(3)          # 가장 안쪽(마지막) 스플리터가 뷰포트다
    return best


def toggle(u):
    ref = viewport_ref(u)
    if not ref:
        raise RuntimeError("viewport widget not found")
    u.call(S, "Click", {"ref": ref})
    u.call(S, "PressKey", {"key": "G"})
    u.call("EditorToolset.EditorAppToolset", "SelectActors", {"actors": []})
    return ref


if __name__ == "__main__":
    from ue_mcp import UE
    print(toggle(UE()))


def _has_gizmo(path):
    """좌하단 월드 축 기즈모(파란 Z축)가 찍혔는지 본다."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    box = im.crop((0, im.height - 90, 90, im.height))
    n = 0
    for r, g, b in box.getdata():
        if b > 130 and b > r + 55:
            n += 1
    return n >= 6


def ensure(u, cam, verbose=True):
    """게임 뷰가 켜질 때까지 토글한다. G는 토글이라 상태 확인이 필요하다."""
    from ue_mcp import UE  # noqa
    name, loc, rot = cam
    for i in range(3):
        p = u.capture("shots/_gvchk.png", loc, rot)
        if not _has_gizmo(p):
            if verbose:
                print("game view: on")
            return True
        toggle(u)
    if verbose:
        print("game view: FAILED")
    return False
