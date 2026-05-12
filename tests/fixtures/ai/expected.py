from __future__ import annotations
from prelude import (  # noqa: F401
    Any, Literal, Never, TypedDict, overload,
    js, JsBuffer, JsProxy, create_proxy, to_js,
    datetime, timezone,
    _jsnull_to_none, _auto_to_py, _none_to_jsnull,
    _to_js_date, _from_js_date,
    Headers,
)

class BaseAiImageClassification:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiImageClassification:
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
    def inputs(self) -> AiImageClassificationInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiImageClassificationInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> AiImageClassificationOutput:
        return _auto_to_py(self._binding.postProcessedOutputs)
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: AiImageClassificationOutput) -> None:
        self._binding.postProcessedOutputs = value


class BaseAiImageToText:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiImageToText:
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
    def inputs(self) -> AiImageToTextInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiImageToTextInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> AiImageToTextOutput:
        return _auto_to_py(self._binding.postProcessedOutputs)
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: AiImageToTextOutput) -> None:
        self._binding.postProcessedOutputs = value


class BaseAiImageTextToText:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiImageTextToText:
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
    def inputs(self) -> AiImageTextToTextInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiImageTextToTextInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> AiImageTextToTextOutput:
        return _auto_to_py(self._binding.postProcessedOutputs)
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: AiImageTextToTextOutput) -> None:
        self._binding.postProcessedOutputs = value


class BaseAiMultimodalEmbeddings:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiMultimodalEmbeddings:
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
    def inputs(self) -> AiImageTextToTextInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiImageTextToTextInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> AiImageTextToTextOutput:
        return _auto_to_py(self._binding.postProcessedOutputs)
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: AiImageTextToTextOutput) -> None:
        self._binding.postProcessedOutputs = value


class BaseAiObjectDetection:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiObjectDetection:
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
    def inputs(self) -> AiObjectDetectionInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiObjectDetectionInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> AiObjectDetectionOutput:
        return _auto_to_py(self._binding.postProcessedOutputs)
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: AiObjectDetectionOutput) -> None:
        self._binding.postProcessedOutputs = value


class BaseAiSentenceSimilarity:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiSentenceSimilarity:
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
    def inputs(self) -> AiSentenceSimilarityInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiSentenceSimilarityInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> Any:
        return self._binding.postProcessedOutputs
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: Any) -> None:
        self._binding.postProcessedOutputs = value


class BaseAiAutomaticSpeechRecognition:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiAutomaticSpeechRecognition:
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
    def inputs(self) -> AiAutomaticSpeechRecognitionInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiAutomaticSpeechRecognitionInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> AiAutomaticSpeechRecognitionOutput:
        return _auto_to_py(self._binding.postProcessedOutputs)
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: AiAutomaticSpeechRecognitionOutput) -> None:
        self._binding.postProcessedOutputs = value


class BaseAiSummarization:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiSummarization:
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
    def inputs(self) -> AiSummarizationInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiSummarizationInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> AiSummarizationOutput:
        return _auto_to_py(self._binding.postProcessedOutputs)
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: AiSummarizationOutput) -> None:
        self._binding.postProcessedOutputs = value


class BaseAiTextClassification:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiTextClassification:
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
    def inputs(self) -> AiTextClassificationInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiTextClassificationInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> AiTextClassificationOutput:
        return _auto_to_py(self._binding.postProcessedOutputs)
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: AiTextClassificationOutput) -> None:
        self._binding.postProcessedOutputs = value


class BaseAiTextEmbeddings:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiTextEmbeddings:
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
    def inputs(self) -> AiTextEmbeddingsInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiTextEmbeddingsInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> AiTextEmbeddingsOutput:
        return _auto_to_py(self._binding.postProcessedOutputs)
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: AiTextEmbeddingsOutput) -> None:
        self._binding.postProcessedOutputs = value


