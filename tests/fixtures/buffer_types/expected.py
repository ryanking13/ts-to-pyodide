class CryptoHelper:
    _binding: Any

    def __init__(self, binding: JsProxy) -> None:
        self._binding = binding

    @property
    def raw(self) -> JsBuffer:
        return self._binding.raw

    async def digest(self, data: JsBuffer) -> JsBuffer:
        return await self._binding.digest(to_js(data))

    def encode(self, input: str) -> JsBuffer:
        return self._binding.encode(input)
