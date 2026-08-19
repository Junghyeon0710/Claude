"""언리얼 MCP(http://127.0.0.1:8000/mcp) JSON-RPC 직결 클라이언트.

세션에서 MCP 툴이 사라져도 이 경로로 계속 작업할 수 있고,
CaptureViewport의 base64가 대화 컨텍스트를 거치지 않고 곧바로 파일로 떨어진다.
"""
import base64
import json
import os
import urllib.request

ENDPOINT = os.environ.get("UE_MCP_URL", "http://127.0.0.1:8000/mcp")


class UEError(RuntimeError):
    pass


class UE:
    def __init__(self, endpoint=ENDPOINT):
        self.endpoint = endpoint
        self.session_id = None
        self._id = 0
        self._connect()

    # ---- 저수준 ----------------------------------------------------------
    def _post(self, payload, timeout=600):
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        req = urllib.request.Request(self.endpoint, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            sid = resp.headers.get("Mcp-Session-Id")
            if sid:
                self.session_id = sid
            body = resp.read().decode("utf-8", "replace")
        return self._parse(body)

    @staticmethod
    def _parse(body):
        # 서버가 SSE(text/event-stream)로 답할 수 있어 data: 줄을 걷어낸다.
        if not body.strip():
            return None
        for line in body.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
        return json.loads(body)

    def _rpc(self, method, params=None, timeout=600):
        self._id += 1
        payload = {"jsonrpc": "2.0", "id": self._id, "method": method}
        if params is not None:
            payload["params"] = params
        res = self._post(payload, timeout=timeout)
        if res is None:
            return None
        if "error" in res:
            raise UEError(json.dumps(res["error"], ensure_ascii=False))
        return res.get("result")

    def _connect(self):
        self._rpc("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "harbor-lighting", "version": "1.0"},
        })
        self._id += 1
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    # ---- 고수준 ----------------------------------------------------------
    def call(self, toolset, tool, args=None, raw=False, timeout=600):
        """툴셋의 툴 하나를 호출하고 파싱된 결과를 돌려준다."""
        payload = {"tool_name": tool, "arguments": args or {}}
        if toolset:
            payload["toolset_name"] = toolset
        res = self._rpc("tools/call", {"name": "call_tool", "arguments": payload}, timeout=timeout)
        if raw:
            return res
        return self._unwrap(res)

    @staticmethod
    def _unwrap(res):
        if res is None:
            return None
        if res.get("isError"):
            raise UEError(_text_of(res))
        sc = res.get("structuredContent")
        if isinstance(sc, dict) and "result" in sc:
            return _maybe_json(sc["result"])
        txt = _text_of(res)
        if txt:
            try:
                obj = json.loads(txt)
            except json.JSONDecodeError:
                return txt
            if isinstance(obj, dict) and set(obj) == {"returnValue"}:
                return obj["returnValue"]
            return obj
        return res

    # ---- 자주 쓰는 래퍼 --------------------------------------------------
    def scene(self, tool, **kw):
        return self.call("editor_toolset.toolsets.scene.SceneTools", tool, kw)

    def actor(self, tool, **kw):
        return self.call("editor_toolset.toolsets.actor.ActorTools", tool, kw)

    def obj(self, tool, **kw):
        return self.call("editor_toolset.toolsets.object.ObjectTools", tool, kw)

    def asset(self, tool, **kw):
        return self.call("editor_toolset.toolsets.asset.AssetTools", tool, kw)

    def editor(self, tool, **kw):
        return self.call("EditorToolset.EditorAppToolset", tool, kw)

    def mi(self, tool, **kw):
        return self.call("editor_toolset.toolsets.material_instance.MaterialInstanceTools", tool, kw)

    def script(self, code, timeout=900):
        """ProgrammaticToolset 스크립트 실행. 반환값은 run()의 리턴."""
        r = self.call(
            "editor_toolset.toolsets.programmatic.ProgrammaticToolset",
            "execute_tool_script", {"script": code}, timeout=timeout)
        # 결과가 JSON 문자열로 몇 겹 감싸여 오는 경우가 있어 dict가 될 때까지 벗긴다.
        for _ in range(3):
            if isinstance(r, str):
                r = _maybe_json(r)
            else:
                break
        return r

    def set_props(self, ref, values):
        """ObjectTools.set_properties — values는 반드시 JSON '문자열'."""
        return self.obj("set_properties", instance=_ref(ref),
                        values=json.dumps(values))

    def get_props(self, ref, names):
        return self.obj("get_properties", instance=_ref(ref), properties=names)

    def capture(self, out_path, location, rotation, fov=None, width=None, height=None):
        """뷰포트를 지정 카메라로 렌더해 파일로 저장. base64는 컨텍스트를 안 거친다."""
        xform = {
            "location": {"x": location[0], "y": location[1], "z": location[2]},
            "rotation": {"pitch": rotation[0], "yaw": rotation[1], "roll": rotation[2]},
        }
        args = {"captureTransform": xform, "annotations": []}
        if fov is not None:
            args["fov"] = fov
        if width:
            args["width"] = width
        if height:
            args["height"] = height
        res = self.call("EditorToolset.EditorAppToolset", "CaptureViewport", args, raw=True)
        return _save_image(res, out_path)


def _maybe_json(v):
    """구조화 결과가 JSON '문자열'로 오는 경우가 있어 한 번 더 벗긴다."""
    if isinstance(v, str):
        t = v.strip()
        if t[:1] in "[{":
            try:
                return json.loads(t)
            except json.JSONDecodeError:
                return v
    return v


def _ref(ref):
    if isinstance(ref, dict):
        return ref
    return {"refPath": ref}


def _text_of(res):
    parts = []
    for c in res.get("content") or []:
        if c.get("type") == "text":
            parts.append(c.get("text", ""))
    return "\n".join(parts)


def _save_image(res, out_path):
    if res is None:
        raise UEError("capture returned nothing")
    if res.get("isError"):
        raise UEError(_text_of(res))
    data = None
    for c in res.get("content") or []:
        if c.get("type") == "image" and c.get("data"):
            data = c["data"]
            break
    if data is None:
        # 구조화 결과 안에 {"image": {"data": ...}} 로 들어오는 경로.
        sc = res.get("structuredContent") or {}
        blob = sc.get("result")
        if isinstance(blob, str):
            blob = _maybe_json(blob)
        if blob is None:
            blob = _maybe_json(_text_of(res))
        if isinstance(blob, dict):
            blob = blob.get("returnValue", blob)
            if isinstance(blob, dict):
                img = blob.get("image") or blob
                data = img.get("data")
    if not data:
        raise UEError("no image in response: " + _text_of(res)[:300])
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(data))
    return out_path