class BaseAiTextGeneration:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiTextGeneration:
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
    def inputs(self) -> AiTextGenerationInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiTextGenerationInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> AiTextGenerationOutput:
        return _auto_to_py(self._binding.postProcessedOutputs)
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: AiTextGenerationOutput) -> None:
        self._binding.postProcessedOutputs = value


class BaseAiTextToSpeech:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiTextToSpeech:
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
    def inputs(self) -> AiTextToSpeechInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiTextToSpeechInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> AiTextToSpeechOutput:
        return _auto_to_py(self._binding.postProcessedOutputs)
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: AiTextToSpeechOutput) -> None:
        self._binding.postProcessedOutputs = value


class BaseAiTextToImage:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiTextToImage:
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
    def inputs(self) -> AiTextToImageInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiTextToImageInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> Any:
        return self._binding.postProcessedOutputs
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: Any) -> None:
        self._binding.postProcessedOutputs = value


class BaseAiTranslation:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> BaseAiTranslation:
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
    def inputs(self) -> AiTranslationInput:
        return _auto_to_py(self._binding.inputs)
    
    @inputs.setter
    def inputs(self, value: AiTranslationInput) -> None:
        self._binding.inputs = value

    @property
    def post_processed_outputs(self) -> AiTranslationOutput:
        return _auto_to_py(self._binding.postProcessedOutputs)
    
    @post_processed_outputs.setter
    def post_processed_outputs(self, value: AiTranslationOutput) -> None:
        self._binding.postProcessedOutputs = value


class Ai:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> Ai:
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
    def ai_gateway_log_id(self) -> str | None:
        return _jsnull_to_none(self._binding.aiGatewayLogId)
    
    @ai_gateway_log_id.setter
    def ai_gateway_log_id(self, value: str | None) -> None:
        self._binding.aiGatewayLogId = value

    async def run(self, *args: Any, **kwargs: Any) -> Any:
        _a = list(args)
        if len(_a) > 0:
            _a[0] = to_js(_a[0])
        if len(_a) > 1:
            _a[1] = to_js(_a[1])
        if len(_a) > 2:
            _a[2] = to_js(_a[2])
        _r = await self._binding.run(*_a, **kwargs)
        if isinstance(args[1], str):
            return _auto_to_py(_r)
        elif isinstance(args[1], str):
            return _auto_to_py(_r)
        elif isinstance(args[1], str):
            return _auto_to_py(_r)
        return _r

    async def models(self, params: AiModelsSearchParams | None = None) -> list[AiModelsSearchObject]:
        return [_auto_to_py(e) for e in await self._binding.models(to_js(params))]

    async def to_markdown(self, *args: Any, **kwargs: Any) -> Any:
        _a = list(args)
        if len(_a) > 0:
            _a[0] = to_js(_a[0])
        if len(_a) > 1:
            _a[1] = to_js(_a[1])
        _r = await self._binding.toMarkdown(*_a, **kwargs)
        if len(args) <= 0:
            return ToMarkdownService.from_js(_r)
        elif isinstance(args[0], list):
            return [_auto_to_py(e) for e in _r]
        elif isinstance(args[0], str):
            return _auto_to_py(_r)
        return _r


class ToMarkdownService:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> ToMarkdownService:
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

    async def transform(self, *args: Any, **kwargs: Any) -> Any:
        _a = list(args)
        if len(_a) > 0:
            _a[0] = to_js(_a[0])
        if len(_a) > 1:
            _a[1] = to_js(_a[1])
        _r = await self._binding.transform(*_a, **kwargs)
        if isinstance(args[0], list):
            return [_auto_to_py(e) for e in _r]
        elif isinstance(args[0], str):
            return _auto_to_py(_r)
        return _r

    async def supported(self) -> list[SupportedFileFormat]:
        return [_auto_to_py(e) for e in await self._binding.supported()]


class AiModels:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> AiModels:
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


class AiImageClassificationInput(TypedDict):
    image: list[int | float]


