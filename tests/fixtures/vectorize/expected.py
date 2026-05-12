from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal, Never, TypedDict, overload
import js
from pyodide.ffi import JsBuffer, JsProxy, create_proxy, to_js as _raw_to_js

def to_js(obj: Any, **kwargs: Any) -> Any:
    if "dict_converter" not in kwargs:
        kwargs["dict_converter"] = js.Object.fromEntries
    return _raw_to_js(obj, **kwargs)

def _jsnull_to_none(value: Any) -> Any:
    try:
        from pyodide.ffi import jsnull
    except ImportError:
        return value
    if value is jsnull:
        return None
    return value

def _auto_to_py(value: Any) -> Any:
    if isinstance(value, JsProxy):
        try:
            value = value.to_py()
        except Exception:
            return value
    if isinstance(value, dict):
        return {k: _auto_to_py(_jsnull_to_none(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [_auto_to_py(_jsnull_to_none(v)) for v in value]
    return value

def _none_to_jsnull(value: Any) -> Any:
    if value is None:
        try:
            from pyodide.ffi import jsnull
            return jsnull
        except ImportError:
            return value
    return value

def _to_js_headers(headers: dict[str, str] | list[tuple[str, str]] | JsProxy) -> JsProxy:
    if isinstance(headers, dict):
        return js.Headers.new(list(headers.items()))
    elif isinstance(headers, list):
        return js.Headers.new(headers)
    return headers

def _to_js_date(dt: datetime | JsProxy) -> JsProxy:
    if isinstance(dt, JsProxy):
        return dt
    return js.Date.new(int(dt.timestamp() * 1000))

def _from_js_date(js_date: Any) -> datetime:
    return datetime.fromtimestamp(js_date.getTime() / 1000, tz=timezone.utc)

class Vectorize:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Vectorize:
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

    async def describe(self) -> VectorizeIndexInfo:
        return _auto_to_py(await self._binding.describe())

    async def query(self, vector: Any | list[int | float], options: VectorizeQueryOptions | None = None) -> VectorizeMatches:
        return _auto_to_py(await self._binding.query(to_js(vector), to_js(options)))

    async def query_by_id(self, vector_id: str, options: VectorizeQueryOptions | None = None) -> VectorizeMatches:
        return _auto_to_py(await self._binding.queryById(vector_id, to_js(options)))

    async def insert(self, vectors: list[VectorizeVector]) -> VectorizeAsyncMutation:
        return _auto_to_py(await self._binding.insert(to_js(vectors)))

    async def upsert(self, vectors: list[VectorizeVector]) -> VectorizeAsyncMutation:
        return _auto_to_py(await self._binding.upsert(to_js(vectors)))

    async def delete_by_ids(self, ids: list[str]) -> VectorizeAsyncMutation:
        return _auto_to_py(await self._binding.deleteByIds(to_js(ids)))

    async def get_by_ids(self, ids: list[str]) -> list[VectorizeVector]:
        return [_auto_to_py(e) for e in await self._binding.getByIds(to_js(ids))]


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
