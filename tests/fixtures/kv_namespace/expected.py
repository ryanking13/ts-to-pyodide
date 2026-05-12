from __future__ import annotations
from prelude import (  # noqa: F401
    Any, Literal, Never, TypedDict, overload,
    js, JsBuffer, JsProxy, create_proxy, to_js,
    datetime, timezone,
    _jsnull_to_none, _auto_to_py, _none_to_jsnull,
    _to_js_date, _from_js_date,
    Headers,
)

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
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._binding == other._binding

    def __hash__(self) -> int:
        return id(self._binding)

    async def get(self, *args: Any, **kwargs: Any) -> Any:
        _a = list(args)
        if len(_a) > 0:
            _a[0] = to_js(_a[0])
        if len(_a) > 1:
            _a[1] = to_js(_a[1])
        _r = await self._binding.get(*_a, **kwargs)
        if isinstance(args[0], str):
            return _auto_to_py(_jsnull_to_none(_r))
        elif isinstance(args[0], list):
            return _auto_to_py(_r)
        return _r

    async def list(self, options: KVNamespaceListOptions | None = None) -> KVNamespaceListResult:
        return _auto_to_py(await self._binding.list(to_js(options)))

    async def put(self, key: str, value: str | JsBuffer | JsProxy, options: KVNamespacePutOptions | None = None) -> None:
        await self._binding.put(key, to_js(value), to_js(options))

    async def get_with_metadata(self, *args: Any, **kwargs: Any) -> Any:
        _a = list(args)
        if len(_a) > 0:
            _a[0] = to_js(_a[0])
        if len(_a) > 1:
            _a[1] = to_js(_a[1])
        _r = await self._binding.getWithMetadata(*_a, **kwargs)
        if isinstance(args[0], str):
            return _auto_to_py(_r)
        elif isinstance(args[0], list):
            return _auto_to_py(_r)
        return _r

    async def delete(self, key: str) -> None:
        await self._binding.delete(key)


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
