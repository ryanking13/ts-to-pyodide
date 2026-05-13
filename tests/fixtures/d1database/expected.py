from __future__ import annotations
from prelude import *

class D1Database:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> D1Database:
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

    def prepare(self, query: str) -> D1PreparedStatement:
        return D1PreparedStatement.from_js(self._js_obj.prepare(query))

    async def batch(self, statements: list[D1PreparedStatement]) -> list[D1Result]:
        return [to_py(e) for e in await self._js_obj.batch(to_js(statements))]

    async def exec(self, query: str) -> D1ExecResult:
        return to_py(await self._js_obj.exec(query))

    def with_session(self, constraint_or_bookmark: str | Literal["first-primary", "first-unconstrained"] | None = None) -> D1DatabaseSession:
        return D1DatabaseSession.from_js(self._js_obj.withSession(to_js(constraint_or_bookmark)))

    async def dump(self) -> JsBuffer:
        return await self._js_obj.dump()


class D1DatabaseSession:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> D1DatabaseSession:
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

    def prepare(self, query: str) -> D1PreparedStatement:
        return D1PreparedStatement.from_js(self._js_obj.prepare(query))

    async def batch(self, statements: list[D1PreparedStatement]) -> list[D1Result]:
        return [to_py(e) for e in await self._js_obj.batch(to_js(statements))]

    def get_bookmark(self) -> str | None:
        return _jsnull_to_none(self._js_obj.getBookmark())


class D1PreparedStatement:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> D1PreparedStatement:
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

    def bind(self, *values: Any) -> D1PreparedStatement:
        return D1PreparedStatement.from_js(self._js_obj.bind(*[_none_to_jsnull(v) for v in values]))

    async def first(self, *args: Any, **kwargs: Any) -> Any:
        return to_py(_jsnull_to_none(await self._js_obj.first(*args, **kwargs)))

    async def run(self) -> D1Result:
        return to_py(await self._js_obj.run())

    async def all(self) -> D1Result:
        return to_py(await self._js_obj.all())

    async def raw(self, *args: Any, **kwargs: Any) -> Any:
        _a = list(args)
        if len(_a) > 0:
            _a[0] = to_js(_a[0])
        return to_py(await self._js_obj.raw(*_a, **kwargs))


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
    timings: D1MetaTimings | None
    total_attempts: int | float | None


class D1Result(TypedDict):
    results: list[Any]


class D1MetaTimings(TypedDict):
    sql_duration_ms: int | float
