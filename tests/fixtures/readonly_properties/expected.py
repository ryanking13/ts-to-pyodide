class Hyperdrive:
    _binding: Any

    def __init__(self, binding: JsProxy) -> None:
        self._binding = binding

    @property
    def host(self) -> str:
        return self._binding.host

    @property
    def port(self) -> int | float:
        return self._binding.port
