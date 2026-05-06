class D1Database:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> D1Database:
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

    def prepare(self, query: str) -> Any:
        return self._binding.prepare(query)

    async def exec(self, query: str) -> Any:
        return await self._binding.exec(query)

    async def batch(self, statements: list[Any]) -> list[Any]:
        return await self._binding.batch(to_js(statements))

    async def dump(self) -> Any:
        return await self._binding.dump()
