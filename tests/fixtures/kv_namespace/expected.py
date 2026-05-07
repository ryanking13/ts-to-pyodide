from __future__ import annotations
from typing import Any, Literal, TypedDict, overload
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

class KVNamespace:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> KVNamespace:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, _to_snake(key))

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, _to_snake(key), value)

    async def get(self, *args: Any, **kwargs: Any) -> Any:
        _a = list(args)
        if len(_a) > 0:
            _a[0] = to_js(_a[0])
        if len(_a) > 1 and isinstance(_a[1], dict):
            _a[1] = _to_js_opts(_a[1])
        _r = await self._binding.get(*_a, **kwargs)
        if isinstance(args[0], str):
            return _jsnull_to_none(_r)
        elif isinstance(args[0], list):
            return (_r).to_py()
        return _r

    async def list(self, options: KVNamespaceListOptions | None = None) -> KVNamespaceListResult:
        return _from_js_opts(await self._binding.list(_to_js_opts(options)))

    async def put(self, key: str, value: str | JsBuffer | Any, options: KVNamespacePutOptions | None = None) -> None:
        await self._binding.put(key, to_js(value), _to_js_opts(options))

    async def get_with_metadata(self, *args: Any, **kwargs: Any) -> Any:
        _a = list(args)
        if len(_a) > 0:
            _a[0] = to_js(_a[0])
        if len(_a) > 1 and isinstance(_a[1], dict):
            _a[1] = _to_js_opts(_a[1])
        _r = await self._binding.getWithMetadata(*_a, **kwargs)
        if isinstance(args[0], str):
            return _from_js_opts(_r)
        elif isinstance(args[0], list):
            return (_r).to_py()
        return _r

    async def delete(self, key: str) -> None:
        await self._binding.delete(key)


class KVNamespaceGetOptions(TypedDict):
    type_: Any
    cache_ttl: int | float | None


class KVNamespaceListOptions(TypedDict, total=False):
    limit: int | float
    prefix: str | None
    cursor: str | None


class KVNamespacePutOptions(TypedDict, total=False):
    expiration: int | float
    expiration_ttl: int | float
    metadata: Any | None


class KVNamespaceGetWithMetadataResult(TypedDict):
    value: Any | None
    metadata: Any | None
    cache_status: str | None


class KVNamespaceListKey(TypedDict):
    name: str
    expiration: int | float | None
    metadata: Any | None


class KVNamespaceListResult(TypedDict):
    list_complete: bool
    keys: list[KVNamespaceListKey]
    cursor: str | None
    cache_status: str | None
