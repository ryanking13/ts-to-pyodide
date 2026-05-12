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

class Headers:
    _binding: Any

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._binding = js.Headers.new(*args, **kwargs)

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Headers:
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

    def get(self, name: str) -> str | None:
        return _jsnull_to_none(self._binding.get(name))

    def set(self, name: str, value: str) -> None:
        self._binding.set(name, value)

    def has(self, name: str) -> bool:
        return self._binding.has(name)

    def delete(self, name: str) -> None:
        self._binding.delete(name)
