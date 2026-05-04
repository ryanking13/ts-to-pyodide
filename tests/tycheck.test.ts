import { describe, it } from "node:test";
import { execSync } from "child_process";
import { writeFileSync, mkdtempSync, rmSync, readFileSync } from "fs";
import { resolve, join } from "path";
import { tmpdir } from "os";
import { Renderer } from "../src/renderer.js";
import { InterfaceIR, CallableIR, SigIR, ParamIR, PropertyIR, TypeIR } from "../src/ir.js";

const VENV_PATH = resolve(import.meta.dirname!, "..", ".venv-ty");

const renderer = new Renderer();

function checkTy(code: string): void {
  const dir = mkdtempSync(join(tmpdir(), "ty-test-"));
  const file = join(dir, "test.py");
  try {
    writeFileSync(file, code);
    execSync(`ty check --python ${VENV_PATH} ${file}`, {
      encoding: "utf-8",
      timeout: 15_000,
    });
  } catch (e: any) {
    const stdout = e.stdout ?? "";
    throw new Error(
      `ty check failed:\n${stdout}\n\n--- generated code ---\n${code}`,
    );
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

const FIXTURES_DIR = resolve(import.meta.dirname!, "fixtures");

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
  "buffer_types",
  "kwparams",
  "get_accessor",
];

describe("ty type-check fixtures", () => {
  for (const name of FIXTURE_NAMES) {
    it(name, () => {
      const ir = JSON.parse(
        readFileSync(resolve(FIXTURES_DIR, name, "ir.json"), "utf-8"),
      );
      checkTy(renderer.renderFile([ir]));
    });
  }
});

function irInterface(name: string, methods: CallableIR[] = [], properties: PropertyIR[] = []): InterfaceIR {
  return { kind: "interface", name, methods, properties, typeParams: [], bases: [] };
}
function irMethod(name: string, signatures: SigIR[] = []): CallableIR {
  return { kind: "callable", name, signatures, isStatic: false };
}
function irSig(params: ParamIR[] = [], returns: TypeIR = { kind: "simple", text: "None" }): SigIR {
  return { params, returns };
}
function irSigWithSpread(params: ParamIR[], spreadParam: ParamIR, returns: TypeIR = { kind: "simple", text: "None" }): SigIR {
  return { params, spreadParam, returns };
}
function irParam(name: string, type: TypeIR, isOptional = false): ParamIR {
  return { name, type, isOptional };
}
function irProperty(name: string, type: TypeIR, isReadonly = false, isOptional = false): PropertyIR {
  return { name, type, isReadonly, isOptional, isStatic: false };
}
function promiseOf(inner: TypeIR): TypeIR {
  return { kind: "reference", name: "Promise", typeArgs: [inner] };
}
function callableType(params: ParamIR[] = [], returns: TypeIR = { kind: "simple", text: "None" }): TypeIR {
  return { kind: "callable", signatures: [irSig(params, returns)] };
}

function refType(name: string): TypeIR {
  return { kind: "reference", name, typeArgs: [] };
}

describe("ty type-check sub-binding wrapping", () => {
  it("method returning known interface (forward reference)", () => {
    checkTy(renderer.renderFile([
      irInterface("DB_iface", [
        irMethod("prepare", [irSig(
          [irParam("query", { kind: "simple", text: "str" })],
          refType("Stmt_iface"),
        )]),
      ]),
      irInterface("Stmt_iface", [
        irMethod("run", [irSig([], promiseOf({ kind: "simple", text: "Any" }))]),
      ]),
    ]));
  });

  it("property typed as known interface", () => {
    checkTy(renderer.renderFile([
      irInterface("Videos_iface", [
        irMethod("list", [irSig([], promiseOf({ kind: "simple", text: "Any" }))]),
      ]),
      irInterface("Binding_iface", [], [
        irProperty("videos", refType("Videos_iface"), true),
      ]),
    ]));
  });
});

function irSigWithKwparams(
  params: ParamIR[],
  kwparams: ParamIR[],
  returns: TypeIR = { kind: "simple", text: "None" },
): SigIR {
  return { params, kwparams, returns };
}

describe("ty type-check kwparams", () => {
  it("kwparams method with dict building", () => {
    checkTy(renderer.renderFile([
      irInterface("KV_iface", [
        irMethod("put", [
          irSigWithKwparams(
            [
              irParam("key", { kind: "simple", text: "str" }),
              irParam("value", { kind: "simple", text: "str" }),
            ],
            [
              irParam("expiration", { kind: "number" }, true),
              irParam("metadata", { kind: "simple", text: "Any" }, true),
            ],
            promiseOf({ kind: "simple", text: "None" }),
          ),
        ]),
      ]),
    ]));
  });
});

describe("ty type-check inline cases", () => {
  it("arg conversion with array param", () => {
    checkTy(renderer.renderFile([
      irInterface("D1_iface", [
        irMethod("batch", [irSig([
          irParam("statements", { kind: "array", type: { kind: "simple", text: "Any" } }),
        ], promiseOf({ kind: "simple", text: "Any" }))])
      ]),
    ]));
  });

  it("create_proxy", () => {
    checkTy(renderer.renderFile([
      irInterface("State_iface", [
        irMethod("blockConcurrencyWhile", [irSig([
          irParam("callback", callableType([], promiseOf({ kind: "simple", text: "Any" }))),
        ], promiseOf({ kind: "simple", text: "Any" }))])
      ]),
    ]));
  });

  it("rest params", () => {
    checkTy(renderer.renderFile([
      irInterface("Stmt_iface", [
        irMethod("bind", [irSigWithSpread(
          [],
          irParam("values", { kind: "simple", text: "Any" }),
          { kind: "simple", text: "Any" },
        )])
      ]),
    ]));
  });

  it("reserved word property", () => {
    checkTy(renderer.renderFile([
      irInterface("Email_iface", [], [
        irProperty("from", { kind: "simple", text: "str" }, true),
      ]),
    ]));
  });

  it("writable property", () => {
    checkTy(renderer.renderFile([
      irInterface("Config_iface", [], [
        irProperty("name", { kind: "simple", text: "str" }),
      ]),
    ]));
  });
});
