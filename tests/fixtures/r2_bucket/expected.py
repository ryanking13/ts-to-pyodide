from __future__ import annotations
from typing import Any, TypedDict, overload
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

def _build_opts(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}

def _to_js_headers(headers: dict[str, str] | list[tuple[str, str]] | JsProxy) -> JsProxy:
    if isinstance(headers, dict):
        return js.Headers.new(list(headers.items()))
    elif isinstance(headers, list):
        return js.Headers.new(headers)
    return headers

class R2Object:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2Object:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def key(self) -> str:
        return self._binding.key

    @property
    def version(self) -> str:
        return self._binding.version

    @property
    def size(self) -> int | float:
        return self._binding.size

    @property
    def etag(self) -> str:
        return self._binding.etag

    @property
    def http_etag(self) -> str:
        return self._binding.httpEtag

    @property
    def checksums(self) -> R2Checksums:
        return R2Checksums.from_js(self._binding.checksums)

    @property
    def uploaded(self) -> Any:
        return self._binding.uploaded

    @property
    def http_metadata(self) -> R2HTTPMetadata | None:
        _v = self._binding.httpMetadata
        return _v.to_py() if _v is not None else None

    @property
    def custom_metadata(self) -> dict[str, str] | None:
        _v = self._binding.customMetadata
        return _v.to_py() if _v is not None else None

    @property
    def storage_class(self) -> str:
        return self._binding.storageClass

    def write_http_metadata(self, headers: dict[str, str] | list[tuple[str, str]] | JsProxy) -> None:
        self._binding.writeHttpMetadata(_to_js_headers(headers))

    def __len__(self) -> int:
        return self._binding.__len__()


class R2Bucket:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2Bucket:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    async def head(self, key: str) -> R2Object | None:
        _v = await self._binding.head(key)
        return R2Object.from_js(_v) if _v is not None else None

    async def get(self, key: str, *, only_if: R2Conditional | dict[str, str] | list[tuple[str, str]] | JsProxy | None = None, range: dict[str, str] | list[tuple[str, str]] | JsProxy | None = None, ssec_key: JsBuffer | str | None = None) -> R2ObjectBody | None:
        _opts = _build_opts(onlyIf=only_if, range=_to_js_headers(range) if range is not None else None, ssecKey=ssec_key)
        _v = await self._binding.get(key, to_js(_opts) if _opts else None)
        return R2ObjectBody.from_js(_v) if _v is not None else None

    async def put(self, key: str, value: Any | JsBuffer | str | Any | None, *, only_if: R2Conditional | dict[str, str] | list[tuple[str, str]] | JsProxy | None = None, http_metadata: R2HTTPMetadata | dict[str, str] | list[tuple[str, str]] | JsProxy | None = None, custom_metadata: dict[str, str] | None = None, md5: JsBuffer | str | None = None, sha256: JsBuffer | str | None = None, storage_class: str | None = None, ssec_key: JsBuffer | str | None = None) -> R2Object:
        _opts = _build_opts(onlyIf=only_if, httpMetadata=http_metadata, customMetadata=custom_metadata, md5=md5, sha256=sha256, storageClass=storage_class, ssecKey=ssec_key)
        return R2Object.from_js(await self._binding.put(key, to_js(value), to_js(_opts) if _opts else None))

    async def create_multipart_upload(self, key: str, *, http_metadata: R2HTTPMetadata | dict[str, str] | list[tuple[str, str]] | JsProxy | None = None, custom_metadata: dict[str, str] | None = None, storage_class: str | None = None) -> R2MultipartUpload:
        _opts = _build_opts(httpMetadata=http_metadata, customMetadata=custom_metadata, storageClass=storage_class)
        return R2MultipartUpload.from_js(await self._binding.createMultipartUpload(key, to_js(_opts) if _opts else None))

    def resume_multipart_upload(self, key: str, upload_id: str) -> R2MultipartUpload:
        return R2MultipartUpload.from_js(self._binding.resumeMultipartUpload(key, upload_id))

    async def delete(self, keys: str | list[str]) -> None:
        await self._binding.delete(to_js(keys))

    async def list(self, *, limit: int | float | None = None, prefix: str | None = None, cursor: str | None = None, delimiter: str | None = None, start_after: str | None = None) -> Any:
        _opts = _build_opts(limit=limit, prefix=prefix, cursor=cursor, delimiter=delimiter, startAfter=start_after)
        return await self._binding.list(to_js(_opts) if _opts else None)

    async def __getitem__(self, key: str, *, only_if: R2Conditional | dict[str, str] | list[tuple[str, str]] | JsProxy | None = None, range: dict[str, str] | list[tuple[str, str]] | JsProxy | None = None, ssec_key: JsBuffer | str | None = None) -> R2ObjectBody | None:
        _opts = _build_opts(onlyIf=only_if, range=_to_js_headers(range) if range is not None else None, ssecKey=ssec_key)
        _v = await self._binding.__getitem__(key, to_js(_opts) if _opts else None)
        return R2ObjectBody.from_js(_v) if _v is not None else None

    async def __delitem__(self, keys: str | list[str]) -> None:
        await self._binding.__delitem__(to_js(keys))


