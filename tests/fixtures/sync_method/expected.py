class Counter:
    _binding: Any

    def __init__(self, binding: JsProxy) -> None:
        self._binding = binding

    def increment(self) -> None:
        self._binding.increment()
