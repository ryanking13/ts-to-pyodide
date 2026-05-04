interface KVPutOptions {
    expiration?: number;
    expirationTtl?: number;
    metadata?: any;
}

interface KVStore {
    put(key: string, value: string, options?: KVPutOptions): Promise<void>;
    get(key: string): Promise<string | null>;
}

declare var kv: KVStore[];
