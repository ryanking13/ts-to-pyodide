// Copied from @cloudflare/workers-types@4.20260506.1 index.d.ts lines 2305-2385
type QueueContentType = "text" | "bytes" | "json" | "v8";
interface Queue<Body = unknown> {
  metrics(): Promise<QueueMetrics>;
  send(message: Body, options?: QueueSendOptions): Promise<QueueSendResponse>;
  sendBatch(
    messages: Iterable<MessageSendRequest<Body>>,
    options?: QueueSendBatchOptions,
  ): Promise<QueueSendBatchResponse>;
}
interface QueueSendMetrics {
  backlogCount: number;
  backlogBytes: number;
  oldestMessageTimestamp?: Date;
}
interface QueueSendMetadata {
  metrics: QueueSendMetrics;
}
interface QueueSendResponse {
  metadata: QueueSendMetadata;
}
interface QueueSendBatchMetrics {
  backlogCount: number;
  backlogBytes: number;
  oldestMessageTimestamp?: Date;
}
interface QueueSendBatchMetadata {
  metrics: QueueSendBatchMetrics;
}
interface QueueSendBatchResponse {
  metadata: QueueSendBatchMetadata;
}
interface QueueSendOptions {
  contentType?: QueueContentType;
  delaySeconds?: number;
}
interface QueueSendBatchOptions {
  delaySeconds?: number;
}
interface MessageSendRequest<Body = unknown> {
  body: Body;
  contentType?: QueueContentType;
  delaySeconds?: number;
}
interface QueueMetrics {
  backlogCount: number;
  backlogBytes: number;
  oldestMessageTimestamp?: Date;
}
interface MessageBatchMetrics {
  backlogCount: number;
  backlogBytes: number;
  oldestMessageTimestamp?: Date;
}
interface MessageBatchMetadata {
  metrics: MessageBatchMetrics;
}
interface QueueRetryOptions {
  delaySeconds?: number;
}
interface Message<Body = unknown> {
  readonly id: string;
  readonly timestamp: Date;
  readonly body: Body;
  readonly attempts: number;
  retry(options?: QueueRetryOptions): void;
  ack(): void;
}
interface MessageBatch<Body = unknown> {
  readonly messages: readonly Message<Body>[];
  readonly queue: string;
  readonly metadata: MessageBatchMetadata;
  retryAll(options?: QueueRetryOptions): void;
  ackAll(): void;
}

declare var queue: Queue[];
declare var batch: MessageBatch[];
