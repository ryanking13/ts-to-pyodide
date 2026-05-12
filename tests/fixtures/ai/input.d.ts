// Copied from @cloudflare/workers-types@4.20260506.1 latest/index.d.ts
// Core AI input/output types (lines 4860-5133), AiOptions/Ai class (lines 10836-10975),
// GatewayRetries/GatewayOptions (lines 10976-10991),
// Markdown/Conversion types + ToMarkdownService (lines 14528-14591)
// AiModels simplified to representative models only (original has 80+ entries)
type AiImageClassificationInput = {
  image: number[];
};
type AiImageClassificationOutput = {
  score?: number;
  label?: string;
}[];
declare abstract class BaseAiImageClassification {
  inputs: AiImageClassificationInput;
  postProcessedOutputs: AiImageClassificationOutput;
}
type AiImageToTextInput = {
  image: number[];
  prompt?: string;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
  top_k?: number;
  seed?: number;
  repetition_penalty?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  raw?: boolean;
  messages?: RoleScopedChatInput[];
};
type AiImageToTextOutput = {
  description: string;
};
declare abstract class BaseAiImageToText {
  inputs: AiImageToTextInput;
  postProcessedOutputs: AiImageToTextOutput;
}
type AiImageTextToTextInput = {
  image: string;
  prompt?: string;
  max_tokens?: number;
  temperature?: number;
  ignore_eos?: boolean;
  top_p?: number;
  top_k?: number;
  seed?: number;
  repetition_penalty?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  raw?: boolean;
  messages?: RoleScopedChatInput[];
};
type AiImageTextToTextOutput = {
  description: string;
};
declare abstract class BaseAiImageTextToText {
  inputs: AiImageTextToTextInput;
  postProcessedOutputs: AiImageTextToTextOutput;
}
type AiMultimodalEmbeddingsInput = {
  image: string;
  text: string[];
};
type AiIMultimodalEmbeddingsOutput = {
  data: number[][];
  shape: number[];
};
declare abstract class BaseAiMultimodalEmbeddings {
  inputs: AiImageTextToTextInput;
  postProcessedOutputs: AiImageTextToTextOutput;
}
type AiObjectDetectionInput = {
  image: number[];
};
type AiObjectDetectionOutput = {
  score?: number;
  label?: string;
}[];
declare abstract class BaseAiObjectDetection {
  inputs: AiObjectDetectionInput;
  postProcessedOutputs: AiObjectDetectionOutput;
}
type AiSentenceSimilarityInput = {
  source: string;
  sentences: string[];
};
type AiSentenceSimilarityOutput = number[];
declare abstract class BaseAiSentenceSimilarity {
  inputs: AiSentenceSimilarityInput;
  postProcessedOutputs: AiSentenceSimilarityOutput;
}
type AiAutomaticSpeechRecognitionInput = {
  audio: number[];
};
type AiAutomaticSpeechRecognitionOutput = {
  text?: string;
  words?: {
    word: string;
    start: number;
    end: number;
  }[];
  vtt?: string;
};
declare abstract class BaseAiAutomaticSpeechRecognition {
  inputs: AiAutomaticSpeechRecognitionInput;
  postProcessedOutputs: AiAutomaticSpeechRecognitionOutput;
}
type AiSummarizationInput = {
  input_text: string;
  max_length?: number;
};
type AiSummarizationOutput = {
  summary: string;
};
declare abstract class BaseAiSummarization {
  inputs: AiSummarizationInput;
  postProcessedOutputs: AiSummarizationOutput;
}
type AiTextClassificationInput = {
  text: string;
};
type AiTextClassificationOutput = {
  score?: number;
  label?: string;
}[];
declare abstract class BaseAiTextClassification {
  inputs: AiTextClassificationInput;
  postProcessedOutputs: AiTextClassificationOutput;
}
type AiTextEmbeddingsInput = {
  text: string | string[];
};
type AiTextEmbeddingsOutput = {
  shape: number[];
  data: number[][];
};
declare abstract class BaseAiTextEmbeddings {
  inputs: AiTextEmbeddingsInput;
  postProcessedOutputs: AiTextEmbeddingsOutput;
}
type RoleScopedChatInput = {
  role:
    | "user"
    | "assistant"
    | "system"
    | "tool"
    | (string & NonNullable<unknown>);
  content: string;
  name?: string;
};
type AiTextGenerationToolLegacyInput = {
  name: string;
  description: string;
  parameters?: {
    type: "object" | (string & NonNullable<unknown>);
    properties: {
      [key: string]: {
        type: string;
        description?: string;
      };
    };
    required: string[];
  };
};
type AiTextGenerationToolInput = {
  type: "function" | (string & NonNullable<unknown>);
  function: {
    name: string;
    description: string;
    parameters?: {
      type: "object" | (string & NonNullable<unknown>);
      properties: {
        [key: string]: {
          type: string;
          description?: string;
        };
      };
      required: string[];
    };
  };
};
type AiTextGenerationFunctionsInput = {
  name: string;
  code: string;
};
type AiTextGenerationResponseFormat = {
  type: string;
  json_schema?: any;
};
type AiTextGenerationInput = {
  prompt?: string;
  raw?: boolean;
  stream?: boolean;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
  top_k?: number;
  seed?: number;
  repetition_penalty?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  messages?: RoleScopedChatInput[];
  response_format?: AiTextGenerationResponseFormat;
  tools?:
    | AiTextGenerationToolInput[]
    | AiTextGenerationToolLegacyInput[]
    | (object & NonNullable<unknown>);
  functions?: AiTextGenerationFunctionsInput[];
};
type AiTextGenerationToolLegacyOutput = {
  name: string;
  arguments: unknown;
};
type AiTextGenerationToolOutput = {
  id: string;
  type: "function";
  function: {
    name: string;
    arguments: string;
  };
};
type UsageTags = {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
};
type AiTextGenerationOutput = {
  response?: string;
  tool_calls?: AiTextGenerationToolLegacyOutput[] &
    AiTextGenerationToolOutput[];
  usage?: UsageTags;
};
declare abstract class BaseAiTextGeneration {
  inputs: AiTextGenerationInput;
  postProcessedOutputs: AiTextGenerationOutput;
}
type AiTextToSpeechInput = {
  prompt: string;
  lang?: string;
};
type AiTextToSpeechOutput =
  | Uint8Array
  | {
      audio: string;
    };
