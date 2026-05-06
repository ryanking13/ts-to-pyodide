class KVStore:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> KVStore:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    async def put(self, key: str, value: str, *, expiration: int | float | None = None, expiration_ttl: int | float | None = None, metadata: Any | None = None) -> None:
        _opts: dict[str, Any] = {}
        if expiration is not None:
            _opts["expiration"] = expiration
        if expiration_ttl is not None:
            _opts["expirationTtl"] = expiration_ttl
        if metadata is not None:
            _opts["metadata"] = metadata
        await self._binding.put(key, value, to_js(_opts) if _opts else None)

    async def get(self, key: str) -> str | None:
        return _jsnull_to_none(await self._binding.get(key))
