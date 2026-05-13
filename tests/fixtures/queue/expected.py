from __future__ import annotations
from prelude import *

class Queue:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Queue:
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

    async def metrics(self) -> QueueMetrics:
        return to_py(await self._js_obj.metrics())

    async def send(self, message: Any, options: QueueSendOptions | None = None) -> QueueSendResponse:
        return to_py(await self._js_obj.send(to_js(_none_to_jsnull(message)), to_js(options)))

    async def send_batch(self, messages: Any, options: QueueSendBatchOptions | None = None) -> QueueSendBatchResponse:
        return to_py(await self._js_obj.sendBatch(to_js(messages), to_js(options)))


class MessageBatch:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> MessageBatch:
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

    @property
    def messages(self) -> list[Message]:
        return [Message.from_js(e) for e in self._js_obj.messages]

    @property
    def queue(self) -> str:
        return self._js_obj.queue

    @property
    def metadata(self) -> MessageBatchMetadata:
        return to_py(self._js_obj.metadata)

    def retry_all(self, options: QueueRetryOptions | None = None) -> None:
        self._js_obj.retryAll(to_js(options))

    def ack_all(self) -> None:
        self._js_obj.ackAll()


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
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Message:
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

    @property
    def id(self) -> str:
        return self._js_obj.id

    @property
    def timestamp(self) -> datetime:
        return _from_js_date(self._js_obj.timestamp)

    @property
    def body(self) -> Any:
        return to_py(_jsnull_to_none(self._js_obj.body))

    @property
    def attempts(self) -> int | float:
        return self._js_obj.attempts

    def retry(self, options: QueueRetryOptions | None = None) -> None:
        self._js_obj.retry(to_js(options))

    def ack(self) -> None:
        self._js_obj.ack()


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