declare abstract class BaseAiTextToSpeech {
  inputs: AiTextToSpeechInput;
  postProcessedOutputs: AiTextToSpeechOutput;
}
type AiTextToImageInput = {
  prompt: string;
  negative_prompt?: string;
  height?: number;
  width?: number;
  image?: number[];
  image_b64?: string;
  mask?: number[];
  num_steps?: number;
  strength?: number;
  guidance?: number;
  seed?: number;
};
type AiTextToImageOutput = ReadableStream<Uint8Array>;
declare abstract class BaseAiTextToImage {
  inputs: AiTextToImageInput;
  postProcessedOutputs: AiTextToImageOutput;
}
type AiTranslationInput = {
  text: string;
  target_lang: string;
  source_lang?: string;
};
type AiTranslationOutput = {
  translated_text?: string;
};
declare abstract class BaseAiTranslation {
  inputs: AiTranslationInput;
  postProcessedOutputs: AiTranslationOutput;
}
type GatewayRetries = {
  maxAttempts?: 1 | 2 | 3 | 4 | 5;
  retryDelayMs?: number;
  backoff?: "constant" | "linear" | "exponential";
};
type GatewayOptions = {
  id: string;
  cacheKey?: string;
  cacheTtl?: number;
  skipCache?: boolean;
  metadata?: Record<string, number | string | boolean | null | bigint>;
  collectLog?: boolean;
  eventId?: string;
  requestTimeoutMs?: number;
  retries?: GatewayRetries;
};
type AiOptions = {
  queueRequest?: boolean;
  websocket?: boolean;
  tags?: string[];
  gateway?: GatewayOptions;
  returnRawResponse?: boolean;
  prefix?: string;
  extraHeaders?: object;
  signal?: AbortSignal;
};
type AiModelsSearchParams = {
  author?: string;
  hide_experimental?: boolean;
  page?: number;
  per_page?: number;
  search?: string;
  source?: number;
  task?: string;
};
type AiModelsSearchObject = {
  id: string;
  source: number;
  name: string;
  description: string;
  task: {
    id: string;
    name: string;
    description: string;
  };
  tags: string[];
  properties: {
    property_id: string;
    value: string;
  }[];
};
type AiModelListType = Record<string, any>;
type AiAsyncBatchResponse = {
  request_id: string;
};
interface AiModels {
  "@cf/microsoft/resnet-50": BaseAiImageClassification;
  "@cf/meta/llama-2-7b-chat-int8": BaseAiTextGeneration;
  "@cf/baai/bge-base-en-v1.5": BaseAiTextEmbeddings;
  "@cf/stabilityai/stable-diffusion-xl-base-1.0": BaseAiTextToImage;
  "@cf/facebook/bart-large-cnn": BaseAiSummarization;
  "@cf/huggingface/distilbert-sst-2-int8": BaseAiTextClassification;
  "@cf/openai/whisper": BaseAiAutomaticSpeechRecognition;
  "@cf/meta/m2m100-1.2b": BaseAiTranslation;
  "@cf/llava-hf/llava-1.5-7b-hf": BaseAiImageToText;
  "@cf/myshell-ai/melotts": BaseAiTextToSpeech;
}
declare abstract class Ai<AiModelList extends AiModelListType = AiModels> {
  aiGatewayLogId: string | null;
  run<Name extends keyof AiModelList>(
    model: Name,
    inputs: {
      requests: AiModelList[Name]["inputs"][];
    },
    options: AiOptions & {
      queueRequest: true;
    },
  ): Promise<AiAsyncBatchResponse>;
  run<Name extends keyof AiModelList>(
    model: Name,
    inputs: AiModelList[Name]["inputs"],
    options: AiOptions & {
      returnRawResponse: true;
    },
  ): Promise<Response>;
  run<Name extends keyof AiModelList>(
    model: Name,
    inputs: AiModelList[Name]["inputs"],
    options: AiOptions & {
      websocket: true;
    },
  ): Promise<Response>;
  run<Name extends keyof AiModelList>(
    model: Name,
    inputs: AiModelList[Name]["inputs"] & {
      stream: true;
    },
    options?: AiOptions,
  ): Promise<ReadableStream>;
  run<Name extends keyof AiModelList>(
    model: Name,
    inputs: AiModelList[Name]["inputs"],
    options?: AiOptions,
  ): Promise<AiModelList[Name]["postProcessedOutputs"]>;
  run(
    model: string & {},
    inputs: Record<string, unknown>,
    options?: AiOptions,
  ): Promise<Record<string, unknown>>;
  models(params?: AiModelsSearchParams): Promise<AiModelsSearchObject[]>;
  toMarkdown(): ToMarkdownService;
  toMarkdown(
    files: MarkdownDocument[],
    options?: ConversionRequestOptions,
  ): Promise<ConversionResponse[]>;
  toMarkdown(
    files: MarkdownDocument,
    options?: ConversionRequestOptions,
  ): Promise<ConversionResponse>;
}
type MarkdownDocument = {
  name: string;
  blob: Blob;
};
type ConversionResponse =
  | {
      id: string;
      name: string;
      mimeType: string;
      format: "markdown";
      tokens: number;
      data: string;
    }
  | {
      id: string;
      name: string;
      mimeType: string;
      format: "error";
      error: string;
    };
