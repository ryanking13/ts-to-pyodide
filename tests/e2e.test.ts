import { describe, it } from "node:test";
import assert from "node:assert";
import { readFileSync } from "fs";
import { resolve } from "path";
import { FIXTURE_NAMES, FIXTURES_DIR, makeProject } from "./helpers.js";
import { convertToIR } from "../src/extract.js";
import { Renderer } from "../src/renderer.js";
import { InterfaceIR } from "../src/ir.js";

const renderer = new Renderer();

function loadFixture(name: string) {
  const dir = resolve(FIXTURES_DIR, name);
  const inputDts = readFileSync(resolve(dir, "input.d.ts"), "utf-8");
  const expectedIR = JSON.parse(
    readFileSync(resolve(dir, "ir.json"), "utf-8"),
  ) as InterfaceIR;
  const expectedPy = readFileSync(resolve(dir, "expected.py"), "utf-8");
  return { inputDts, expectedIR, expectedPy };
}

function findIface(
  result: ReturnType<typeof convertToIR>,
  irName: string,
): InterfaceIR {
  const iface = result.topLevels.ifaces.find((i) => i.name === irName);
  if (!iface) {
    const names = result.topLevels.ifaces.map((i) => i.name).join(", ");
    throw new Error(`${irName} not found. Available: ${names}`);
  }
  return iface;
}

describe("e2e: .d.ts → IR (fixture validation)", () => {
  for (const name of FIXTURE_NAMES) {
    it(name, () => {
      const { inputDts, expectedIR } = loadFixture(name);

      const project = makeProject();
      project.createSourceFile("/fixture.d.ts", inputDts);
      const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);

      const iface = findIface(result, expectedIR.name);

      const expectedMethods = expectedIR.methods
        .filter((m) => m.name !== "__call__")
        .map((m) => m.name);
      const actualMethods = iface.methods
        .filter((m) => m.name !== "__call__" && !m.name!.startsWith("__"))
        .map((m) => m.name);

      for (const method of expectedMethods) {
        assert.ok(
          actualMethods.includes(method),
          `Missing method ${method} in IR for ${name}. Got: ${actualMethods.join(", ")}`,
        );
      }

      for (const prop of expectedIR.properties) {
        const found = iface.properties.find((p) => p.name === prop.name);
        assert.ok(found, `Missing property ${prop.name} in IR for ${name}`);
        assert.strictEqual(found.isReadonly, prop.isReadonly);
      }
    });
  }
});

describe("e2e: .d.ts → IR → Python (full pipeline)", () => {
  for (const name of FIXTURE_NAMES) {
    it(name, () => {
      const { inputDts, expectedIR, expectedPy } = loadFixture(name);

      const project = makeProject();
      project.createSourceFile("/fixture.d.ts", inputDts);
      const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);
      const iface = findIface(result, expectedIR.name);

      const rendered = renderer.renderInterface(iface);
      for (const line of expectedPy.split("\n")) {
        if (line.trim()) {
          assert.ok(
            rendered.includes(line),
            `Missing line in rendered output for ${name}:\n  expected: ${line}\n  got:\n${rendered}`,
          );
        }
      }
    });
  }
});

describe("e2e: sub-binding wrapping (.d.ts → IR → renderFile)", () => {
  it("sub_binding_wrap: method returning known interface wraps with class constructor", () => {
    const inputDts = readFileSync(
      resolve(FIXTURES_DIR, "sub_binding_wrap", "input.d.ts"),
      "utf-8",
    );
    const expectedPy = readFileSync(
      resolve(FIXTURES_DIR, "sub_binding_wrap", "expected.py"),
      "utf-8",
    );

    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", inputDts);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);

    const output = renderer.renderFile(result.topLevels.ifaces);
    assert.strictEqual(output, expectedPy);
  });
});

describe("e2e: R2 bucket (.d.ts → IR → renderFile)", () => {
  it("r2_bucket: binding interface with declare class, sub-binding wrapping, kwparams", () => {
    const inputDts = readFileSync(
      resolve(FIXTURES_DIR, "r2_bucket", "input.d.ts"),
      "utf-8",
    );
    const expectedPy = readFileSync(
      resolve(FIXTURES_DIR, "r2_bucket", "expected.py"),
      "utf-8",
    );

    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", inputDts);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);

    const output = renderer.renderFile(result.topLevels.ifaces);
    assert.strictEqual(output, expectedPy);
  });
});

describe("e2e: constructor (.d.ts → IR → renderFile)", () => {
  it("constructor: declare class with constructor produces __init__", () => {
    const inputDts = readFileSync(
      resolve(FIXTURES_DIR, "constructor", "input.d.ts"),
      "utf-8",
    );
    const expectedPy = readFileSync(
      resolve(FIXTURES_DIR, "constructor", "expected.py"),
      "utf-8",
    );

    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", inputDts);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);

    const output = renderer.renderFile(result.topLevels.ifaces);
    assert.strictEqual(output, expectedPy);
  });
});

describe("e2e: declare module extraction (.d.ts → IR → renderFile)", () => {
  it("declare_module: class from declare module + top-level interface", () => {
    const inputDts = readFileSync(
      resolve(FIXTURES_DIR, "declare_module", "input.d.ts"),
      "utf-8",
    );
    const expectedPy = readFileSync(
      resolve(FIXTURES_DIR, "declare_module", "expected.py"),
      "utf-8",
    );

    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", inputDts);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);

    const output = renderer.renderFile(result.topLevels.ifaces);
    assert.strictEqual(output, expectedPy);
  });
});

