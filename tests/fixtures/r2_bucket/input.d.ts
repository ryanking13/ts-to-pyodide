// Adapted from @cloudflare/workers-types R2 types

interface R2ListOptions {
    limit?: number;
    prefix?: string;
    cursor?: string;
    delimiter?: string;
    startAfter?: string;
}

interface R2Conditional {
    etagMatches?: string;
    etagDoesNotMatch?: string;
    uploadedBefore?: Date;
    uploadedAfter?: Date;
    secondsGranularity?: boolean;
}

interface R2GetOptions {
    onlyIf?: R2Conditional | Headers;
    range?: Headers;
    ssecKey?: ArrayBuffer | string;
}

interface R2PutOptions {
    onlyIf?: R2Conditional | Headers;
    httpMetadata?: R2HTTPMetadata | Headers;
    customMetadata?: Record<string, string>;
    md5?: ArrayBuffer | string;
    sha256?: ArrayBuffer | string;
    storageClass?: string;
    ssecKey?: ArrayBuffer | string;
}

interface R2MultipartOptions {
    httpMetadata?: R2HTTPMetadata | Headers;
    customMetadata?: Record<string, string>;
    storageClass?: string;
}

interface R2HTTPMetadata {
    contentType?: string;
    contentLanguage?: string;
    contentDisposition?: string;
    contentEncoding?: string;
    cacheControl?: string;
}

interface R2Checksums {
    readonly md5?: ArrayBuffer;
    readonly sha1?: ArrayBuffer;
    readonly sha256?: ArrayBuffer;
    toJSON(): R2StringChecksums;
}

interface R2StringChecksums {
    md5?: string;
    sha1?: string;
    sha256?: string;
}

interface R2UploadedPart {
    partNumber: number;
    etag: string;
}

declare abstract class R2Object {
    readonly key: string;
    readonly version: string;
    readonly size: number;
    readonly etag: string;
    readonly httpEtag: string;
    readonly checksums: R2Checksums;
    readonly uploaded: Date;
    readonly httpMetadata?: R2HTTPMetadata;
    readonly customMetadata?: Record<string, string>;
    readonly storageClass: string;
    writeHttpMetadata(headers: Headers): void;
}

interface R2ObjectBody extends R2Object {
    get body(): ReadableStream;
    get bodyUsed(): boolean;
    arrayBuffer(): Promise<ArrayBuffer>;
    text(): Promise<string>;
    json(): Promise<any>;
    blob(): Promise<Blob>;
}

interface R2MultipartUpload {
    readonly key: string;
    readonly uploadId: string;
    uploadPart(
        partNumber: number,
        value: ReadableStream | ArrayBuffer | string | Blob,
    ): Promise<R2UploadedPart>;
    abort(): Promise<void>;
    complete(uploadedParts: R2UploadedPart[]): Promise<R2Object>;
}

interface R2Bucket {
    head(key: string): Promise<R2Object | null>;
    get(key: string, options?: R2GetOptions): Promise<R2ObjectBody | null>;
    put(
        key: string,
        value: ReadableStream | ArrayBuffer | string | null | Blob,
        options?: R2PutOptions,
    ): Promise<R2Object>;
    createMultipartUpload(
        key: string,
        options?: R2MultipartOptions,
    ): Promise<R2MultipartUpload>;
    resumeMultipartUpload(key: string, uploadId: string): R2MultipartUpload;
    delete(keys: string | string[]): Promise<void>;
    list(options?: R2ListOptions): Promise<any>;
}

declare var bucket: R2Bucket[];
