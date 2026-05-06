class Counter:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Counter:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    def increment(self) -> None:
        self._binding.increment()
