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

    @overload
    async def get(self, key: str, options: Any | None = None) -> str | None: ...
    @overload
    async def get(self, key: str, type_: Literal["text"]) -> str | None: ...
    @overload
    async def get(self, key: str, type_: Literal["json"]) -> Any | None: ...
    @overload
    async def get(self, key: str, type_: Literal["arrayBuffer"]) -> JsBuffer | None: ...
    @overload
    async def get(self, key: str, type_: Literal["stream"]) -> Any | None: ...
    @overload
    async def get(self, key: str, options: KVNamespaceGetOptions | None = None) -> str | None: ...
    @overload
    async def get(self, key: str, options: KVNamespaceGetOptions | None = None) -> Any | None: ...
    @overload
    async def get(self, key: str, options: KVNamespaceGetOptions | None = None) -> JsBuffer | None: ...
    @overload
    async def get(self, key: str, options: KVNamespaceGetOptions | None = None) -> Any | None: ...
    @overload
    async def get(self, key: Any, type_: Literal["text"]) -> Any: ...
    @overload
    async def get(self, key: Any, type_: Literal["json"]) -> Any: ...
    @overload
    async def get(self, key: Any, options: Any | None = None) -> Any: ...
    @overload
    async def get(self, key: Any, options: KVNamespaceGetOptions | None = None) -> Any: ...
    @overload
    async def get(self, key: Any, options: KVNamespaceGetOptions | None = None) -> Any: ...
    async def get(self, *args: Any, **kwargs: Any) -> Any:
        return await self._binding.get(*args, **kwargs)

    async def list(self, options: KVNamespaceListOptions | None = None) -> KVNamespaceListResult:
        return _from_js_opts(await self._binding.list(_to_js_opts(options)))

    async def put(self, key: str, value: str | JsBuffer | ArrayBufferView | Any, options: KVNamespacePutOptions | None = None) -> None:
        await self._binding.put(key, to_js(value), _to_js_opts(options))

    @overload
    async def get_with_metadata(self, key: str, options: Any | None = None) -> KVNamespaceGetWithMetadataResult: ...
    @overload
    async def get_with_metadata(self, key: str, type_: Literal["text"]) -> KVNamespaceGetWithMetadataResult: ...
    @overload
    async def get_with_metadata(self, key: str, type_: Literal["json"]) -> KVNamespaceGetWithMetadataResult: ...
    @overload
    async def get_with_metadata(self, key: str, type_: Literal["arrayBuffer"]) -> KVNamespaceGetWithMetadataResult: ...
    @overload
    async def get_with_metadata(self, key: str, type_: Literal["stream"]) -> KVNamespaceGetWithMetadataResult: ...
    @overload
    async def get_with_metadata(self, key: str, options: KVNamespaceGetOptions) -> KVNamespaceGetWithMetadataResult: ...
    @overload
    async def get_with_metadata(self, key: str, options: KVNamespaceGetOptions) -> KVNamespaceGetWithMetadataResult: ...
    @overload
    async def get_with_metadata(self, key: str, options: KVNamespaceGetOptions) -> KVNamespaceGetWithMetadataResult: ...
    @overload
    async def get_with_metadata(self, key: str, options: KVNamespaceGetOptions) -> KVNamespaceGetWithMetadataResult: ...
    @overload
    async def get_with_metadata(self, key: Any, type_: Literal["text"]) -> Any: ...
    @overload
    async def get_with_metadata(self, key: Any, type_: Literal["json"]) -> Any: ...
    @overload
    async def get_with_metadata(self, key: Any, options: Any | None = None) -> Any: ...
    @overload
    async def get_with_metadata(self, key: Any, options: KVNamespaceGetOptions | None = None) -> Any: ...
    @overload
    async def get_with_metadata(self, key: Any, options: KVNamespaceGetOptions | None = None) -> Any: ...
    async def get_with_metadata(self, *args: Any, **kwargs: Any) -> Any:
        return await self._binding.getWithMetadata(*args, **kwargs)

    async def delete(self, key: str) -> None:
        await self._binding.delete(key)

    @overload
    async def __getitem__(self, key: str, options: Any | None = None) -> str | None: ...
    @overload
    async def __getitem__(self, key: str, type_: Literal["text"]) -> str | None: ...
    @overload
    async def __getitem__(self, key: str, type_: Literal["json"]) -> Any | None: ...
    @overload
    async def __getitem__(self, key: str, type_: Literal["arrayBuffer"]) -> JsBuffer | None: ...
    @overload
    async def __getitem__(self, key: str, type_: Literal["stream"]) -> Any | None: ...
    @overload
    async def __getitem__(self, key: str, options: KVNamespaceGetOptions | None = None) -> str | None: ...
    @overload
    async def __getitem__(self, key: str, options: KVNamespaceGetOptions | None = None) -> Any | None: ...
    @overload
    async def __getitem__(self, key: str, options: KVNamespaceGetOptions | None = None) -> JsBuffer | None: ...
    @overload
    async def __getitem__(self, key: str, options: KVNamespaceGetOptions | None = None) -> Any | None: ...
    @overload
    async def __getitem__(self, key: Any, type_: Literal["text"]) -> Any: ...
    @overload
    async def __getitem__(self, key: Any, type_: Literal["json"]) -> Any: ...
    @overload
    async def __getitem__(self, key: Any, options: Any | None = None) -> Any: ...
    @overload
    async def __getitem__(self, key: Any, options: KVNamespaceGetOptions | None = None) -> Any: ...
    @overload
    async def __getitem__(self, key: Any, options: KVNamespaceGetOptions | None = None) -> Any: ...
    async def __getitem__(self, *args: Any, **kwargs: Any) -> Any:
        return await self._binding.__getitem__(*args, **kwargs)

    async def __delitem__(self, key: str) -> None:
        await self._binding.__delitem__(key)


class KVNamespaceGetOptions(TypedDict):
    type_: Any
    cache_ttl: int | float | None


class KVNamespaceListOptions(TypedDict, total=False):
    limit: int | float
    prefix: str | None
    cursor: str | None


class ArrayBufferView(TypedDict):
    buffer: Any
    byte_length: int | float
    byte_offset: int | float


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