type ImageConversionOptions = {
  descriptionLanguage?: "en" | "es" | "fr" | "it" | "pt" | "de";
};
type EmbeddedImageConversionOptions = ImageConversionOptions & {
  convert?: boolean;
  maxConvertedImages?: number;
};
type ConversionOptions = {
  html?: {
    images?: EmbeddedImageConversionOptions & {
      convertOGImage?: boolean;
    };
    hostname?: string;
    cssSelector?: string;
  };
  docx?: {
    images?: EmbeddedImageConversionOptions;
  };
  image?: ImageConversionOptions;
  pdf?: {
    images?: EmbeddedImageConversionOptions;
    metadata?: boolean;
  };
};
type ConversionRequestOptions = {
  gateway?: GatewayOptions;
  extraHeaders?: object;
  conversionOptions?: ConversionOptions;
};
type SupportedFileFormat = {
  mimeType: string;
  extension: string;
};
declare abstract class ToMarkdownService {
  transform(
    files: MarkdownDocument[],
    options?: ConversionRequestOptions,
  ): Promise<ConversionResponse[]>;
  transform(
    files: MarkdownDocument,
    options?: ConversionRequestOptions,
  ): Promise<ConversionResponse>;
  supported(): Promise<SupportedFileFormat[]>;
}

declare var ai: Ai[];
