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

    async def metrics(self) -> QueueMetrics:
        return _auto_to_py(await self._binding.metrics())

    async def send(self, message: Any, options: QueueSendOptions | None = None) -> QueueSendResponse:
        return _auto_to_py(await self._binding.send(to_js(_none_to_jsnull(message)), to_js(options)))

    async def send_batch(self, messages: Any, options: QueueSendBatchOptions | None = None) -> QueueSendBatchResponse:
        return _auto_to_py(await self._binding.sendBatch(to_js(messages), to_js(options)))


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

    @property
    def messages(self) -> list[Message]:
        return [Message.from_js(e) for e in self._binding.messages]

    @property
    def queue(self) -> str:
        return self._binding.queue

    @property
    def metadata(self) -> MessageBatchMetadata:
        return _auto_to_py(self._binding.metadata)

    def retry_all(self, options: QueueRetryOptions | None = None) -> None:
        self._binding.retryAll(to_js(options))

    def ack_all(self) -> None:
        self._binding.ackAll()


class QueueMetrics(TypedDict):
    backlogCount: int | float
    backlogBytes: int | float
    oldestMessageTimestamp: datetime | None


class QueueSendOptions(TypedDict, total=False):
    contentType: Literal["text", "bytes", "json", "v8"]
    delaySeconds: int | float


class QueueSendResponse(TypedDict):
    metadata: QueueSendMetadata


class MessageSendRequest(TypedDict):
    body: Any
    contentType: Literal["text", "bytes", "json", "v8"] | None
    delaySeconds: int | float | None


class QueueSendBatchOptions(TypedDict, total=False):
    delaySeconds: int | float


class QueueSendBatchResponse(TypedDict):
    metadata: QueueSendBatchMetadata


class QueueRetryOptions(TypedDict, total=False):
    delaySeconds: int | float


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

    @property
    def id(self) -> str:
        return self._binding.id

    @property
    def timestamp(self) -> datetime:
        return _from_js_date(self._binding.timestamp)

    @property
    def body(self) -> Any:
        return _auto_to_py(_jsnull_to_none(self._binding.body))

    @property
    def attempts(self) -> int | float:
        return self._binding.attempts

    def retry(self, options: QueueRetryOptions | None = None) -> None:
        self._binding.retry(to_js(options))

    def ack(self) -> None:
        self._binding.ack()


class MessageBatchMetadata(TypedDict):
    metrics: MessageBatchMetrics


class QueueSendMetadata(TypedDict):
    metrics: QueueSendMetrics


class QueueSendBatchMetadata(TypedDict):
    metrics: QueueSendBatchMetrics


class MessageBatchMetrics(TypedDict):
    backlogCount: int | float
    backlogBytes: int | float
    oldestMessageTimestamp: datetime | None


class QueueSendMetrics(TypedDict):
    backlogCount: int | float
    backlogBytes: int | float
    oldestMessageTimestamp: datetime | None


class QueueSendBatchMetrics(TypedDict):
    backlogCount: int | float
    backlogBytes: int | float
    oldestMessageTimestamp: datetime | None
