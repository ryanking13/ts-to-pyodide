class D1PreparedStatement:
    _binding: Any

    def __init__(self, binding: JsProxy) -> None:
        self._binding = binding

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
