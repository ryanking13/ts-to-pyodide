class Calculator:
    _binding: Any

    def __init__(self, binding: JsProxy) -> None:
        self._binding = binding

    def add(self, a: int | float, b: int | float) -> int | float:
        return self._binding.add(a, b)
