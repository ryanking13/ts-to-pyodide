class Binding:
    _binding: Any

    def __init__(self, binding: JsProxy) -> None:
        self._binding = binding

    @property
    def videos(self) -> Any:
        return self._binding.videos
    
    @videos.setter
    def videos(self, value: Any) -> None:
        self._binding.videos = value

    @property
    def name(self) -> str:
        return self._binding.name

    async def fetch(self, url: str) -> Any:
        return await self._binding.fetch(url)
