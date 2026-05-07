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

class D1Database:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> D1Database:
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

    def prepare(self, query: str) -> D1PreparedStatement:
        return D1PreparedStatement.from_js(self._binding.prepare(query))

    async def batch(self, statements: list[D1PreparedStatement]) -> list[D1Result]:
        return [_from_js_opts(e) for e in await self._binding.batch(to_js(statements))]

    async def exec(self, query: str) -> D1ExecResult:
        return _from_js_opts(await self._binding.exec(query))

    def with_session(self, constraint_or_bookmark: str | Literal["first-primary", "first-unconstrained"] | None = None) -> D1DatabaseSession:
        return D1DatabaseSession.from_js(self._binding.withSession(to_js(constraint_or_bookmark) if constraint_or_bookmark is not None else None))

    async def dump(self) -> JsBuffer:
        return await self._binding.dump()


class D1DatabaseSession:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> D1DatabaseSession:
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

    def prepare(self, query: str) -> D1PreparedStatement:
        return D1PreparedStatement.from_js(self._binding.prepare(query))

    async def batch(self, statements: list[D1PreparedStatement]) -> list[D1Result]:
        return [_from_js_opts(e) for e in await self._binding.batch(to_js(statements))]

    def get_bookmark(self) -> str | None:
        return _jsnull_to_none(self._binding.getBookmark())


class D1PreparedStatement:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> D1PreparedStatement:
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

    def bind(self, *values: Any) -> D1PreparedStatement:
        return D1PreparedStatement.from_js(self._binding.bind(*[_none_to_jsnull(v) for v in values]))

    async def first(self, *args: Any, **kwargs: Any) -> Any:
        return _auto_to_py(_jsnull_to_none(await self._binding.first(*args, **kwargs)))

    async def run(self) -> D1Result:
        return _from_js_opts(await self._binding.run())

    async def all(self) -> D1Result:
        return _from_js_opts(await self._binding.all())

    async def raw(self, *args: Any, **kwargs: Any) -> Any:
        _a = list(args)
        if len(_a) > 0 and isinstance(_a[0], dict):
            _a[0] = _to_js_opts(_a[0])
        return _auto_to_py(await self._binding.raw(*_a, **kwargs))


class D1ExecResult(TypedDict):
    count: int | float
    duration: int | float


class D1Response(TypedDict):
    success: Literal[True]
    meta: Any
    error: Never | None


class D1Meta(TypedDict):
    duration: int | float
    size_after: int | float
    rows_read: int | float
    rows_written: int | float
    last_row_id: int | float
    changed_db: bool
    changes: int | float
    served_by_region: str | None
    served_by_colo: str | None
    served_by_primary: bool | None
    timings: Any | None
    total_attempts: int | float | None
    sql_duration_ms: int | float


class D1Result(TypedDict):
    results: list[Any]