class R2Checksums:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2Checksums:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def md5(self) -> JsBuffer | None:
        return _jsnull_to_none(self._binding.md5)

    @property
    def sha1(self) -> JsBuffer | None:
        return _jsnull_to_none(self._binding.sha1)

    @property
    def sha256(self) -> JsBuffer | None:
        return _jsnull_to_none(self._binding.sha256)

    def to_json(self) -> R2StringChecksums:
        return (self._binding.toJSON()).to_py()


class R2HTTPMetadata(TypedDict, total=False):
    contentType: str
    contentLanguage: str
    contentDisposition: str
    contentEncoding: str
    cacheControl: str


class R2GetOptions(TypedDict, total=False):
    onlyIf: R2Conditional | dict[str, str] | list[tuple[str, str]] | JsProxy | None
    range: dict[str, str] | list[tuple[str, str]] | JsProxy
    ssecKey: JsBuffer | str | None


class R2ObjectBody:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2ObjectBody:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def body(self) -> Any:
        return self._binding.body

    @property
    def body_used(self) -> bool:
        return self._binding.bodyUsed

    async def array_buffer(self) -> JsBuffer:
        return await self._binding.arrayBuffer()

    async def text(self) -> str:
        return await self._binding.text()

    async def json(self) -> Any:
        return await self._binding.json()

    async def blob(self) -> Any:
        return await self._binding.blob()


class R2Conditional(TypedDict, total=False):
    etagMatches: str
    etagDoesNotMatch: str
    uploadedBefore: Any
    uploadedAfter: Any
    secondsGranularity: bool


class R2PutOptions(TypedDict, total=False):
    onlyIf: R2Conditional | dict[str, str] | list[tuple[str, str]] | JsProxy | None
    httpMetadata: R2HTTPMetadata | dict[str, str] | list[tuple[str, str]] | JsProxy | None
    customMetadata: dict[str, str]
    md5: JsBuffer | str | None
    sha256: JsBuffer | str | None
    storageClass: str
    ssecKey: JsBuffer | str | None


class R2MultipartOptions(TypedDict, total=False):
    httpMetadata: R2HTTPMetadata | dict[str, str] | list[tuple[str, str]] | JsProxy | None
    customMetadata: dict[str, str]
    storageClass: str


class R2MultipartUpload:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2MultipartUpload:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def key(self) -> str:
        return self._binding.key

    @property
    def upload_id(self) -> str:
        return self._binding.uploadId

    async def upload_part(self, part_number: int | float, value: Any | JsBuffer | str | Any) -> R2UploadedPart:
        return R2UploadedPart.from_js(await self._binding.uploadPart(part_number, to_js(value)))

    async def abort(self) -> None:
        await self._binding.abort()

    async def complete(self, uploaded_parts: list[R2UploadedPart]) -> R2Object:
        return R2Object.from_js(await self._binding.complete(to_js(uploaded_parts)))


class R2ListOptions(TypedDict, total=False):
    limit: int | float
    prefix: str
    cursor: str
    delimiter: str
    startAfter: str


class R2StringChecksums(TypedDict, total=False):
    md5: str
    sha1: str
    sha256: str


class R2UploadedPart:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2UploadedPart:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def part_number(self) -> int | float:
        return self._binding.partNumber
    
    @part_number.setter
    def part_number(self, value: int | float) -> None:
        self._binding.partNumber = value

    @property
    def etag(self) -> str:
        return self._binding.etag
    
    @etag.setter
    def etag(self, value: str) -> None:
        self._binding.etag = value
