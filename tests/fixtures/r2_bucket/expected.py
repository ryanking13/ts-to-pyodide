from __future__ import annotations
from typing import Any, overload
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
        return R2HTTPMetadata.from_js(_v) if _v is not None else None

    @property
    def custom_metadata(self) -> dict[str, str] | None:
        _v = self._binding.customMetadata
        return _v.to_py() if _v is not None else None

    @property
    def storage_class(self) -> str:
        return self._binding.storageClass

    def write_http_metadata(self, headers: Any) -> None:
        self._binding.writeHttpMetadata(to_js(headers))

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

    async def get(self, key: str, *, only_if: R2Conditional | Any | None = None, range: Any | None = None, ssec_key: JsBuffer | str | None = None) -> R2ObjectBody | None:
        _opts = _build_opts(onlyIf=only_if, range=range, ssecKey=ssec_key)
        _v = await self._binding.get(key, to_js(_opts) if _opts else None)
        return R2ObjectBody.from_js(_v) if _v is not None else None

    async def put(self, key: str, value: Any | JsBuffer | str | Any | None, *, only_if: R2Conditional | Any | None = None, http_metadata: R2HTTPMetadata | Any | None = None, custom_metadata: dict[str, str] | None = None, md5: JsBuffer | str | None = None, sha256: JsBuffer | str | None = None, storage_class: str | None = None, ssec_key: JsBuffer | str | None = None) -> R2Object:
        _opts = _build_opts(onlyIf=only_if, httpMetadata=http_metadata, customMetadata=custom_metadata, md5=md5, sha256=sha256, storageClass=storage_class, ssecKey=ssec_key)
        return R2Object.from_js(await self._binding.put(key, to_js(value), to_js(_opts) if _opts else None))

    async def create_multipart_upload(self, key: str, *, http_metadata: R2HTTPMetadata | Any | None = None, custom_metadata: dict[str, str] | None = None, storage_class: str | None = None) -> R2MultipartUpload:
        _opts = _build_opts(httpMetadata=http_metadata, customMetadata=custom_metadata, storageClass=storage_class)
        return R2MultipartUpload.from_js(await self._binding.createMultipartUpload(key, to_js(_opts) if _opts else None))

    def resume_multipart_upload(self, key: str, upload_id: str) -> R2MultipartUpload:
        return R2MultipartUpload.from_js(self._binding.resumeMultipartUpload(key, upload_id))

    async def delete(self, keys: str | list[str]) -> None:
        await self._binding.delete(to_js(keys))

    async def list(self, *, limit: int | float | None = None, prefix: str | None = None, cursor: str | None = None, delimiter: str | None = None, start_after: str | None = None) -> Any:
        _opts = _build_opts(limit=limit, prefix=prefix, cursor=cursor, delimiter=delimiter, startAfter=start_after)
        return await self._binding.list(to_js(_opts) if _opts else None)

    async def __getitem__(self, key: str, *, only_if: R2Conditional | Any | None = None, range: Any | None = None, ssec_key: JsBuffer | str | None = None) -> R2ObjectBody | None:
        _opts = _build_opts(onlyIf=only_if, range=range, ssecKey=ssec_key)
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
        return R2StringChecksums.from_js(self._binding.toJSON())


class R2HTTPMetadata:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2HTTPMetadata:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def content_type(self) -> str | None:
        return _jsnull_to_none(self._binding.contentType)
    
    @content_type.setter
    def content_type(self, value: str | None) -> None:
        self._binding.contentType = value

    @property
    def content_language(self) -> str | None:
        return _jsnull_to_none(self._binding.contentLanguage)
    
    @content_language.setter
    def content_language(self, value: str | None) -> None:
        self._binding.contentLanguage = value

    @property
    def content_disposition(self) -> str | None:
        return _jsnull_to_none(self._binding.contentDisposition)
    
    @content_disposition.setter
    def content_disposition(self, value: str | None) -> None:
        self._binding.contentDisposition = value

    @property
    def content_encoding(self) -> str | None:
        return _jsnull_to_none(self._binding.contentEncoding)
    
    @content_encoding.setter
    def content_encoding(self, value: str | None) -> None:
        self._binding.contentEncoding = value

    @property
    def cache_control(self) -> str | None:
        return _jsnull_to_none(self._binding.cacheControl)
    
    @cache_control.setter
    def cache_control(self, value: str | None) -> None:
        self._binding.cacheControl = value


class R2GetOptions:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2GetOptions:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def only_if(self) -> R2Conditional | Any | None:
        return _jsnull_to_none(self._binding.onlyIf)
    
    @only_if.setter
    def only_if(self, value: R2Conditional | Any | None) -> None:
        self._binding.onlyIf = value

    @property
    def range(self) -> Any | None:
        return _jsnull_to_none(self._binding.range)
    
    @range.setter
    def range(self, value: Any | None) -> None:
        self._binding.range = value

    @property
    def ssec_key(self) -> JsBuffer | str | None:
        return _jsnull_to_none(self._binding.ssecKey)
    
    @ssec_key.setter
    def ssec_key(self, value: JsBuffer | str | None) -> None:
        self._binding.ssecKey = value


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


