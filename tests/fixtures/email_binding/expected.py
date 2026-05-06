from __future__ import annotations
from typing import Any, TypedDict, overload
import js
from pyodide.ffi import JsBuffer, JsProxy, create_proxy, to_js

def _call_js_method(binding: Any, method: str, *args: Any, **kwargs: Any) -> Any:
    return js.Reflect.get(binding, method)(*args, **kwargs)

def _jsnull_to_none(value: Any) -> Any:
    try:
        from pyodide.ffi import jsnull
    except ImportError:
        return value
    if value is jsnull:
        return None
    return value

def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])

def _to_snake(s: str) -> str:
    import re
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()

def _to_js_opts(opts: Any) -> Any:
    if opts is None:
        return None
    def _convert(v: Any) -> Any:
        if isinstance(v, dict):
            return {_to_camel(k): _convert(val) for k, val in v.items() if val is not None}
        if isinstance(v, list):
            return [_convert(item) for item in v]
        return v
    return to_js(_convert(opts))

def _from_js_opts(js_obj: Any) -> Any:
    if js_obj is None:
        return None
    def _convert(v: Any) -> Any:
        if isinstance(v, dict):
            return {_to_snake(k): _convert(val) for k, val in v.items()}
        if isinstance(v, list):
            return [_convert(item) for item in v]
        return v
    return _convert(js_obj.to_py())

def _to_js_headers(headers: dict[str, str] | list[tuple[str, str]] | JsProxy) -> JsProxy:
    if isinstance(headers, dict):
        return js.Headers.new(list(headers.items()))
    elif isinstance(headers, list):
        return js.Headers.new(headers)
    return headers

def _from_js_headers(js_headers: Any) -> Any:
    import http.client
    result = http.client.HTTPMessage()
    for key, val in js_headers:
        result[key] = val
    return result

class SendEmail:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> SendEmail:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    async def send(self, message: EmailMessage) -> EmailSendResult:
        return _from_js_opts(await _call_js_method(self._binding, "send", _to_js_opts(message)))


class ForwardableEmailMessage:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> ForwardableEmailMessage:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def raw(self) -> Any:
        return self._binding.raw

    @property
    def headers(self) -> http.client.HTTPMessage:
        return _from_js_headers(self._binding.headers)

    @property
    def raw_size(self) -> int | float:
        return self._binding.rawSize

    def set_reject(self, reason: str) -> None:
        self._binding.setReject(reason)

    async def forward(self, rcpt_to: str, headers: dict[str, str] | list[tuple[str, str]] | JsProxy | None = None) -> EmailSendResult:
        return _from_js_opts(await self._binding.forward(rcpt_to, _to_js_headers(headers) if headers is not None else None))

    async def reply(self, message: EmailMessage) -> EmailSendResult:
        return _from_js_opts(await self._binding.reply(_to_js_opts(message)))


class EmailMessage(TypedDict):
    from_: str
    to: str


class EmailSendResult(TypedDict):
    message_id: str
