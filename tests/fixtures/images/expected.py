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

class ImagesBinding:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> ImagesBinding:
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
    def hosted(self) -> HostedImagesBinding:
        return HostedImagesBinding.from_js(self._binding.hosted)

    async def info(self, stream: Any, options: ImageInputOptions | None = None) -> ImageInfoResponse:
        return _auto_to_py(await self._binding.info(to_js(stream), to_js(options)))

    def input(self, stream: Any, options: ImageInputOptions | None = None) -> ImageTransformer:
        return ImageTransformer.from_js(self._binding.input(to_js(stream), to_js(options)))


class ImageTransformer:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> ImageTransformer:
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

    def transform(self, transform: ImageTransform) -> ImageTransformer:
        return ImageTransformer.from_js(self._binding.transform(to_js(transform)))

    def draw(self, image: Any | ImageTransformer, options: ImageDrawOptions | None = None) -> ImageTransformer:
        return ImageTransformer.from_js(self._binding.draw(to_js(image), to_js(options)))

    async def output(self, options: ImageOutputOptions) -> ImageTransformationResult:
        return ImageTransformationResult.from_js(await self._binding.output(to_js(options)))


class HostedImagesBinding:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> HostedImagesBinding:
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

    def image(self, image_id: str) -> ImageHandle:
        return ImageHandle.from_js(self._binding.image(image_id))

    async def upload(self, image: Any | JsBuffer, options: ImageUploadOptions | None = None) -> ImageMetadata:
        return _auto_to_py(await self._binding.upload(to_js(image), to_js(options)))

    async def list(self, options: ImageListOptions | None = None) -> ImageList:
        return _auto_to_py(await self._binding.list(to_js(options)))


class ImageTransformationResult:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> ImageTransformationResult:
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

    def response(self) -> Any:
        return self._binding.response()

    def content_type(self) -> str:
        return self._binding.contentType()

    def image(self, options: ImageTransformationOutputOptions | None = None) -> Any:
        return self._binding.image(to_js(options))


class ImageHandle:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> ImageHandle:
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

    async def details(self) -> ImageMetadata | None:
        _v = _jsnull_to_none(await self._binding.details())
        return _auto_to_py(_v) if _v is not None else None

    async def bytes(self) -> Any | None:
        return _jsnull_to_none(await self._binding.bytes())

    async def update(self, options: ImageUpdateOptions) -> ImageMetadata:
        return _auto_to_py(await self._binding.update(to_js(options)))

    async def delete(self) -> bool:
        return await self._binding.delete()


class ImageUploadOptions(TypedDict, total=False):
    id: str
    filename: str
    requireSignedURLs: bool
    metadata: dict[str, Any]
    creator: str
    encoding: Literal["base64"]


class ImageMetadata(TypedDict):
    id: str
    filename: str | None
    uploaded: str | None
    requireSignedURLs: bool
    meta: dict[str, Any] | None
    variants: list[str]
    draft: bool | None
    creator: str | None


class ImageListOptions(TypedDict, total=False):
    limit: int | float
    cursor: str
    sortOrder: Literal["asc", "desc"] | None
    creator: str


class ImageList(TypedDict):
    images: list[ImageMetadata]
    cursor: str | None
    listComplete: bool


class ImageUpdateOptions(TypedDict, total=False):
    requireSignedURLs: bool
    metadata: dict[str, Any]
    creator: str


class ImageInputOptions(TypedDict, total=False):
    encoding: Literal["base64"]


class ImageTransform(TypedDict):
    width: int | float | None
    height: int | float | None
    background: str | None
    blur: int | float | None
    border: Any | None
    brightness: int | float | None
    contrast: int | float | None
    fit: Literal["scale-down", "contain", "pad", "squeeze", "cover", "crop"] | None
    flip: Literal["h", "v", "hv"] | None
    gamma: int | float | None
    segment: Literal["foreground"] | None
    gravity: Any | Literal["face", "left", "right", "top", "bottom", "center", "auto", "entropy"] | None
    rotate: Literal[0, 90, 180, 270] | None
    saturation: int | float | None
    sharpen: int | float | None
    trim: Any | Literal["border"] | None
    color: str | None
    top: int | float | None
    bottom: int | float | None
    left: int | float | None
    right: int | float | None
    x: int | float | None
    y: int | float | None
    mode: Literal["remainder", "box-center"]
    tolerance: int | float | None
    keep: int | float | None


class ImageDrawOptions(TypedDict, total=False):
    opacity: int | float
    repeat: bool | str | None
    top: int | float
    left: int | float
    bottom: int | float
    right: int | float


class ImageOutputOptions(TypedDict):
    format: Literal["image/jpeg", "image/png", "image/gif", "image/webp", "image/avif", "rgb", "rgba"]
    quality: int | float | None
    background: str | None
    anim: bool | None


class ImageTransformationOutputOptions(TypedDict, total=False):
    encoding: Literal["base64"]


class ImageInfoResponse(TypedDict):
    format: Literal["image/svg+xml"] | str
    fileSize: int | float | None
    width: int | float | None
    height: int | float | None
