# -*- coding: utf-8 -*-
"""시간대 프리셋 값.

프로퍼티 키는 전부 camelCase(엔진 리플렉션 이름)여야 한다. 하나라도 틀리면
get/set 호출 전체가 실패한다.
"""

def rgb(r, g, b, a=1.0):
    return {"r": r, "g": g, "b": b, "a": a}


SODIUM = dict(bUseTemperature=True, intensityUnits="Lumens", castShadows=True,
              sourceRadius=6.0, bCastVolumetricShadow=False)

# ─────────────────────────────────────────────────────────────────────────
# 1) 여명 — 차가운 청록 하늘 vs 따뜻한 나트륨등. 색 대비가 이 씬의 전부다.
# ─────────────────────────────────────────────────────────────────────────
BLUEHOUR = {
    "sun_rot": (0.5, 170.0),          # 태양이 지평선 바로 아래 → 지평선만 옅게 트인다
    "dir": {
        "intensity": 0.62,
        "bUseTemperature": True,
        "temperature": 2900.0,
        "volumetricScatteringIntensity": 1.5,
        "lightSourceAngle": 1.5,
        "indirectLightingIntensity": 0.7,
    },
    "sky": {"intensity": 2.4, "volumetricScatteringIntensity": 1.2},
    "fog": {
        "fogDensity": 0.055,
        "fogHeightFalloff": 0.10,
        "fogInscatteringLuminance": rgb(0.055, 0.10, 0.20),
        "bEnableVolumetricFog": True,
        "volumetricFogScatteringDistribution": 0.2,
        "volumetricFogAlbedo": rgb(0.70, 0.82, 1.0),
        "volumetricFogExtinctionScale": 0.9,
        "volumetricFogDistance": 24000.0,
        "startDistance": 400.0,
        "fogMaxOpacity": 0.82,
        "directionalInscatteringLuminance": rgb(0.60, 0.30, 0.14),
        "directionalInscatteringExponent": 16.0,
        "directionalInscatteringStartDistance": 1000.0,
    },
    "points": dict(intensity=2050.0, intensityUnits="Lumens", bUseTemperature=True,
                   temperature=2050.0, attenuationRadius=1400.0, sourceRadius=16.0,
                   volumetricScatteringIntensity=5.0, castShadows=True),
    "spots": {
        "street": dict(SODIUM, temperature=2150.0, intensity=5400.0, attenuationRadius=1600.0,
                       innerConeAngle=18.0, outerConeAngle=52.0, volumetricScatteringIntensity=4.0),
        "pier":   dict(SODIUM, temperature=2150.0, intensity=6600.0, attenuationRadius=1900.0,
                       innerConeAngle=16.0, outerConeAngle=46.0, volumetricScatteringIntensity=4.5),
        "yard":   dict(SODIUM, temperature=2200.0, intensity=8400.0, attenuationRadius=2200.0,
                       innerConeAngle=20.0, outerConeAngle=55.0, volumetricScatteringIntensity=4.0),
        "crane":  dict(SODIUM, temperature=3400.0, intensity=15600.0, attenuationRadius=4000.0,
                       innerConeAngle=10.0, outerConeAngle=32.0, volumetricScatteringIntensity=5.5),
    },
    "ppv": {
        "autoExposureMethod": "AEM_Manual",
        "autoExposureMinBrightness": 1.0,
        "autoExposureMaxBrightness": 1.0,
        "autoExposureBias": 8.2,     # 하늘이 화면을 지배해야 야간과 구분된다
        "bloomIntensity": 0.75,
        "colorSaturation": rgb(1.02, 1.0, 1.08),
        "colorContrast": rgb(1.06, 1.05, 1.02),
        "colorGainShadows": rgb(0.84, 0.94, 1.18),
        "colorGainHighlights": rgb(1.10, 1.0, 0.88),
        "vignetteIntensity": 0.32,
        "filmGrainIntensity": 0.12,
        "sceneFringeIntensity": 0.3,
    },
}


