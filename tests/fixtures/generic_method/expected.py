class Stmt:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Stmt:
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

    async def first(self, *args: Any, **kwargs: Any) -> Any:
        return _jsnull_to_none(await self._binding.first(*args, **kwargs))

    async def run(self) -> Any:
        return await self._binding.run()
