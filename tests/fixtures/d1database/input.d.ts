interface D1Database {
    prepare(query: string): any;
    exec(query: string): Promise<any>;
    batch(statements: any[]): Promise<any[]>;
    dump(): Promise<any>;
}
declare var db: D1Database[];
