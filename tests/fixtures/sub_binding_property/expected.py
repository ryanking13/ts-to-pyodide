class Binding:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Binding:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

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
