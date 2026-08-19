# -*- coding: utf-8 -*-
"""구역별 대표 카메라 — 세 프리셋에서 정확히 같은 좌표/회전으로 캡처해야 비교가 성립한다.

에디터 뷰포트 FOV는 MCP로 노출되지 않아 뷰포트 기본값(90도)을 그대로 쓴다.
캡처 해상도는 뷰포트 크기를 따라가므로 창을 최대화한 상태에서 찍는다.
"""

# (이름, 위치(x,y,z), 회전(pitch,yaw,roll))
CAMERAS = [
    # B 창고 거리 — 도로 소실점, 우측 창고 벽을 전경에 걸침
    ("B_warehouse", (-5400.0, 1150.0, 172.0), (0.5, 2.0, 0.0)),
    # C 컨테이너 야적장 — Y=1100 협로, 우측 녹슨 기둥이 전경 층을 만든다
    ("C_yard",      ( 3200.0, 1100.0, 180.0), (1.0, 1.0, 0.0)),
    # E 부두 — 부두 난간 소실점 + 갠트리 크레인 실루엣 + 수면 반사
    ("E_pier",      ( 3200.0,-5980.0, 172.0), (1.0, 176.0, 0.0)),
]

# 프리셋별 추가 검증용 보조 구도(비교 이미지에는 쓰지 않는다)
EXTRA = [
    ("B_alt",  (-4800.0, 1250.0, 175.0), (1.0, 1.0, 0.0)),
    ("E_alt",  ( 2600.0,-6000.0, 175.0), (2.0, 172.0, 0.0)),
    ("A_gate", (-9400.0,  900.0, 170.0), (-1.0, 0.0, 0.0)),
]

PRESETS = ["BlueHour", "GoldenHour", "Night"]
LEVEL_BASE = "/Game/IndustrialHarbor_Claude/Level/L_IndustrialHarbor_Claude"
LEVEL_OF = {p: "/Game/IndustrialHarbor_Claude/Level/L_IndustrialHarbor_%s" % p for p in PRESETS}
