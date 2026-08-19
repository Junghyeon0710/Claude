# -*- coding: utf-8 -*-
"""에디터 콘솔에 명령을 보낸다.

MCP에 CVar 설정 툴이 없어서 슬레이트 UI의 Cmd 입력란을 직접 두드린다.
입력란은 접근성 트리 루트 스냅샷에는 안 잡히고, 상태바의 Cmd 메뉴(m20)를
한 번 클릭한 뒤 그 서브트리를 스냅샷해야 textbox가 나타난다.
(PowerShell SendKeys는 Access denied로 막혀 이 경로가 유일하다.)
"""
import re

S = "SlateInspectorToolset.SlateInspectorToolset"


def _find_box(u):
    u.call(S, "Snapshot", {"ref": "", "maxDepth": 30})
    snap = u.call(S, "Snapshot", {"ref": "", "maxDepth": 30})
    m = re.search(r'menu \[pos=\d+,10\d\d[^\]]*\] \[ref=(m\d+)\]', snap if isinstance(snap, str) else "")
    menu_ref = m.group(1) if m else "m20"
    u.call(S, "Click", {"ref": menu_ref})
    sub = u.call(S, "Snapshot", {"ref": menu_ref, "maxDepth": 12})
    t = re.search(r'textbox.*?\[ref=(tb\d+)\]', sub if isinstance(sub, str) else "")
    if not t:
        raise RuntimeError("console textbox not found:\n" + str(sub)[:500])
    return t.group(1)


def run(u, *commands):
    box = _find_box(u)
    for c in commands:
        u.call(S, "Type", {"ref": box, "text": c, "submit": True})
    return box


if __name__ == "__main__":
    import sys
    from ue_mcp import UE
    print(run(UE(), *sys.argv[1:]))
