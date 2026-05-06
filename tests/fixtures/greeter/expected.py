class Greeter:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Greeter:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    def greet(self, name: str) -> str:
        return self._binding.greet(name)
