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

class Queue:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Queue:
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

    async def metrics(self) -> QueueMetrics:
        return _from_js_opts(await self._binding.metrics())

    async def send(self, message: Any, options: QueueSendOptions | None = None) -> QueueSendResponse:
        return _from_js_opts(await self._binding.send(to_js(message), _to_js_opts(options)))

    async def send_batch(self, messages: Any, options: QueueSendBatchOptions | None = None) -> QueueSendBatchResponse:
        return _from_js_opts(await self._binding.sendBatch(to_js(messages), _to_js_opts(options)))


class MessageBatch:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> MessageBatch:
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

    @property
    def messages(self) -> list[Message]:
        return self._binding.messages

    @property
    def queue(self) -> str:
        return self._binding.queue

    @property
    def metadata(self) -> MessageBatchMetadata:
        return _from_js_opts(self._binding.metadata)

    def retry_all(self, options: QueueRetryOptions | None = None) -> None:
        self._binding.retryAll(_to_js_opts(options))

    def ack_all(self) -> None:
        self._binding.ackAll()


class QueueMetrics(TypedDict):
    backlog_count: int | float
    backlog_bytes: int | float
    oldest_message_timestamp: datetime | None


class QueueSendOptions(TypedDict, total=False):
    content_type: Literal["text", "bytes", "json", "v8"]
    delay_seconds: int | float


class QueueSendResponse(TypedDict):
    metadata: QueueSendMetadata


class MessageSendRequest(TypedDict):
    body: Any
    content_type: Literal["text", "bytes", "json", "v8"] | None
    delay_seconds: int | float | None


class QueueSendBatchOptions(TypedDict, total=False):
    delay_seconds: int | float


class QueueSendBatchResponse(TypedDict):
    metadata: QueueSendBatchMetadata


class QueueRetryOptions(TypedDict, total=False):
    delay_seconds: int | float


class Message:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Message:
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

    @property
    def id(self) -> str:
        return self._binding.id

    @property
    def timestamp(self) -> datetime:
        return _from_js_date(self._binding.timestamp)

    @property
    def body(self) -> Any:
        return self._binding.body

    @property
    def attempts(self) -> int | float:
        return self._binding.attempts

    def retry(self, options: QueueRetryOptions | None = None) -> None:
        self._binding.retry(_to_js_opts(options))

    def ack(self) -> None:
        self._binding.ack()


class MessageBatchMetadata(TypedDict):
    metrics: MessageBatchMetrics


class QueueSendMetadata(TypedDict):
    metrics: QueueSendMetrics


class QueueSendBatchMetadata(TypedDict):
    metrics: QueueSendBatchMetrics


class MessageBatchMetrics(TypedDict):
    backlog_count: int | float
    backlog_bytes: int | float
    oldest_message_timestamp: datetime | None


class QueueSendMetrics(TypedDict):
    backlog_count: int | float
    backlog_bytes: int | float
    oldest_message_timestamp: datetime | None


class QueueSendBatchMetrics(TypedDict):
    backlog_count: int | float
    backlog_bytes: int | float
    oldest_message_timestamp: datetime | None
