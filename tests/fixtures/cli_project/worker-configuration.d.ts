interface KVNamespace_iface {
    get(key: string): Promise<string | null>;
    put(key: string, value: string): Promise<void>;
    delete(key: string): Promise<void>;
}

declare var KVNamespace: KVNamespace_iface;
