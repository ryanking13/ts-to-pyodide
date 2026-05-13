from __future__ import annotations
from prelude import *

class R2Object:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2Object:
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
    def key(self) -> str:
        return self._js_obj.key

    @property
    def version(self) -> str:
        return self._js_obj.version

    @property
    def size(self) -> int | float:
        return self._js_obj.size

    @property
    def etag(self) -> str:
        return self._js_obj.etag

    @property
    def http_etag(self) -> str:
        return self._js_obj.httpEtag

    @property
    def checksums(self) -> R2Checksums:
        return R2Checksums.from_js(self._js_obj.checksums)

    @property
    def uploaded(self) -> datetime:
        return _from_js_date(self._js_obj.uploaded)

    @property
    def http_metadata(self) -> R2HTTPMetadata | None:
        _v = _jsnull_to_none(self._js_obj.httpMetadata)
        return to_py(_v) if _v is not None else None

    @property
    def custom_metadata(self) -> dict[str, str] | None:
        _v = _jsnull_to_none(self._js_obj.customMetadata)
        return _v.to_py() if _v is not None else None

    @property
    def storage_class(self) -> str:
        return self._js_obj.storageClass

    def write_http_metadata(self, headers: Headers) -> None:
        self._js_obj.writeHttpMetadata(headers.js_object if isinstance(headers, Headers) else headers)

    def __len__(self) -> int:
        return self._js_obj.__len__()


class R2Bucket:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2Bucket:
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

    async def head(self, key: str) -> R2Object | None:
        _v = _jsnull_to_none(await self._js_obj.head(key))
        return R2Object.from_js(_v) if _v is not None else None

    async def get(self, key: str, options: R2GetOptions | None = None) -> R2ObjectBody | None:
        _v = _jsnull_to_none(await self._js_obj.get(key, to_js(options)))
        return R2ObjectBody.from_js(_v) if _v is not None else None

    async def put(self, key: str, value: JsProxy | JsBuffer | str | Any | None, options: R2PutOptions | None = None) -> R2Object:
        return R2Object.from_js(await self._js_obj.put(key, to_js(value), to_js(options)))

    async def create_multipart_upload(self, key: str, options: R2MultipartOptions | None = None) -> R2MultipartUpload:
        return R2MultipartUpload.from_js(await self._js_obj.createMultipartUpload(key, to_js(options)))

    def resume_multipart_upload(self, key: str, upload_id: str) -> R2MultipartUpload:
        return R2MultipartUpload.from_js(self._js_obj.resumeMultipartUpload(key, upload_id))

    async def delete(self, keys: str | list[str]) -> None:
        await self._js_obj.delete(to_js(keys))

    async def list(self, options: R2ListOptions | None = None) -> R2Objects:
        return R2Objects.from_js(await self._js_obj.list(to_js(options)))


class R2Checksums:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2Checksums:
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
    def md5(self) -> JsBuffer | None:
        return _jsnull_to_none(self._js_obj.md5)

    @property
    def sha1(self) -> JsBuffer | None:
        return _jsnull_to_none(self._js_obj.sha1)

    @property
    def sha256(self) -> JsBuffer | None:
        return _jsnull_to_none(self._js_obj.sha256)

    def to_json(self) -> R2StringChecksums:
        return to_py(self._js_obj.toJSON())


class R2HTTPMetadata(TypedDict, total=False):
    contentType: str
    contentLanguage: str
    contentDisposition: str
    contentEncoding: str
    cacheControl: str


class R2GetOptions(TypedDict, total=False):
    onlyIf: R2Conditional | Headers | None
    range: Headers
    ssecKey: JsBuffer | str | None


class R2ObjectBody:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2ObjectBody:
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
    def body(self) -> JsProxy:
        return self._js_obj.body

    @property
    def body_used(self) -> bool:
        return self._js_obj.bodyUsed

    async def array_buffer(self) -> JsBuffer:
        return await self._js_obj.arrayBuffer()

    async def text(self) -> str:
        return await self._js_obj.text()

    async def json(self) -> Any:
        return await self._js_obj.json()

    async def blob(self) -> Any:
        return await self._js_obj.blob()


class R2Conditional(TypedDict, total=False):
    etagMatches: str
    etagDoesNotMatch: str
    uploadedBefore: datetime
    uploadedAfter: datetime
    secondsGranularity: bool


class R2PutOptions(TypedDict, total=False):
    onlyIf: R2Conditional | Headers | None
    httpMetadata: R2HTTPMetadata | Headers | None
    customMetadata: dict[str, str]
    md5: JsBuffer | str | None
    sha256: JsBuffer | str | None
    storageClass: str
    ssecKey: JsBuffer | str | None


class R2MultipartOptions(TypedDict, total=False):
    httpMetadata: R2HTTPMetadata | Headers | None
    customMetadata: dict[str, str]
    storageClass: str


class R2MultipartUpload:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2MultipartUpload:
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
    def key(self) -> str:
        return self._js_obj.key

    @property
    def upload_id(self) -> str:
        return self._js_obj.uploadId

    async def upload_part(self, part_number: int | float, value: JsProxy | JsBuffer | str | Any) -> R2UploadedPart:
        return to_py(await self._js_obj.uploadPart(part_number, to_js(value)))

    async def abort(self) -> None:
        await self._js_obj.abort()

    async def complete(self, uploaded_parts: list[R2UploadedPart]) -> R2Object:
        return R2Object.from_js(await self._js_obj.complete(to_js(uploaded_parts)))


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


class R2UploadedPart(TypedDict):
    partNumber: int | float
    etag: str


class R2Objects:
    _js_obj: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> R2Objects:
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
    def objects(self) -> list[R2Object]:
        return [R2Object.from_js(e) for e in self._js_obj.objects]
    
    @objects.setter
    def objects(self, value: list[R2Object]) -> None:
        self._js_obj.objects = value

    @property
    def delimited_prefixes(self) -> list[str]:
        return self._js_obj.delimitedPrefixes
    
    @delimited_prefixes.setter
    def delimited_prefixes(self, value: list[str]) -> None:
        self._js_obj.delimitedPrefixes = value

    @property
    def truncated(self) -> bool:
        return self._js_obj.truncated
    
    @truncated.setter
    def truncated(self, value: bool) -> None:
        self._js_obj.truncated = value

    @property
    def cursor(self) -> str | None:
        return _jsnull_to_none(self._js_obj.cursor)
    
    @cursor.setter
    def cursor(self, value: str | None) -> None:
        self._js_obj.cursor = value
