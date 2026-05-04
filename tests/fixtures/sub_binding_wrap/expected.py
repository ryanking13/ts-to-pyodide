from __future__ import annotations
from typing import Any, overload
from pyodide.ffi import JsBuffer, JsProxy, create_proxy, to_js

def _jsnull_to_none(value: Any) -> Any:
    try:
        from pyodide.ffi import jsnull
    except ImportError:
        return value
    if value is jsnull:
        return None
    return value

class D1Database:
    _binding: Any

    def __init__(self, binding: JsProxy) -> None:
        self._binding = binding

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    def prepare(self, query: str) -> D1PreparedStatement:
        return D1PreparedStatement(self._binding.prepare(query))

    async def exec(self, query: str) -> Any:
        return await self._binding.exec(query)


class D1PreparedStatement:
    _binding: Any

    def __init__(self, binding: JsProxy) -> None:
        self._binding = binding

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
