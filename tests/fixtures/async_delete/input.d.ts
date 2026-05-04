interface KV {
    delete(key: string): Promise<void>;
}
declare var kv: KV[];
