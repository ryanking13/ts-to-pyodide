interface Pipeline {
    send(records: any[]): Promise<void>;
}

declare module "my:pipelines" {
    class PipelineEntrypoint {
        run(records: any[]): Promise<any[]>;
    }
}

declare var p: Pipeline[];
