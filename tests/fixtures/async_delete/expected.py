class KV:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> KV:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    async def delete(self, key: str) -> None:
        await self._binding.delete(key)
