class CryptoHelper:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> CryptoHelper:
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

    @property
    def raw(self) -> JsBuffer:
        return self._binding.raw

    async def digest(self, data: JsBuffer) -> JsBuffer:
        return await self._binding.digest(to_js(data))

    def encode(self, input: str) -> JsBuffer:
        return self._binding.encode(input)