class R2Conditional:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2Conditional:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def etag_matches(self) -> str | None:
        return _jsnull_to_none(self._binding.etagMatches)
    
    @etag_matches.setter
    def etag_matches(self, value: str | None) -> None:
        self._binding.etagMatches = value

    @property
    def etag_does_not_match(self) -> str | None:
        return _jsnull_to_none(self._binding.etagDoesNotMatch)
    
    @etag_does_not_match.setter
    def etag_does_not_match(self, value: str | None) -> None:
        self._binding.etagDoesNotMatch = value

    @property
    def uploaded_before(self) -> Any | None:
        return _jsnull_to_none(self._binding.uploadedBefore)
    
    @uploaded_before.setter
    def uploaded_before(self, value: Any | None) -> None:
        self._binding.uploadedBefore = value

    @property
    def uploaded_after(self) -> Any | None:
        return _jsnull_to_none(self._binding.uploadedAfter)
    
    @uploaded_after.setter
    def uploaded_after(self, value: Any | None) -> None:
        self._binding.uploadedAfter = value

    @property
    def seconds_granularity(self) -> bool | None:
        return _jsnull_to_none(self._binding.secondsGranularity)
    
    @seconds_granularity.setter
    def seconds_granularity(self, value: bool | None) -> None:
        self._binding.secondsGranularity = value


class R2PutOptions:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2PutOptions:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def only_if(self) -> R2Conditional | Any | None:
        return _jsnull_to_none(self._binding.onlyIf)
    
    @only_if.setter
    def only_if(self, value: R2Conditional | Any | None) -> None:
        self._binding.onlyIf = value

    @property
    def http_metadata(self) -> R2HTTPMetadata | Any | None:
        return _jsnull_to_none(self._binding.httpMetadata)
    
    @http_metadata.setter
    def http_metadata(self, value: R2HTTPMetadata | Any | None) -> None:
        self._binding.httpMetadata = value

    @property
    def custom_metadata(self) -> dict[str, str] | None:
        _v = self._binding.customMetadata
        return _v.to_py() if _v is not None else None
    
    @custom_metadata.setter
    def custom_metadata(self, value: dict[str, str] | None) -> None:
        self._binding.customMetadata = value

    @property
    def md5(self) -> JsBuffer | str | None:
        return _jsnull_to_none(self._binding.md5)
    
    @md5.setter
    def md5(self, value: JsBuffer | str | None) -> None:
        self._binding.md5 = value

    @property
    def sha256(self) -> JsBuffer | str | None:
        return _jsnull_to_none(self._binding.sha256)
    
    @sha256.setter
    def sha256(self, value: JsBuffer | str | None) -> None:
        self._binding.sha256 = value

    @property
    def storage_class(self) -> str | None:
        return _jsnull_to_none(self._binding.storageClass)
    
    @storage_class.setter
    def storage_class(self, value: str | None) -> None:
        self._binding.storageClass = value

    @property
    def ssec_key(self) -> JsBuffer | str | None:
        return _jsnull_to_none(self._binding.ssecKey)
    
    @ssec_key.setter
    def ssec_key(self, value: JsBuffer | str | None) -> None:
        self._binding.ssecKey = value


class R2MultipartOptions:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2MultipartOptions:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def http_metadata(self) -> R2HTTPMetadata | Any | None:
        return _jsnull_to_none(self._binding.httpMetadata)
    
    @http_metadata.setter
    def http_metadata(self, value: R2HTTPMetadata | Any | None) -> None:
        self._binding.httpMetadata = value

    @property
    def custom_metadata(self) -> dict[str, str] | None:
        _v = self._binding.customMetadata
        return _v.to_py() if _v is not None else None
    
    @custom_metadata.setter
    def custom_metadata(self, value: dict[str, str] | None) -> None:
        self._binding.customMetadata = value

    @property
    def storage_class(self) -> str | None:
        return _jsnull_to_none(self._binding.storageClass)
    
    @storage_class.setter
    def storage_class(self, value: str | None) -> None:
        self._binding.storageClass = value


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


class R2ListOptions:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2ListOptions:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def limit(self) -> int | float | None:
        return _jsnull_to_none(self._binding.limit)
    
    @limit.setter
    def limit(self, value: int | float | None) -> None:
        self._binding.limit = value

    @property
    def prefix(self) -> str | None:
        return _jsnull_to_none(self._binding.prefix)
    
    @prefix.setter
    def prefix(self, value: str | None) -> None:
        self._binding.prefix = value

    @property
    def cursor(self) -> str | None:
        return _jsnull_to_none(self._binding.cursor)
    
    @cursor.setter
    def cursor(self, value: str | None) -> None:
        self._binding.cursor = value

    @property
    def delimiter(self) -> str | None:
        return _jsnull_to_none(self._binding.delimiter)
    
    @delimiter.setter
    def delimiter(self, value: str | None) -> None:
        self._binding.delimiter = value

    @property
    def start_after(self) -> str | None:
        return _jsnull_to_none(self._binding.startAfter)
    
    @start_after.setter
    def start_after(self, value: str | None) -> None:
        self._binding.startAfter = value


class R2StringChecksums:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2StringChecksums:
        instance = object.__new__(cls)
        instance._binding = js_obj
        return instance

    @property
    def js_object(self) -> JsProxy:
        return self._binding

    def __getattr__(self, name: str) -> Any:
        return getattr(self._binding, name)

    @property
    def md5(self) -> str | None:
        return _jsnull_to_none(self._binding.md5)
    
    @md5.setter
    def md5(self, value: str | None) -> None:
        self._binding.md5 = value

    @property
    def sha1(self) -> str | None:
        return _jsnull_to_none(self._binding.sha1)
    
    @sha1.setter
    def sha1(self, value: str | None) -> None:
        self._binding.sha1 = value

    @property
    def sha256(self) -> str | None:
        return _jsnull_to_none(self._binding.sha256)
    
    @sha256.setter
    def sha256(self, value: str | None) -> None:
        self._binding.sha256 = value


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
