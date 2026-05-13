import { describe, it, before } from "node:test";
import { loadPyodide, type PyodideInterface } from "pyodide";
import { convertToIR } from "../src/extract.js";
import { Renderer } from "../src/renderer.js";
import { makeProject } from "./helpers.js";

const INPUT_DTS = `
interface ItemResult {
  id: string;
  value: string;
  score?: number;
}

interface ListOptions {
  prefix?: string;
  limit?: number;
}

interface Store {
  get(key: string): Promise<string | null>;
  put(key: string, value: string): Promise<void>;
  delete(key: string): Promise<boolean>;
  list(options?: ListOptions): Promise<ItemResult[]>;
  getItem(key: string): Promise<ItemResult | null>;
}

declare var store: Store[];
`;

function generateWrapper(): { code: string; prelude: string } {
  const project = makeProject();
  project.createSourceFile("/fixture.d.ts", INPUT_DTS);
  const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);
  const renderer = new Renderer();
  return {
    code: renderer.renderFile(result.topLevels.ifaces),
    prelude: renderer.getPrelude(),
  };
}

function buildMockStore() {
  const data = new Map<string, string>([
    ["key1", "value1"],
    ["key2", "value2"],
    ["key3", "value3"],
  ]);

  return {
    get: async (key: string) => data.get(key) ?? null,
    put: async (key: string, value: string) => { data.set(key, value); },
    delete: async (key: string) => data.delete(key),
    list: async (options?: { prefix?: string; limit?: number }) => {
      let entries = [...data.entries()].map(([k, v], i) => ({
        id: k,
        value: v,
        score: i * 10,
      }));
      if (options?.prefix) {
        entries = entries.filter((e) => e.id.startsWith(options.prefix!));
      }
      if (options?.limit) {
        entries = entries.slice(0, options.limit);
      }
      return entries;
    },
    getItem: async (key: string) => {
      const v = data.get(key);
      if (v === undefined) return null;
      return { id: key, value: v, score: 42 };
    },
  };
}

function runPy(pyodide: PyodideInterface, code: string) {
  return pyodide.runPythonAsync(code);
}

describe("pyodide: generated wrappers run in real Pyodide", () => {
  let pyodide: PyodideInterface;

  before(async () => {
    const wrapper = generateWrapper();
    (globalThis as any).mockStore = buildMockStore();
    pyodide = await loadPyodide();
    pyodide.FS.writeFile("/home/pyodide/prelude.py", wrapper.prelude);
    pyodide.FS.writeFile("/home/pyodide/bindings.py", wrapper.code);

    await runPy(pyodide, `
import sys
sys.path.insert(0, "/home/pyodide")
from bindings import Store
import js
store = Store.from_js(js.mockStore)
`);
  });

  it("async get returns string", () =>
    runPy(pyodide, `assert await store.get("key1") == "value1"`));

  it("async get returns None for missing key", () =>
    runPy(pyodide, `assert await store.get("nonexistent") is None`));

  it("async put then get round-trip", () =>
    runPy(pyodide, `
await store.put("new-key", "new-value")
assert await store.get("new-key") == "new-value"
`));

  it("async delete returns bool", () =>
    runPy(pyodide, `
await store.put("to-delete", "bye")
assert await store.delete("to-delete") is True
`));

  it("list returns Python list of dicts", () =>
    runPy(pyodide, `
items = await store.list()
assert isinstance(items, list)
assert len(items) >= 3
assert items[0]["id"] == "key1"
assert items[0]["value"] == "value1"
assert isinstance(items[0]["score"], (int, float))
`));

  it("list with TypedDict options parameter", () =>
    runPy(pyodide, `
items = await store.list({"prefix": "key", "limit": 2})
assert len(items) == 2
`));

  it("getItem returns dict for existing key", () =>
    runPy(pyodide, `
item = await store.get_item("key1")
assert item is not None
assert item["id"] == "key1"
assert item["value"] == "value1"
assert item["score"] == 42
`));

  it("getItem returns None for missing key", () =>
    runPy(pyodide, `assert await store.get_item("missing") is None`));

  it("wrapper class equality", () =>
    runPy(pyodide, `
store2 = Store.from_js(js.mockStore)
assert store == store2
`));

  it("js_object returns JsProxy", () =>
    runPy(pyodide, `
from pyodide.ffi import JsProxy
assert isinstance(store.js_object, JsProxy)
`));
});
