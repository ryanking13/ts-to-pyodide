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

def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])

def _to_snake(s: str) -> str:
    import re
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()

def _to_js_opts(opts: Any) -> Any:
    if opts is None:
        return None
    return to_js({_to_camel(k): v for k, v in opts.items() if v is not None})

def _from_js_opts(js_obj: Any) -> Any:
    if js_obj is None:
        return None
    return {_to_snake(k): v for k, v in js_obj.to_py().items()}

def _to_js_headers(headers: dict[str, str] | list[tuple[str, str]] | JsProxy) -> JsProxy:
    if isinstance(headers, dict):
        return js.Headers.new(list(headers.items()))
    elif isinstance(headers, list):
        return js.Headers.new(headers)
    return headers

class D1Database:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> D1Database:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    def prepare(self, query: str) -> D1PreparedStatement:
        return D1PreparedStatement.from_js(self._binding.prepare(query))

    async def exec(self, query: str) -> Any:
        return await self._binding.exec(query)


class D1PreparedStatement:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> D1PreparedStatement:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    async def first(self, col_name: str | None = None) -> Any:
        return await self._binding.first(col_name)

    async def run(self) -> Any:
        return await self._binding.run()

    async def all(self) -> Any:
        return await self._binding.all()
