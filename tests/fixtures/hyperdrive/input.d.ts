interface Hyperdrive {
    readonly connectionString: string;
    readonly host: string;
    readonly port: number;
    readonly user: string;
    readonly password: string;
    readonly database: string;
    connect(): any;
}
declare var h: Hyperdrive[];
