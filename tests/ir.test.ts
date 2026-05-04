import { describe, it } from "node:test";
import assert from "node:assert";
import { getTypeNode, typeToIR, makeProject } from "./helpers";
import { Converter } from "../src/astToIR.js";
import { SyntaxKind } from "ts-morph";
import { InterfaceIR, SigIR, typeParam } from "../src/ir.js";
import { convertToIR } from "../src/extract.js";

function typeToIRHelper(tsType: string) {
  const typeNode = getTypeNode(tsType);
  return typeToIR(typeNode);
}

function convertSource(source: string) {
  const project = makeProject();
  project.createSourceFile("/a.ts", source);
  const files = [project.getSourceFileOrThrow("/a.ts")];
  return convertToIR(files);
}

describe("typeToIR", () => {
  it("convert string", () => {
    const typeIR = typeToIRHelper("string");
    assert.deepStrictEqual(typeIR, { kind: "simple", text: "str" });
  });

  it("convert number", () => {
    const typeIR = typeToIRHelper("number");
    assert.deepStrictEqual(typeIR, { kind: "number" });
  });

  it("convert union", () => {
    const typeIR = typeToIRHelper("string | boolean");
    assert.deepStrictEqual(typeIR, {
      kind: "union",
      types: [
        { kind: "simple", text: "str" },
        { kind: "simple", text: "bool" },
      ],
    });
  });

  it("convert array", () => {
    const typeIR = typeToIRHelper("string[]");
    assert.deepStrictEqual(typeIR, {
      kind: "array",
      type: { kind: "simple", text: "str" },
    });
  });

  it("convert Promise", () => {
    const typeIR = typeToIRHelper("Promise<string>");
    assert.strictEqual(typeIR.kind, "reference");
    if (typeIR.kind === "reference") {
      assert.ok(typeIR.name.startsWith("Promise"));
      assert.strictEqual(typeIR.typeArgs.length, 1);
      assert.deepStrictEqual(typeIR.typeArgs[0], { kind: "simple", text: "str" });
    }
  });
});

describe("convertToIR", () => {
  it("converts a simple interface", () => {
    const result = convertSource(`
      interface KV {
        get(key: string): Promise<string | null>;
        put(key: string, value: string): Promise<void>;
        delete(key: string): Promise<void>;
      }
      declare var kv: KV[];
    `);

    const ifaces = result.topLevels.ifaces;
    const ifaceNames = ifaces.map((i) => i.name);

    const kvIface = ifaces.find((i) => i.name === "KV_iface");
    assert.ok(kvIface, `Expected 'KV_iface', got: ${ifaceNames.join(", ")}`);

    const methodNames = kvIface.methods
      .map((m) => m.name)
      .filter((n) => n !== "__call__");
    assert.ok(methodNames.includes("get"), "should have get method");
    assert.ok(methodNames.includes("put"), "should have put method");
    assert.ok(methodNames.includes("delete"), "should have delete method");

    const getMeth = kvIface.methods.find((m) => m.name === "get")!;
    assert.strictEqual(getMeth.signatures.length, 1);
    assert.strictEqual(getMeth.signatures[0].params.length, 1);
    assert.strictEqual(getMeth.signatures[0].params[0].name, "key");

    const returnType = getMeth.signatures[0].returns;
    assert.strictEqual(returnType.kind, "reference");
    if (returnType.kind === "reference") {
      assert.ok(returnType.name.startsWith("Promise"));
    }
  });

  it("converts overloaded methods", () => {
    const result = convertSource(`
      interface X {
        f(a: string): void;
        f(a: string, b: number): void;
      }
      declare var x: X[];
    `);

    const allNames = result.topLevels.ifaces.map((i) => i.name);
    const xIface = result.topLevels.ifaces.find((i) => i.name === "X_iface");
    assert.ok(xIface, `Expected X_iface, got: ${allNames.join(", ")}`);
    const fMeth = xIface.methods.find((m) => m.name === "f")!;
    assert.strictEqual(fMeth.signatures.length, 2);
  });

  it("converts properties", () => {
    const result = convertSource(`
      interface X {
        readonly name: string;
        count: number;
      }
      declare var x: X[];
    `);

    const allNames = result.topLevels.ifaces.map((i) => i.name);
    const xIface = result.topLevels.ifaces.find((i) => i.name === "X_iface");
    assert.ok(xIface, `Expected X_iface, got: ${allNames.join(", ")}`);
    assert.strictEqual(xIface.properties.length, 2);

    const nameProp = xIface.properties.find((p) => p.name === "name")!;
    assert.strictEqual(nameProp.isReadonly, true);

    const countProp = xIface.properties.find((p) => p.name === "count")!;
    assert.strictEqual(countProp.isReadonly, false);
  });

  it("IR is JSON-serializable", () => {
    const result = convertSource(`
      interface KV {
        get(key: string): Promise<string | null>;
      }
      declare var kv: KV;
    `);

    const json = JSON.stringify(result, null, 2);
    const parsed = JSON.parse(json);
    assert.ok(parsed.topLevels);
    assert.ok(parsed.topLevels.ifaces.length > 0);
  });
});
