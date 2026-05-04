import { describe, it } from "node:test";
import assert from "node:assert";
import { readFileSync, existsSync } from "fs";
import { resolve } from "path";
import { makeProject } from "./helpers.js";
import { convertToIR } from "../src/extract.js";
import { Renderer } from "../src/renderer.js";
import { InterfaceIR } from "../src/ir.js";

const FIXTURES_DIR = resolve(import.meta.dirname!, "fixtures");
const renderer = new Renderer();

const FIXTURE_NAMES = [
  "sync_method",
  "greeter",
  "math_params",
  "async_delete",
  "readonly_properties",
  "d1database",
  "hyperdrive",
  "overloads",
  "generic_method",
  "sub_binding_property",
];

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

describe("e2e: IR → Python (fixture validation)", () => {
  for (const name of FIXTURE_NAMES) {
    it(name, () => {
      const { expectedIR, expectedPy } = loadFixture(name);
      const result = renderer.renderInterface(expectedIR);
      assert.strictEqual(result, expectedPy);
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

describe("e2e: known IR gaps", () => {
  it("get accessors are dropped from IR (known limitation)", () => {
    const inputDts = readFileSync(
      resolve(FIXTURES_DIR, "get_accessor", "input.d.ts"),
      "utf-8",
    );

    const project = makeProject();
    project.createSourceFile("/fixture.d.ts", inputDts);
    const result = convertToIR([project.getSourceFileOrThrow("/fixture.d.ts")]);
    const iface = findIface(result, "ObjectBody_iface");

    const propNames = iface.properties.map((p) => p.name);
    assert.ok(
      !propNames.includes("body"),
      "get body() is missing from IR (known gap — GetAccessor not handled by astToIR)",
    );
    assert.ok(propNames.includes("etag"), "readonly etag should be present");
  });
});
