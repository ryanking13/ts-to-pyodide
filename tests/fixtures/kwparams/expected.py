from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal, Never, TypedDict, overload
import js
from pyodide.ffi import JsBuffer, JsProxy, create_proxy, to_js as _raw_to_js

def to_js(obj: Any, **kwargs: Any) -> Any:
    if "dict_converter" not in kwargs:
        kwargs["dict_converter"] = js.Object.fromEntries
    return _raw_to_js(obj, **kwargs)

def _jsnull_to_none(value: Any) -> Any:
    try:
        from pyodide.ffi import jsnull
    except ImportError:
        return value
    if value is jsnull:
        return None
    return value

def _auto_to_py(value: Any) -> Any:
    if isinstance(value, JsProxy):
        try:
            value = value.to_py()
        except Exception:
            return value
    if isinstance(value, dict):
        return {k: _auto_to_py(_jsnull_to_none(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [_auto_to_py(_jsnull_to_none(v)) for v in value]
    return value

def _none_to_jsnull(value: Any) -> Any:
    if value is None:
        try:
            from pyodide.ffi import jsnull
            return jsnull
        except ImportError:
            return value
    return value

def _to_js_headers(headers: dict[str, str] | list[tuple[str, str]] | JsProxy) -> JsProxy:
    if isinstance(headers, dict):
        return js.Headers.new(list(headers.items()))
    elif isinstance(headers, list):
        return js.Headers.new(headers)
    return headers

def _to_js_date(dt: datetime | JsProxy) -> JsProxy:
    if isinstance(dt, JsProxy):
        return dt
    return js.Date.new(int(dt.timestamp() * 1000))

def _from_js_date(js_date: Any) -> datetime:
    return datetime.fromtimestamp(js_date.getTime() / 1000, tz=timezone.utc)

class KVStore:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> KVStore:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._binding == other._binding

    def __hash__(self) -> int:
        return id(self._binding)

    async def put(self, key: str, value: str, options: KVPutOptions | None = None) -> None:
        await self._binding.put(key, value, to_js(options))

    async def get(self, key: str) -> str | None:
        return _jsnull_to_none(await self._binding.get(key))


class KVPutOptions(TypedDict, total=False):
    expiration: int | float
    expirationTtl: int | float
    metadata: Any
