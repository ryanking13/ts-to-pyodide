// Copied from @cloudflare/workers-types@4.20260506.1 index.d.ts lines 2154-2304

interface KVNamespaceListKey<Metadata, Key extends string = string> {
  name: Key;
  expiration?: number;
  metadata?: Metadata;
}
type KVNamespaceListResult<Metadata, Key extends string = string> =
  | {
      list_complete: false;
      keys: KVNamespaceListKey<Metadata, Key>[];
      cursor: string;
      cacheStatus: string | null;
    }
  | {
      list_complete: true;
      keys: KVNamespaceListKey<Metadata, Key>[];
      cacheStatus: string | null;
    };
interface KVNamespace<Key extends string = string> {
  get(
    key: Key,
    options?: Partial<KVNamespaceGetOptions<undefined>>,
  ): Promise<string | null>;
  get(key: Key, type: "text"): Promise<string | null>;
  get<ExpectedValue = unknown>(
    key: Key,
    type: "json",
  ): Promise<ExpectedValue | null>;
  get(key: Key, type: "arrayBuffer"): Promise<ArrayBuffer | null>;
  get(key: Key, type: "stream"): Promise<ReadableStream | null>;
  get(
    key: Key,
    options?: KVNamespaceGetOptions<"text">,
  ): Promise<string | null>;
  get<ExpectedValue = unknown>(
    key: Key,
    options?: KVNamespaceGetOptions<"json">,
  ): Promise<ExpectedValue | null>;
  get(
    key: Key,
    options?: KVNamespaceGetOptions<"arrayBuffer">,
  ): Promise<ArrayBuffer | null>;
  get(
    key: Key,
    options?: KVNamespaceGetOptions<"stream">,
  ): Promise<ReadableStream | null>;
  get(key: Array<Key>, type: "text"): Promise<Map<string, string | null>>;
  get<ExpectedValue = unknown>(
    key: Array<Key>,
    type: "json",
  ): Promise<Map<string, ExpectedValue | null>>;
  get(
    key: Array<Key>,
    options?: Partial<KVNamespaceGetOptions<undefined>>,
  ): Promise<Map<string, string | null>>;
  get(
    key: Array<Key>,
    options?: KVNamespaceGetOptions<"text">,
  ): Promise<Map<string, string | null>>;
  get<ExpectedValue = unknown>(
    key: Array<Key>,
    options?: KVNamespaceGetOptions<"json">,
  ): Promise<Map<string, ExpectedValue | null>>;
  list<Metadata = unknown>(
    options?: KVNamespaceListOptions,
  ): Promise<KVNamespaceListResult<Metadata, Key>>;
  put(
    key: Key,
    value: string | ArrayBuffer | ArrayBufferView | ReadableStream,
    options?: KVNamespacePutOptions,
  ): Promise<void>;
  getWithMetadata<Metadata = unknown>(
    key: Key,
    options?: Partial<KVNamespaceGetOptions<undefined>>,
  ): Promise<KVNamespaceGetWithMetadataResult<string, Metadata>>;
  getWithMetadata<Metadata = unknown>(
    key: Key,
    type: "text",
  ): Promise<KVNamespaceGetWithMetadataResult<string, Metadata>>;
  getWithMetadata<ExpectedValue = unknown, Metadata = unknown>(
    key: Key,
    type: "json",
  ): Promise<KVNamespaceGetWithMetadataResult<ExpectedValue, Metadata>>;
  getWithMetadata<Metadata = unknown>(
    key: Key,
    type: "arrayBuffer",
  ): Promise<KVNamespaceGetWithMetadataResult<ArrayBuffer, Metadata>>;
  getWithMetadata<Metadata = unknown>(
    key: Key,
    type: "stream",
  ): Promise<KVNamespaceGetWithMetadataResult<ReadableStream, Metadata>>;
  getWithMetadata<Metadata = unknown>(
    key: Key,
    options: KVNamespaceGetOptions<"text">,
  ): Promise<KVNamespaceGetWithMetadataResult<string, Metadata>>;
  getWithMetadata<ExpectedValue = unknown, Metadata = unknown>(
    key: Key,
    options: KVNamespaceGetOptions<"json">,
  ): Promise<KVNamespaceGetWithMetadataResult<ExpectedValue, Metadata>>;
  getWithMetadata<Metadata = unknown>(
    key: Key,
    options: KVNamespaceGetOptions<"arrayBuffer">,
  ): Promise<KVNamespaceGetWithMetadataResult<ArrayBuffer, Metadata>>;
  getWithMetadata<Metadata = unknown>(
    key: Key,
    options: KVNamespaceGetOptions<"stream">,
  ): Promise<KVNamespaceGetWithMetadataResult<ReadableStream, Metadata>>;
  getWithMetadata<Metadata = unknown>(
    key: Array<Key>,
    type: "text",
  ): Promise<Map<string, KVNamespaceGetWithMetadataResult<string, Metadata>>>;
  getWithMetadata<ExpectedValue = unknown, Metadata = unknown>(
    key: Array<Key>,
    type: "json",
  ): Promise<
    Map<string, KVNamespaceGetWithMetadataResult<ExpectedValue, Metadata>>
  >;
  getWithMetadata<Metadata = unknown>(
    key: Array<Key>,
    options?: Partial<KVNamespaceGetOptions<undefined>>,
  ): Promise<Map<string, KVNamespaceGetWithMetadataResult<string, Metadata>>>;
  getWithMetadata<Metadata = unknown>(
    key: Array<Key>,
    options?: KVNamespaceGetOptions<"text">,
  ): Promise<Map<string, KVNamespaceGetWithMetadataResult<string, Metadata>>>;
  getWithMetadata<ExpectedValue = unknown, Metadata = unknown>(
    key: Array<Key>,
    options?: KVNamespaceGetOptions<"json">,
  ): Promise<
    Map<string, KVNamespaceGetWithMetadataResult<ExpectedValue, Metadata>>
  >;
  delete(key: Key): Promise<void>;
}
interface KVNamespaceListOptions {
  limit?: number;
  prefix?: string | null;
  cursor?: string | null;
}
interface KVNamespaceGetOptions<Type> {
  type: Type;
  cacheTtl?: number;
}
interface KVNamespacePutOptions {
  expiration?: number;
  expirationTtl?: number;
  metadata?: any | null;
}
interface KVNamespaceGetWithMetadataResult<Value, Metadata> {
  value: Value | null;
  metadata: Metadata | null;
  cacheStatus: string | null;
}

declare var kv: KVNamespace[];
