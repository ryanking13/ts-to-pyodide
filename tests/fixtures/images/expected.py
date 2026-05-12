from __future__ import annotations
from prelude import (  # noqa: F401
    Any, Literal, Never, TypedDict, overload,
    js, JsBuffer, JsProxy, create_proxy, to_js,
    datetime, timezone,
    _jsnull_to_none, _auto_to_py, _none_to_jsnull,
    _to_js_date, _from_js_date,
    Headers,
)

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

    async def info(self, stream: JsProxy, options: ImageInputOptions | None = None) -> ImageInfoResponse:
        return _auto_to_py(await self._binding.info(to_js(stream), to_js(options)))

    def input(self, stream: JsProxy, options: ImageInputOptions | None = None) -> ImageTransformer:
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

    def draw(self, image: JsProxy | ImageTransformer, options: ImageDrawOptions | None = None) -> ImageTransformer:
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

    async def upload(self, image: JsProxy | JsBuffer, options: ImageUploadOptions | None = None) -> ImageMetadata:
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

    def image(self, options: ImageTransformationOutputOptions | None = None) -> JsProxy:
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

    async def bytes(self) -> JsProxy | None:
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


class ImageTransform(TypedDict, total=False):
    width: int | float
    height: int | float
    background: str
    blur: int | float
    border: ImageTransformBorder | None
    brightness: int | float
    contrast: int | float
    fit: Literal["scale-down", "contain", "pad", "squeeze", "cover", "crop"] | None
    flip: Literal["h", "v", "hv"] | None
    gamma: int | float
    segment: Literal["foreground"]
    gravity: ImageTransformGravity | Literal["face", "left", "right", "top", "bottom", "center", "auto", "entropy"] | None
    rotate: Literal[0, 90, 180, 270] | None
    saturation: int | float
    sharpen: int | float
    trim: ImageTransformTrim | Literal["border"] | None


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


class ImageTransformBorder(TypedDict, total=False):
    color: str
    width: int | float
    top: int | float
    bottom: int | float
    left: int | float
    right: int | float


class ImageTransformGravity(TypedDict):
    x: int | float | None
    y: int | float | None
    mode: Literal["remainder", "box-center"]


class ImageTransformTrimBorder(TypedDict, total=False):
    color: str
    tolerance: int | float
    keep: int | float


class ImageTransformTrim(TypedDict, total=False):
    top: int | float
    bottom: int | float
    left: int | float
    right: int | float
    width: int | float
    height: int | float
    border: bool | ImageTransformTrimBorder | None
