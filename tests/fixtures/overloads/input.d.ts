interface D1PreparedStatement {
    first(colName: string): Promise<any | null>;
    first(): Promise<any | null>;
}
declare var stmt: D1PreparedStatement[];
