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

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._binding == other._binding

    def __hash__(self) -> int:
        return id(self._binding)

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
