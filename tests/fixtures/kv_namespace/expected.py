from __future__ import annotations
from prelude import *

class KVNamespace:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> KVNamespace:
        instance = object.__new__(cls)
        instance._js_obj = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._js_obj

    def __getattr__(self, name: str) -> Any:
        return getattr(self._js_obj, name)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._js_obj == other._js_obj

    def __hash__(self) -> int:
        return id(self._js_obj)

    async def get(self, *args: Any, **kwargs: Any) -> Any:
        _a = list(args)
        if len(_a) > 0:
            _a[0] = to_js(_a[0])
        if len(_a) > 1:
            _a[1] = to_js(_a[1])
        _r = await self._js_obj.get(*_a, **kwargs)
        if isinstance(args[0], str):
            return to_py(_jsnull_to_none(_r))
        elif isinstance(args[0], list):
            return to_py(_r)
        return _r

    async def list(self, options: KVNamespaceListOptions | None = None) -> KVNamespaceListResult:
        return to_py(await self._js_obj.list(to_js(options)))

    async def put(self, key: str, value: str | JsBuffer | JsProxy, options: KVNamespacePutOptions | None = None) -> None:
        await self._js_obj.put(key, to_js(value), to_js(options))

    async def get_with_metadata(self, *args: Any, **kwargs: Any) -> Any:
        _a = list(args)
        if len(_a) > 0:
            _a[0] = to_js(_a[0])
        if len(_a) > 1:
            _a[1] = to_js(_a[1])
        _r = await self._js_obj.getWithMetadata(*_a, **kwargs)
        if isinstance(args[0], str):
            return to_py(_r)
        elif isinstance(args[0], list):
            return to_py(_r)
        return _r

    async def delete(self, key: str) -> None:
        await self._js_obj.delete(key)


class KVNamespaceGetOptions(TypedDict):
    type: Any
    cacheTtl: int | float | None


class KVNamespaceListOptions(TypedDict, total=False):
    limit: int | float
    prefix: str | None
    cursor: str | None


class KVNamespacePutOptions(TypedDict, total=False):
    expiration: int | float
    expirationTtl: int | float
    metadata: Any | None


class KVNamespaceGetWithMetadataResult(TypedDict):
    value: Any | None
    metadata: Any | None
    cacheStatus: str | None


class KVNamespaceListKey(TypedDict):
    name: str
    expiration: int | float | None
    metadata: Any | None


class KVNamespaceListResult(TypedDict):
    list_complete: bool
    keys: list[KVNamespaceListKey]
    cursor: str | None
    cacheStatus: str | None
