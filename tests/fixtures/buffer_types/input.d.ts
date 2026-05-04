interface CryptoHelper {
    digest(data: ArrayBuffer): Promise<ArrayBuffer>;
    encode(input: string): Uint8Array;
    readonly raw: ArrayBuffer;
}
declare var c: CryptoHelper[];