# ─────────────────────────────────────────────────────────────────────────
# 2) 황혼 — 볼류메트릭 갓레이와 긴 그림자. 태양 방위각이 이 씬의 전부다.
# ─────────────────────────────────────────────────────────────────────────
GOLDENHOUR = {
    # 고도 6도. 도로 축(+X)에서 살짝 비껴 놓아야 소실점의 태양이 대칭으로 굳지 않는다.
    # 측면광도 시험했지만 태양이 화면 밖으로 나가 밋밋해져 역광을 택했다.
    "sun_rot": (-6.0, 174.0),
    "dir": {
        "intensity": 22.0,
        "bUseTemperature": True,
        "temperature": 2700.0,
        "volumetricScatteringIntensity": 10.0,  # 갓레이의 세기
        "bEnableLightShaftBloom": False,        # 켜면 화면 전체가 주황 안개로 덮인다
        "lightSourceAngle": 0.6,
        "indirectLightingIntensity": 1.0,
        "bCastVolumetricShadow": True,
    },
    "sky": {"intensity": 5.5, "volumetricScatteringIntensity": 0.6},   # 그늘진 부두를 읽히게
    "fog": {
        "fogDensity": 0.07,
        "fogHeightFalloff": 0.12,
        "fogInscatteringLuminance": rgb(0.16, 0.19, 0.27),   # 그늘을 청색으로 채운다
        "bEnableVolumetricFog": True,
        "volumetricFogScatteringDistribution": 0.75,   # 전방 산란 → 태양 쪽이 밝게 탄다
        "volumetricFogAlbedo": rgb(1.0, 0.95, 0.88),
        "volumetricFogExtinctionScale": 1.1,
        "volumetricFogDistance": 26000.0,
        "startDistance": 300.0,
        "fogMaxOpacity": 0.9,
        "directionalInscatteringLuminance": rgb(0.95, 0.46, 0.18),
        # 지수를 낮추면 태양을 등진 부두까지 붉은 안개가 덮여 형체가 묻힌다.
        "directionalInscatteringExponent": 14.0,
        "directionalInscatteringStartDistance": 800.0,
    },
    # 황혼에는 아직 대부분 꺼져 있다 — 몇 개만 예열된 듯 들어온다
    "points": dict(intensity=2600.0, intensityUnits="Lumens", bUseTemperature=True,
                   temperature=2200.0, attenuationRadius=1200.0, sourceRadius=14.0,
                   volumetricScatteringIntensity=1.5, castShadows=False),
    "spots": {
        "street": dict(SODIUM, temperature=2200.0, intensity=5200.0, attenuationRadius=1400.0,
                       innerConeAngle=18.0, outerConeAngle=52.0, volumetricScatteringIntensity=1.2),
        "pier":   dict(SODIUM, temperature=2200.0, intensity=8000.0, attenuationRadius=1700.0,
                       innerConeAngle=16.0, outerConeAngle=46.0, volumetricScatteringIntensity=1.2),
        "yard":   dict(SODIUM, temperature=2250.0, intensity=8000.0, attenuationRadius=1900.0,
                       innerConeAngle=20.0, outerConeAngle=55.0, volumetricScatteringIntensity=1.2),
        "crane":  dict(SODIUM, temperature=3400.0, intensity=16000.0, attenuationRadius=3200.0,
                       innerConeAngle=10.0, outerConeAngle=32.0, volumetricScatteringIntensity=1.5),
    },
    "ppv": {
        "autoExposureMethod": "AEM_Manual",
        "autoExposureMinBrightness": 1.0,
        "autoExposureMaxBrightness": 1.0,
        "autoExposureBias": 5.0,
        "bloomIntensity": 0.85,
        "colorSaturation": rgb(1.06, 1.02, 0.98),
        "colorContrast": rgb(1.08, 1.06, 1.04),
        "colorGainShadows": rgb(0.78, 0.90, 1.24),
        "colorGainHighlights": rgb(1.12, 1.02, 0.86),
        "vignetteIntensity": 0.30,
        "filmGrainIntensity": 0.10,
        "sceneFringeIntensity": 0.25,
    },
}


# ─────────────────────────────────────────────────────────────────────────
# 3) 야간 조업 — 화면을 만드는 건 전부 인공광. 어둡되 형체는 읽혀야 한다.
# ─────────────────────────────────────────────────────────────────────────
NIGHT = {
    "sun_rot": (-52.0, 35.0),         # 달. 높이 떠 있어 그림자가 짧고 푸르다
    "dir": {
        "intensity": 0.30,
        "bUseTemperature": True,
        "temperature": 9000.0,        # 푸른 기
        "volumetricScatteringIntensity": 0.8,
        "lightSourceAngle": 2.0,
        "indirectLightingIntensity": 0.5,
        "bEnableLightShaftBloom": False,
    },
    "sky": {"intensity": 0.45, "volumetricScatteringIntensity": 1.0},
    "fog": {
        "fogDensity": 0.06,
        "fogHeightFalloff": 0.10,
        "fogInscatteringLuminance": rgb(0.020, 0.035, 0.070),
        "bEnableVolumetricFog": True,
        "volumetricFogScatteringDistribution": 0.25,
        "volumetricFogAlbedo": rgb(0.75, 0.84, 1.0),
        "volumetricFogExtinctionScale": 1.2,
        "volumetricFogDistance": 24000.0,
        "startDistance": 300.0,
        "fogMaxOpacity": 0.9,
        "directionalInscatteringLuminance": rgb(0.06, 0.10, 0.20),
        "directionalInscatteringExponent": 20.0,
        "directionalInscatteringStartDistance": 2000.0,
    },
    "points": dict(intensity=4200.0, intensityUnits="Lumens", bUseTemperature=True,
                   temperature=2000.0, attenuationRadius=1500.0, sourceRadius=18.0,
                   volumetricScatteringIntensity=5.5, castShadows=True),
    "spots": {
        "street": dict(SODIUM, temperature=2100.0, intensity=11000.0, attenuationRadius=1800.0,
                       innerConeAngle=16.0, outerConeAngle=54.0, volumetricScatteringIntensity=5.0),
        "pier":   dict(SODIUM, temperature=2100.0, intensity=14000.0, attenuationRadius=2100.0,
                       innerConeAngle=14.0, outerConeAngle=48.0, volumetricScatteringIntensity=5.5),
        "yard":   dict(SODIUM, temperature=2150.0, intensity=17000.0, attenuationRadius=2400.0,
                       innerConeAngle=18.0, outerConeAngle=56.0, volumetricScatteringIntensity=5.0),
        "crane":  dict(SODIUM, temperature=3600.0, intensity=34000.0, attenuationRadius=4500.0,
                       innerConeAngle=9.0, outerConeAngle=30.0, volumetricScatteringIntensity=6.5),
    },
    "ppv": {
        "autoExposureMethod": "AEM_Manual",
        "autoExposureMinBrightness": 1.0,
        "autoExposureMaxBrightness": 1.0,
        "autoExposureBias": 6.5,
        "bloomIntensity": 0.95,
        "colorSaturation": rgb(1.0, 0.98, 1.10),
        "colorContrast": rgb(1.08, 1.06, 1.02),
        "colorGainShadows": rgb(0.72, 0.88, 1.30),
        "colorGainHighlights": rgb(1.12, 1.00, 0.84),
        "vignetteIntensity": 0.38,
        "filmGrainIntensity": 0.16,
        "sceneFringeIntensity": 0.35,
    },
}
