from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal, Never, TypedDict, overload
import js
from pyodide.ffi import JsBuffer, JsProxy, create_proxy, to_js

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

def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])

def _to_snake(s: str) -> str:
    import re
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()

def _to_js_opts(opts: Any) -> Any:
    if opts is None:
        return None
    def _convert(v: Any) -> Any:
        if isinstance(v, dict):
            return {_to_camel(k): _convert(val) for k, val in v.items() if val is not None}
        if isinstance(v, list):
            return [_convert(item) for item in v]
        return v
    return to_js(_convert(opts))

def _from_js_opts(js_obj: Any) -> Any:
    if js_obj is None:
        return None
    def _convert(v: Any) -> Any:
        v = _jsnull_to_none(v)
        if v is None:
            return None
        if isinstance(v, dict):
            return {_to_snake(k): _convert(val) for k, val in v.items()}
        if isinstance(v, list):
            return [_convert(item) for item in v]
        return v
    return _convert(js_obj.to_py())

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
        return getattr(self, _to_snake(key))

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, _to_snake(key), value)

    async def describe(self) -> VectorizeIndexInfo:
        return _from_js_opts(await self._binding.describe())

    async def query(self, vector: Any | list[int | float], options: VectorizeQueryOptions | None = None) -> VectorizeMatches:
        return _from_js_opts(await self._binding.query(to_js(vector), _to_js_opts(options)))

    async def query_by_id(self, vector_id: str, options: VectorizeQueryOptions | None = None) -> VectorizeMatches:
        return _from_js_opts(await self._binding.queryById(vector_id, _to_js_opts(options)))

    async def insert(self, vectors: list[VectorizeVector]) -> VectorizeAsyncMutation:
        return _from_js_opts(await self._binding.insert(_to_js_opts(vectors)))

    async def upsert(self, vectors: list[VectorizeVector]) -> VectorizeAsyncMutation:
        return _from_js_opts(await self._binding.upsert(_to_js_opts(vectors)))

    async def delete_by_ids(self, ids: list[str]) -> VectorizeAsyncMutation:
        return _from_js_opts(await self._binding.deleteByIds(to_js(ids)))

    async def get_by_ids(self, ids: list[str]) -> list[VectorizeVector]:
        return [_from_js_opts(e) for e in await self._binding.getByIds(to_js(ids))]


class VectorizeIndexInfo(TypedDict):
    vector_count: int | float
    dimensions: int | float
    processed_up_to_datetime: int | float
    processed_up_to_mutation: int | float


class VectorizeQueryOptions(TypedDict, total=False):
    top_k: int | float
    namespace: str
    return_values: bool
    return_metadata: bool | Literal["all", "indexed", "none"] | None
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
    mutation_id: str


class VectorizeMatch(TypedDict):
    id: str
    values: Any | list[int | float] | None
    namespace: str | None
    metadata: dict[str, Any] | None
    score: int | float
