class D1Database:
    _binding: Any

    def __init__(self, binding: JsProxy) -> None:
        self._binding = binding

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    def prepare(self, query: str) -> Any:
        return self._binding.prepare(query)

    async def exec(self, query: str) -> Any:
        return await self._binding.exec(query)

    async def batch(self, statements: list[Any]) -> list[Any]:
        return await self._binding.batch(to_js(statements))

    async def dump(self) -> Any:
        return await self._binding.dump()
