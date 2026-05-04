import { describe, it, before, after } from "node:test";
import assert from "node:assert";
import { execFileSync } from "child_process";
import { readFileSync, rmSync, mkdirSync, symlinkSync, unlinkSync, existsSync } from "fs";
import { resolve, join } from "path";

const PROJECT_ROOT = resolve(import.meta.dirname!, "..");
const FIXTURE_DIR = resolve(import.meta.dirname!, "fixtures/cli_project");
const TMP_DIR = join(PROJECT_ROOT, ".test-output");

function runCli(...args: string[]): string {
  return execFileSync("npx", ["tsx", "src/main.ts", ...args], {
    cwd: PROJECT_ROOT,
    encoding: "utf-8",
    timeout: 30_000,
  });
}

describe("CLI", () => {
  before(() => {
    mkdirSync(TMP_DIR, { recursive: true });
    // Fixture needs node_modules/typescript/lib for ts-morph — symlink from project root
    const fixtureNodeModules = join(FIXTURE_DIR, "node_modules");
    if (!existsSync(fixtureNodeModules)) {
      symlinkSync(
        join(PROJECT_ROOT, "node_modules"),
        fixtureNodeModules,
      );
    }
  });

  after(() => {
    rmSync(TMP_DIR, { recursive: true, force: true });
    const link = join(FIXTURE_DIR, "node_modules");
    if (existsSync(link)) unlinkSync(link);
  });

  describe("render subcommand", () => {
    it("writes a .py file with prelude and classes", () => {
      const outFile = join(TMP_DIR, "render-test.py");
      const stdout = runCli("render", FIXTURE_DIR, outFile);

      assert.match(stdout, /Generated \d+ classes/);

      const content = readFileSync(outFile, "utf-8");
      assert.match(content, /from typing import Any, overload/);
      assert.match(content, /from pyodide\.ffi import JsBuffer, JsProxy/);
      assert.match(content, /def _jsnull_to_none/);
      assert.ok(content.includes("class KVNamespace:"), "expected class KVNamespace in output");
      assert.ok(content.includes("def __init__(self, binding: JsProxy)"), "expected __init__ in output");
    });
  });

  describe("ir subcommand", () => {
    it("writes a JSON file with topLevels", () => {
      const outFile = join(TMP_DIR, "ir-test.json");
      const stdout = runCli("ir", FIXTURE_DIR, outFile);

      assert.match(stdout, /IR written to/);

      const content = JSON.parse(readFileSync(outFile, "utf-8"));
      assert.ok(content.topLevels);
      assert.ok(Array.isArray(content.topLevels.ifaces));
      assert.ok(content.topLevels.ifaces.length > 0);
    });
  });

  describe("default subcommand", () => {
    it("defaults to render when no subcommand given", () => {
      const outFile = join(TMP_DIR, "default-test.py");
      const stdout = runCli(FIXTURE_DIR, outFile);

      assert.match(stdout, /Generated \d+ classes/);

      const content = readFileSync(outFile, "utf-8");
      assert.ok(content.includes("class KVNamespace:"));
    });
  });

  describe("help", () => {
    it("shows usage when no args given", () => {
      const stdout = runCli();
      assert.match(stdout, /Usage:/);
      assert.match(stdout, /render/);
      assert.match(stdout, /ir/);
    });
  });
});
