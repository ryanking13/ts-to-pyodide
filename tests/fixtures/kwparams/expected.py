from __future__ import annotations
from prelude import *

class KVStore:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> KVStore:
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

    async def put(self, key: str, value: str, options: KVPutOptions | None = None) -> None:
        await self._js_obj.put(key, value, to_js(options))

    async def get(self, key: str) -> str | None:
        return _jsnull_to_none(await self._js_obj.get(key))


class KVPutOptions(TypedDict, total=False):
    expiration: int | float
    expirationTtl: int | float
    metadata: Any