class AiImageToTextInput(TypedDict):
    image: list[int | float]
    prompt: str | None
    max_tokens: int | float | None
    temperature: int | float | None
    top_p: int | float | None
    top_k: int | float | None
    seed: int | float | None
    repetition_penalty: int | float | None
    frequency_penalty: int | float | None
    presence_penalty: int | float | None
    raw: bool | None
    messages: list[RoleScopedChatInput] | None


class AiImageToTextOutput(TypedDict):
    description: str


class AiImageTextToTextInput(TypedDict):
    image: str
    prompt: str | None
    max_tokens: int | float | None
    temperature: int | float | None
    ignore_eos: bool | None
    top_p: int | float | None
    top_k: int | float | None
    seed: int | float | None
    repetition_penalty: int | float | None
    frequency_penalty: int | float | None
    presence_penalty: int | float | None
    raw: bool | None
    messages: list[RoleScopedChatInput] | None


class AiImageTextToTextOutput(TypedDict):
    description: str


class AiObjectDetectionInput(TypedDict):
    image: list[int | float]


class AiSentenceSimilarityInput(TypedDict):
    source: str
    sentences: list[str]


class AiAutomaticSpeechRecognitionInput(TypedDict):
    audio: list[int | float]


class AiAutomaticSpeechRecognitionOutput(TypedDict):
    text: str | None
    words: list[Any] | None
    vtt: str | None
    word: str
    start: int | float
    end: int | float


class AiSummarizationInput(TypedDict):
    input_text: str
    max_length: int | float | None


class AiSummarizationOutput(TypedDict):
    summary: str


class AiTextClassificationInput(TypedDict):
    text: str


class AiTextEmbeddingsInput(TypedDict):
    text: str | list[str]


class AiTextEmbeddingsOutput(TypedDict):
    shape: list[int | float]
    data: list[list[int | float]]


class AiTextGenerationInput(TypedDict, total=False):
    prompt: str
    raw: bool
    stream: bool
    max_tokens: int | float
    temperature: int | float
    top_p: int | float
    top_k: int | float
    seed: int | float
    repetition_penalty: int | float
    frequency_penalty: int | float
    presence_penalty: int | float
    messages: list[RoleScopedChatInput]
    response_format: AiTextGenerationResponseFormat
    tools: list[AiTextGenerationToolInput] | list[AiTextGenerationToolLegacyInput] | (Any) | None
    functions: list[AiTextGenerationFunctionsInput]


class AiTextGenerationOutput(TypedDict, total=False):
    response: str
    tool_calls: Any
    usage: UsageTags


class AiTextToSpeechInput(TypedDict):
    prompt: str
    lang: str | None


class AiTextToImageInput(TypedDict):
    prompt: str
    negative_prompt: str | None
    height: int | float | None
    width: int | float | None
    image: list[int | float] | None
    image_b64: str | None
    mask: list[int | float] | None
    num_steps: int | float | None
    strength: int | float | None
    guidance: int | float | None
    seed: int | float | None


class AiTranslationInput(TypedDict):
    text: str
    target_lang: str
    source_lang: str | None


class AiTranslationOutput(TypedDict, total=False):
    translated_text: str


class GatewayOptions(TypedDict):
    id: str
    cacheKey: str | None
    cacheTtl: int | float | None
    skipCache: bool | None
    metadata: dict[str, int | float | str | bool | int | None] | None
    collectLog: bool | None
    eventId: str | None
    requestTimeoutMs: int | float | None
    retries: GatewayRetries | None


class AiAsyncBatchResponse(TypedDict):
    request_id: str


class AiOptions(TypedDict, total=False):
    queueRequest: bool
    websocket: bool
    tags: list[str]
    gateway: GatewayOptions
    returnRawResponse: bool
    prefix: str
    extraHeaders: Any
    signal: Any


class AiModelsSearchParams(TypedDict, total=False):
    author: str
    hide_experimental: bool
    page: int | float
    per_page: int | float
    search: str
    source: int | float
    task: str


