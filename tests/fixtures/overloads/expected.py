class D1PreparedStatement:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> D1PreparedStatement:
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

    @overload
    async def first(self, col_name: str) -> Any | None: ...
    @overload
    async def first(self) -> Any | None: ...
    async def first(self, *args: Any, **kwargs: Any) -> Any:
        return _jsnull_to_none(await self._binding.first(*args, **kwargs))
