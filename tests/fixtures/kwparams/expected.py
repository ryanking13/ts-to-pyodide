from __future__ import annotations
from prelude import (  # noqa: F401
    Any, Literal, Never, TypedDict, overload,
    js, JsBuffer, JsProxy, create_proxy, to_js,
    datetime, timezone,
    _jsnull_to_none, _auto_to_py, _none_to_jsnull,
    _to_js_date, _from_js_date,
    Headers,
)

class KVStore:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> KVStore:
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

    async def put(self, key: str, value: str, options: KVPutOptions | None = None) -> None:
        await self._binding.put(key, value, to_js(options))

    async def get(self, key: str) -> str | None:
        return _jsnull_to_none(await self._binding.get(key))


class KVPutOptions(TypedDict, total=False):
    expiration: int | float
    expirationTtl: int | float
    metadata: Any
