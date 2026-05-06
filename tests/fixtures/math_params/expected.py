class Calculator:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Calculator:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    def add(self, a: int | float, b: int | float) -> int | float:
        return self._binding.add(a, b)
