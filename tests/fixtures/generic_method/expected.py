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

    @overload
    async def first(self, col_name: str) -> Any | None: ...
    @overload
    async def first(self) -> Any | None: ...
    async def first(self, *args: Any, **kwargs: Any) -> Any:
        return await self._binding.first(*args, **kwargs)

    async def run(self) -> Any:
        return await self._binding.run()
