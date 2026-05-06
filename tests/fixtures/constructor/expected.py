from __future__ import annotations
from typing import Any, TypedDict, overload
import js
from pyodide.ffi import JsBuffer, JsProxy, create_proxy, to_js

def _jsnull_to_none(value: Any) -> Any:
    try:
        from pyodide.ffi import jsnull
    except ImportError:
        return value
    if value is jsnull:
        return None
    return value

def _build_opts(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}

def _to_js_headers(headers: dict[str, str] | list[tuple[str, str]] | JsProxy) -> JsProxy:
    if isinstance(headers, dict):
        return js.Headers.new(list(headers.items()))
    elif isinstance(headers, list):
        return js.Headers.new(headers)
    return headers

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

    def get(self, name: str) -> str | None:
        return _jsnull_to_none(self._binding.get(name))

    def set(self, name: str, value: str) -> None:
        self._binding.set(name, value)

    def has(self, name: str) -> bool:
        return self._binding.has(name)

    def delete(self, name: str) -> None:
        self._binding.delete(name)

    def __contains__(self, name: str) -> bool:
        return self._binding.__contains__(name)

    def __getitem__(self, name: str) -> str | None:
        return _jsnull_to_none(self._binding.__getitem__(name))

    def __setitem__(self, name: str, value: str) -> None:
        self._binding.__setitem__(name, value)

    def __delitem__(self, name: str) -> None:
        self._binding.__delitem__(name)
