class ObjectBody:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> ObjectBody:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def etag(self) -> str:
        return self._binding.etag

    @property
    def body(self) -> str:
        return self._binding.body

    @property
    def body_used(self) -> bool:
        return self._binding.bodyUsed

    async def text(self) -> str:
        return await self._binding.text()
