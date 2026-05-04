interface Videos {
    list(): Promise<any>;
}
interface Binding {
    videos: Videos;
    readonly name: string;
    fetch(url: string): Promise<any>;
}
declare var b: Binding[];
