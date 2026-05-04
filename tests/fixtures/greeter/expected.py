class Greeter:
    _binding: Any

    def __init__(self, binding: JsProxy) -> None:
        self._binding = binding

    def greet(self, name: str) -> str:
        return self._binding.greet(name)
