class Hyperdrive:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Hyperdrive:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def host(self) -> str:
        return self._binding.host

    @property
    def port(self) -> int | float:
        return self._binding.port
