import { describe, it } from "node:test";
import { execSync } from "child_process";
import { writeFileSync, mkdtempSync, rmSync, readFileSync } from "fs";
import { resolve, join } from "path";
import { tmpdir } from "os";
import { Renderer } from "../src/renderer.js";
import {
  FIXTURE_NAMES,
  FIXTURES_DIR,
  irInterface,
  irMethod,
  irSig,
  irSigWithSpread,
  irSigWithKwparams,
  irParam,
  irProperty,
  promiseOf,
  callableType,
  refType,
} from "./helpers.js";

const renderer = new Renderer();

function checkTy(code: string): void {
  const dir = mkdtempSync(join(tmpdir(), "ty-test-"));
  const file = join(dir, "test.py");
  try {
    writeFileSync(file, code);
    execSync(
      `uvx --with pyodide-py==0.28.2 --python 3.13 ty check ${file}`,
      { encoding: "utf-8", timeout: 30_000 },
    );
  } catch (e: any) {
    const stdout = e.stdout ?? "";
    throw new Error(
      `ty check failed:\n${stdout}\n\n--- generated code ---\n${code}`,
    );
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

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
