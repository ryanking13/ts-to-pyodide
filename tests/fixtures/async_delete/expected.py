class KV:
    _binding: Any

    def __init__(self, binding: JsProxy) -> None:
        self._binding = binding

    async def delete(self, key: str) -> None:
        await self._binding.delete(key)
