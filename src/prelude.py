from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal, Never, TypedDict, overload
import js
from pyodide.ffi import JsBuffer, JsProxy, create_proxy, to_js as _raw_to_js

def to_js(obj: Any, **kwargs: Any) -> Any:
    if hasattr(obj, "_binding"):
        return obj._binding
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

def _to_js_date(dt: datetime | JsProxy) -> JsProxy:
    if isinstance(dt, JsProxy):
        return dt
    return js.Date.new(int(dt.timestamp() * 1000))

def _from_js_date(js_date: Any) -> datetime:
    return datetime.fromtimestamp(js_date.getTime() / 1000, tz=timezone.utc)

class Headers:
    _binding: Any

    def __init__(self, init: dict[str, str] | list[tuple[str, str]] | JsProxy | Headers | None = None) -> None:
        if init is None:
            self._binding = js.Headers.new()
        elif isinstance(init, Headers):
            self._binding = init._binding
        elif isinstance(init, dict):
            self._binding = js.Headers.new(to_js(list(init.items())))
        elif isinstance(init, list):
            self._binding = js.Headers.new(to_js(init))
        else:
            self._binding = init

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Headers:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def get(self, name: str) -> str | None:
        return _jsnull_to_none(self._binding.get(name))

    def get_all(self, name: str) -> list[str]:
        return list(self._binding.getAll(name))

    def has(self, name: str) -> bool:
        return self._binding.has(name)

    def set(self, name: str, value: str) -> None:
        self._binding.set(name, value)

    def append(self, name: str, value: str) -> None:
        self._binding.append(name, value)

    def delete(self, name: str) -> None:
        self._binding.delete(name)

    def entries(self) -> list[tuple[str, str]]:
        return list(self._binding.entries())

    def keys(self) -> list[str]:
        return list(self._binding.keys())

    def values(self) -> list[str]:
        return list(self._binding.values())

    def to_dict(self) -> dict[str, str]:
        return dict(self._binding.entries())

    def __iter__(self) -> Any:
        return iter(self.entries())

    def __len__(self) -> int:
        return len(self.entries())

    def __contains__(self, name: str) -> bool:
        return self.has(name)

    def __repr__(self) -> str:
        return f"Headers({self.to_dict()!r})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Headers) and self.to_dict() == other.to_dict()

    def __hash__(self) -> int:
        return id(self._binding)
