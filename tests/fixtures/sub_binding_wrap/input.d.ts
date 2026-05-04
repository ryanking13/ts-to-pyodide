interface D1PreparedStatement {
    first(colName?: string): Promise<any>;
    run(): Promise<any>;
    all(): Promise<any>;
}

interface D1Database {
    prepare(query: string): D1PreparedStatement;
    exec(query: string): Promise<any>;
}

declare var db: D1Database[];