class AiModelsSearchObject(TypedDict):
    id: str
    source: int | float
    name: str
    description: str
    task: AiModelsSearchObjectTask
    tags: list[str]
    properties: list[Any]
    property_id: str
    value: str


class MarkdownDocument(TypedDict):
    name: str
    blob: Any


class ConversionRequestOptions(TypedDict, total=False):
    gateway: GatewayOptions
    extraHeaders: Any
    conversionOptions: ConversionOptions


class SupportedFileFormat(TypedDict):
    mimeType: str
    extension: str


class RoleScopedChatInput(TypedDict):
    role: (Any) | Literal["user", "assistant", "system", "tool"]
    content: str
    name: str | None


class AiTextGenerationResponseFormat(TypedDict):
    type: str
    json_schema: Any | None


class AiTextGenerationToolInput(TypedDict):
    type: (Any) | Literal["function"]
    function: AiTextGenerationToolInputFunction


class AiTextGenerationToolLegacyInput(TypedDict):
    name: str
    description: str
    parameters: AiTextGenerationToolLegacyInputParameters | None


class AiTextGenerationFunctionsInput(TypedDict):
    name: str
    code: str


class AiTextGenerationToolLegacyOutput(TypedDict):
    name: str
    arguments: Any


class AiTextGenerationToolOutput(TypedDict):
    id: str
    type: Literal["function"]
    function: AiTextGenerationToolOutputFunction


class UsageTags(TypedDict):
    prompt_tokens: int | float
    completion_tokens: int | float
    total_tokens: int | float


class GatewayRetries(TypedDict, total=False):
    maxAttempts: Literal[1, 2, 3, 4, 5] | None
    retryDelayMs: int | float
    backoff: Literal["constant", "linear", "exponential"] | None


class ConversionOptions(TypedDict, total=False):
    html: ConversionOptionsHtml
    docx: ConversionOptionsDocx
    image: ImageConversionOptions
    pdf: ConversionOptionsPdf
    descriptionLanguage: Literal["en", "es", "fr", "it", "pt", "de"] | None
    convert: bool
    maxConvertedImages: int | float
    convertOGImage: bool


class EmbeddedImageConversionOptions(TypedDict, total=False):
    descriptionLanguage: Literal["en", "es", "fr", "it", "pt", "de"] | None
    convert: bool
    maxConvertedImages: int | float


class ImageConversionOptions(TypedDict, total=False):
    descriptionLanguage: Literal["en", "es", "fr", "it", "pt", "de"] | None


class AiImageClassificationOutput(TypedDict, total=False):
    score: int | float
    label: str


class AiObjectDetectionOutput(TypedDict, total=False):
    score: int | float
    label: str


class AiTextClassificationOutput(TypedDict, total=False):
    score: int | float
    label: str


class AiTextToSpeechOutput(TypedDict):
    audio: str


class AiModelsSearchObjectTask(TypedDict):
    id: str
    name: str
    description: str


class ConversionResponse(TypedDict):
    id: str
    name: str
    mimeType: str
    format: bool
    tokens: int | float | None
    data: str | None
    error: str | None


class AiTextGenerationToolInputFunctionParameters(TypedDict):
    type: (Any) | Literal["object"]
    properties: Any
    required: list[str]


class AiTextGenerationToolInputFunction(TypedDict):
    name: str
    description: str
    parameters: AiTextGenerationToolInputFunctionParameters | None


class AiTextGenerationToolLegacyInputParameters(TypedDict):
    type: (Any) | Literal["object"]
    properties: Any
    required: list[str]


class AiTextGenerationToolOutputFunction(TypedDict):
    name: str
    arguments: str


class ConversionOptionsHtml(TypedDict, total=False):
    images: Any
    hostname: str
    cssSelector: str


class ConversionOptionsDocx(TypedDict, total=False):
    images: EmbeddedImageConversionOptions


class ConversionOptionsPdf(TypedDict, total=False):
    images: EmbeddedImageConversionOptions
    metadata: bool
