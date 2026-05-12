from __future__ import annotations
from prelude import *

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
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._binding == other._binding

    def __hash__(self) -> int:
        return id(self._binding)

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

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._binding == other._binding

    def __hash__(self) -> int:
        return id(self._binding)

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

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._binding == other._binding

    def __hash__(self) -> int:
        return id(self._binding)

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
