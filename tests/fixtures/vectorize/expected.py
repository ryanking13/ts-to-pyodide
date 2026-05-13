from __future__ import annotations
from prelude import *

class Vectorize:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Vectorize:
        instance = object.__new__(cls)
        instance._js_obj = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._js_obj

    def __getattr__(self, name: str) -> Any:
        return getattr(self._js_obj, name)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._js_obj == other._js_obj

    def __hash__(self) -> int:
        return id(self._js_obj)

    async def describe(self) -> VectorizeIndexInfo:
        return to_py(await self._js_obj.describe())

    async def query(self, vector: Any | list[int | float], options: VectorizeQueryOptions | None = None) -> VectorizeMatches:
        return to_py(await self._js_obj.query(to_js(vector), to_js(options)))

    async def query_by_id(self, vector_id: str, options: VectorizeQueryOptions | None = None) -> VectorizeMatches:
        return to_py(await self._js_obj.queryById(vector_id, to_js(options)))

    async def insert(self, vectors: list[VectorizeVector]) -> VectorizeAsyncMutation:
        return to_py(await self._js_obj.insert(to_js(vectors)))

    async def upsert(self, vectors: list[VectorizeVector]) -> VectorizeAsyncMutation:
        return to_py(await self._js_obj.upsert(to_js(vectors)))

    async def delete_by_ids(self, ids: list[str]) -> VectorizeAsyncMutation:
        return to_py(await self._js_obj.deleteByIds(to_js(ids)))

    async def get_by_ids(self, ids: list[str]) -> list[VectorizeVector]:
        return [to_py(e) for e in await self._js_obj.getByIds(to_js(ids))]


class VectorizeIndexInfo(TypedDict):
    vectorCount: int | float
    dimensions: int | float
    processedUpToDatetime: int | float
    processedUpToMutation: int | float


class VectorizeQueryOptions(TypedDict, total=False):
    topK: int | float
    namespace: str
    returnValues: bool
    returnMetadata: bool | Literal["all", "indexed", "none"] | None
    filter: dict[str, Any]


class VectorizeMatches(TypedDict):
    matches: list[VectorizeMatch]
    count: int | float


class VectorizeVector(TypedDict):
    id: str
    values: Any | list[int | float]
    namespace: str | None
    metadata: dict[str, Any] | None


class VectorizeAsyncMutation(TypedDict):
    mutationId: str


class VectorizeMatch(TypedDict):
    id: str
    values: Any | list[int | float] | None
    namespace: str | None
    metadata: dict[str, Any] | None
    score: int | float
