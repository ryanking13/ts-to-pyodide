// Copied from @cloudflare/workers-types@4.20260506.1 latest/index.d.ts lines 14830-15090
type VectorFloatArray = Float32Array | Float64Array;

type VectorizeMetadataRetrievalLevel = "all" | "indexed" | "none";

interface VectorizeQueryOptions {
  topK?: number;
  namespace?: string;
  returnValues?: boolean;
  returnMetadata?: boolean | VectorizeMetadataRetrievalLevel;
  filter?: Record<string, any>;
}

interface VectorizeIndexInfo {
  vectorCount: number;
  dimensions: number;
  processedUpToDatetime: number;
  processedUpToMutation: number;
}

interface VectorizeVector {
  id: string;
  values: VectorFloatArray | number[];
  namespace?: string;
  metadata?: Record<string, any>;
}

interface VectorizeMatch {
  id: string;
  values?: VectorFloatArray | number[];
  namespace?: string;
  metadata?: Record<string, any>;
  score: number;
}

interface VectorizeMatches {
  matches: VectorizeMatch[];
  count: number;
}

interface VectorizeAsyncMutation {
  mutationId: string;
}

declare abstract class Vectorize {
  public describe(): Promise<VectorizeIndexInfo>;
  public query(
    vector: VectorFloatArray | number[],
    options?: VectorizeQueryOptions,
  ): Promise<VectorizeMatches>;
  public queryById(
    vectorId: string,
    options?: VectorizeQueryOptions,
  ): Promise<VectorizeMatches>;
  public insert(vectors: VectorizeVector[]): Promise<VectorizeAsyncMutation>;
  public upsert(vectors: VectorizeVector[]): Promise<VectorizeAsyncMutation>;
  public deleteByIds(ids: string[]): Promise<VectorizeAsyncMutation>;
  public getByIds(ids: string[]): Promise<VectorizeVector[]>;
}

declare var vectorize: Vectorize[];
