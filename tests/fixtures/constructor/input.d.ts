declare class Headers {
    constructor();
    get(name: string): string | null;
    set(name: string, value: string): void;
    has(name: string): boolean;
    delete(name: string): void;
}