describe("e2e: get accessors", () => {
  it("get accessors are extracted as readonly properties", () => {
    const inputDts = readFileSync(
      resolve(FIXTURES_DIR, "get_accessor", "input.d.ts"),
      "utf-8",
    );

    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", inputDts);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);
    const iface = findIface(result, "ObjectBody_iface");

    const propNames = iface.properties.map((p) => p.name);
    assert.ok(propNames.includes("body"), "get body() should be extracted");
    assert.ok(propNames.includes("bodyUsed"), "get bodyUsed() should be extracted");
    assert.ok(propNames.includes("etag"), "readonly etag should be present");

    const bodyProp = iface.properties.find((p) => p.name === "body")!;
    assert.strictEqual(bodyProp.isReadonly, true, "get-only accessor should be readonly");
  });

  it("get + set accessor pair produces writable property", () => {
    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", `
      interface Config {
          get value(): string;
          set value(v: string);
          get name(): string;
      }
      declare var c: Config[];
    `);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);
    const iface = findIface(result, "Config_iface");

    const valueProp = iface.properties.find((p) => p.name === "value")!;
    assert.ok(valueProp, "get/set value should be extracted");
    assert.strictEqual(valueProp.isReadonly, false, "get+set should be writable");

    const nameProp = iface.properties.find((p) => p.name === "name")!;
    assert.ok(nameProp, "get-only name should be extracted");
    assert.strictEqual(nameProp.isReadonly, true, "get-only should be readonly");
  });
});

describe("e2e: declare module extraction", () => {
  it("extracts classes from declare module blocks", () => {
    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", `
      declare module "my:module" {
          class MyService {
              fetch(url: string): Promise<any>;
          }
      }
    `);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);
    const iface = result.topLevels.ifaces.find(
      (i) => i.name === "MyService" || i.name === "MyService_iface",
    );
    assert.ok(iface, "class from declare module should be extracted");
  });

  it("ignores unquoted namespace blocks", () => {
    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", `
      namespace Internal {
          class Hidden {
              run(): void;
          }
      }
      interface Visible {
          go(): void;
      }
      declare var v: Visible[];
    `);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);
    const names = result.topLevels.ifaces.map((i) => i.name);
    assert.ok(!names.some((n) => n.includes("Hidden")), "unquoted namespace contents should not be extracted");
    assert.ok(names.some((n) => n.includes("Visible")), "top-level interface should be extracted");
  });
});

describe("e2e: constructor support", () => {
  it("declare class with constructor produces __init__ via renderFile", () => {
    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", `
      declare class HTMLRewriter {
          constructor();
          on(selector: string, handler: any): HTMLRewriter;
      }
    `);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);
    const output = renderer.renderFile(result.topLevels.ifaces);

    assert.ok(output.includes("class HTMLRewriter:"));
    assert.ok(output.includes("def __init__(self, *args: Any, **kwargs: Any) -> None:"));
    assert.ok(output.includes("self._binding = js.HTMLRewriter.new(*args, **kwargs)"));
    assert.ok(output.includes("def from_js(cls, js_obj: JsProxy) -> HTMLRewriter:"));
    assert.ok(output.includes("def on(self"));
  });

  it("declare class without constructor has no __init__", () => {
    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", `
      declare class MyService {
          fetch(url: string): Promise<any>;
      }
    `);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);
    const output = renderer.renderFile(result.topLevels.ifaces);

    assert.ok(output.includes("class MyService:"));
    assert.ok(!output.includes("def __init__"));
    assert.ok(output.includes("def from_js(cls, js_obj: JsProxy) -> MyService:"));
  });

  it("declare class with parameterized constructor", () => {
    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", `
      declare class Request {
          constructor(input: string, init?: any);
          readonly url: string;
      }
    `);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);
    const output = renderer.renderFile(result.topLevels.ifaces);

    assert.ok(output.includes("class Request:"));
    assert.ok(output.includes("def __init__(self, *args: Any, **kwargs: Any) -> None:"));
    assert.ok(output.includes("self._binding = js.Request.new(*args, **kwargs)"));
    assert.ok(output.includes("def url(self) -> str:"));
  });

  it("interface (not declare class) has no __init__", () => {
    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", `
      interface KVNamespace {
          get(key: string): Promise<string | null>;
      }
      declare var kv: KVNamespace[];
    `);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);
    const output = renderer.renderFile(result.topLevels.ifaces);

    assert.ok(output.includes("class KVNamespace:"));
    assert.ok(!output.includes("def __init__"));
    assert.ok(output.includes("def from_js(cls, js_obj: JsProxy) -> KVNamespace:"));
  });

  // TODO: non-global constructors from declare module blocks will fail at runtime
  // because js.ClassName only works for globalThis-scoped types.
  it("declare class in declare module gets constructor with TODO caveat", () => {
    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", `
      declare module "my:module" {
          class MyWorker {
              constructor(env: any);
              fetch(url: string): Promise<any>;
          }
      }
    `);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);
    const output = renderer.renderFile(result.topLevels.ifaces);

    assert.ok(output.includes("class MyWorker:"));
    assert.ok(output.includes("def __init__(self, *args: Any, **kwargs: Any) -> None:"));
    assert.ok(output.includes("js.MyWorker.new(*args, **kwargs)"));
    assert.ok(output.includes("def from_js(cls, js_obj: JsProxy) -> MyWorker:"));
  });
});
