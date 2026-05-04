interface ObjectBody {
    get body(): string;
    get bodyUsed(): boolean;
    readonly etag: string;
    text(): Promise<string>;
}
declare var o: ObjectBody[];
