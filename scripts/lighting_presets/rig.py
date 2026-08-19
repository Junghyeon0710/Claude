# -*- coding: utf-8 -*-
"""레벨의 라이팅 액터를 찾아 값을 쓰는 얇은 래퍼.

두 가지 함정을 여기서 한 번에 막는다.
  1) get_components는 Billboard/Arrow 같은 에디터 스프라이트도 돌려주므로
     반드시 구체 컴포넌트 타입으로 필터링한다.
  2) 프로퍼티 이름은 camelCase(첫 글자 소문자)다. 이름이 하나라도 틀리면
     get/set 전체가 실패하므로 프리셋 값의 키는 항상 camelCase로 적는다.
"""
import json

CLS = {
    "dir":  ("/Script/Engine.DirectionalLight",     "/Script/Engine.DirectionalLightComponent"),
    "sky":  ("/Script/Engine.SkyLight",             "/Script/Engine.SkyLightComponent"),
    "fog":  ("/Script/Engine.ExponentialHeightFog", "/Script/Engine.ExponentialHeightFogComponent"),
    "atmo": ("/Script/Engine.SkyAtmosphere",        "/Script/Engine.SkyAtmosphereComponent"),
    "cloud":("/Script/Engine.VolumetricCloud",      "/Script/Engine.VolumetricCloudComponent"),
}


class Rig:
    def __init__(self, u):
        self.u = u
        self._cache = {}

    # ---- 탐색 -----------------------------------------------------------
    def find(self, cls, name=""):
        return self.u.scene("find_actors", name=name, tag="", collision_channels=[],
                            actor_type={"refPath": cls}) or []

    def actor(self, key):
        if key not in self._cache:
            r = self.find(CLS[key][0])
            self._cache[key] = r[0] if r else None
        return self._cache[key]

    def comp(self, key):
        ck = key + "#comp"
        if ck not in self._cache:
            a = self.actor(key)
            if not a:
                self._cache[ck] = None
            else:
                c = self.u.actor("get_components", actor=a,
                                 component_type={"refPath": CLS[key][1]})
                self._cache[ck] = c[0] if c else None
        return self._cache[ck]

    def ppv(self):
        if "ppv" not in self._cache:
            r = self.find("/Script/Engine.PostProcessVolume")
            # 언바운드 볼륨을 우선한다.
            pick = None
            for a in r:
                if self.get(a, ["bUnbound"]).get("bUnbound"):
                    pick = a
                    break
            self._cache["ppv"] = pick or (r[0] if r else None)
        return self._cache["ppv"]

    # ---- 읽기/쓰기 ------------------------------------------------------
    def get(self, ref, names):
        r = self.u.get_props(ref, names)
        if isinstance(r, str):
            r = json.loads(r)
        return r

    def set(self, ref, values):
        return self.u.set_props(ref, values)

    def set_comp(self, key, values):
        c = self.comp(key)
        if not c:
            raise RuntimeError("component not found: " + key)
        return self.set(c, values)

    def set_actor_rot(self, key, pitch, yaw, roll=0.0):
        a = self.actor(key)
        return self.u.actor("set_actor_transform", actor=a, worldspace=True,
                            xform={"rotation": {"pitch": pitch, "yaw": yaw, "roll": roll}})

    # ---- 포스트 프로세스 -------------------------------------------------
    def patch_ppv(self, changes):
        """settings 구조체를 통째로 읽어 필요한 키만 갈아끼우고 다시 쓴다.

        부분 dict를 그대로 넘기면 나머지 필드가 기본값으로 밀릴 수 있어
        읽기-수정-쓰기로 처리한다. bOverride_* 플래그도 여기서 함께 켠다.
        """
        a = self.ppv()
        cur = self.get(a, ["settings"])["settings"]
        for k, v in changes.items():
            cur[k] = v
            if not k.startswith("bOverride_"):
                flag = "bOverride_" + k[0].upper() + k[1:]
                if flag in cur:
                    cur[flag] = True
        return self.set(a, {"settings": cur})


def rgb(r, g, b, a=1.0):
    return {"r": r, "g": g, "b": b, "a": a}
