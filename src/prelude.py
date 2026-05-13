from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal, Never, TypedDict, overload
import js
from pyodide.ffi import JsBuffer, JsProxy, create_proxy, to_js as _raw_to_js

try:
    from pyodide.ffi import jsnull as _JSNULL
except ImportError:
    _JSNULL = None

__all__ = [
    "Any", "Literal", "Never", "TypedDict", "overload",
    "js", "JsBuffer", "JsProxy", "create_proxy", "to_js",
    "datetime", "timezone",
    "_jsnull_to_none", "to_py", "_none_to_jsnull",
    "_to_js_date", "_from_js_date",
    "Headers",
]

def to_js(obj: Any, **kwargs: Any) -> Any:
    if hasattr(obj, "_js_obj"):
        return obj._js_obj
    if "dict_converter" not in kwargs:
        kwargs["dict_converter"] = js.Object.fromEntries
    return _raw_to_js(obj, **kwargs)

def _jsnull_to_none(value: Any) -> Any:
    if _JSNULL is not None and value is _JSNULL:
        return None
    return value

def to_py(value: Any) -> Any:
    if isinstance(value, JsProxy):
        try:
            value = value.to_py()
        except Exception:
            return value
    if isinstance(value, dict):
        return {k: to_py(_jsnull_to_none(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [to_py(_jsnull_to_none(v)) for v in value]
    return value

def _none_to_jsnull(value: Any) -> Any:
    if value is None and _JSNULL is not None:
        return _JSNULL
    return value

def _to_js_date(dt: datetime | JsProxy) -> JsProxy:
    if isinstance(dt, JsProxy):
        return dt
    return js.Date.new(int(dt.timestamp() * 1000))

def _from_js_date(js_date: Any) -> datetime:
    return datetime.fromtimestamp(js_date.getTime() / 1000, tz=timezone.utc)

class Headers:
    _js_obj: Any

    def __init__(self, init: dict[str, str] | list[tuple[str, str]] | JsProxy | Headers | None = None) -> None:
        if init is None:
            self._js_obj = js.Headers.new()
        elif isinstance(init, Headers):
            self._js_obj = init._js_obj
        elif isinstance(init, dict):
            self._js_obj = js.Headers.new(to_js(list(init.items())))
        elif isinstance(init, list):
            self._js_obj = js.Headers.new(to_js(init))
        else:
            self._js_obj = init

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Headers:
        instance = object.__new__(cls)
        instance._js_obj = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._js_obj

    def get(self, name: str) -> str | None:
        return _jsnull_to_none(self._js_obj.get(name))

    def get_all(self, name: str) -> list[str]:
        return list(self._js_obj.getAll(name))

    def has(self, name: str) -> bool:
        return self._js_obj.has(name)

    def set(self, name: str, value: str) -> None:
        self._js_obj.set(name, value)

    def append(self, name: str, value: str) -> None:
        self._js_obj.append(name, value)

    def delete(self, name: str) -> None:
        self._js_obj.delete(name)

    def entries(self) -> list[tuple[str, str]]:
        return list(self._js_obj.entries())

    def keys(self) -> list[str]:
        return list(self._js_obj.keys())

    def values(self) -> list[str]:
        return list(self._js_obj.values())

    def to_dict(self) -> dict[str, str]:
        return dict(self._js_obj.entries())

    def __iter__(self) -> Any:
        return iter(self.entries())

    def __len__(self) -> int:
        return len(self.entries())

    def __contains__(self, name: str) -> bool:
        return self.has(name)

    def __repr__(self) -> str:
        return f"Headers({self.to_dict()!r})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Headers) and self._js_obj == other._js_obj

    def __hash__(self) -> int:
        return id(self._js_obj)
