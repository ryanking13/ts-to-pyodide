import { describe, it, before, after } from "node:test";
import assert from "node:assert";
import { execSync, execFileSync } from "child_process";
import { writeFileSync, readFileSync, rmSync, mkdtempSync } from "fs";
import { join, resolve } from "path";
import { tmpdir } from "os";

const RUN_INTEGRATION =
  process.env["INTEGRATION_TEST"] === "1" || process.env["CI"] === "true";

const PROJECT_ROOT = resolve(import.meta.dirname!, "..");

describe("integration: @cloudflare/workers-types", { skip: !RUN_INTEGRATION }, () => {
  let projectDir: string;
  let outputFile: string;

  before(() => {
    projectDir = mkdtempSync(join(tmpdir(), "cf-integration-"));
    outputFile = join(projectDir, "output.py");

    writeFileSync(
      join(projectDir, "package.json"),
      JSON.stringify({
        name: "cf-integration-test",
        private: true,
        dependencies: {
          "@cloudflare/workers-types": "*",
          // TODO: pinned to 5.3.x because the forked IR extractor (astToIR/astUtils)
          // crashes on TS 5.9+ lib files (Uint8Array gains type params without defaults).
          typescript: "~5.3.0",
        },
      }),
    );

    writeFileSync(
      join(projectDir, "tsconfig.json"),
      JSON.stringify({
        compilerOptions: {
          target: "esnext",
          module: "esnext",
          moduleResolution: "nodenext",
          lib: ["esnext"],
          types: ["@cloudflare/workers-types"],
        },
        include: ["types.d.ts"],
      }),
    );

    execSync("npm install --ignore-scripts", {
      cwd: projectDir,
      stdio: "pipe",
      timeout: 60_000,
    });

    const typesPath = join(
      projectDir,
      "node_modules/@cloudflare/workers-types/index.d.ts",
    );
    const types = readFileSync(typesPath, "utf-8");
    writeFileSync(join(projectDir, "types.d.ts"), types);
  });

  after(() => {
    rmSync(projectDir, { recursive: true, force: true });
  });

  it("generates valid Python with classes and methods", () => {
    const stdout = execFileSync(
      "npx",
      ["tsx", join(PROJECT_ROOT, "src/main.ts"), "render", projectDir, outputFile],
      {
        cwd: PROJECT_ROOT,
        encoding: "utf-8",
        timeout: 60_000,
      },
    );

    assert.match(stdout, /Generated \d+ classes/);
    const classCount = parseInt(stdout.match(/Generated (\d+) classes/)![1]);
    assert.ok(classCount > 100, `expected >100 classes, got ${classCount}`);
  });

  it("generates syntactically valid Python", () => {
    const content = readFileSync(outputFile, "utf-8");
    assert.ok(content.length > 0, "output file should not be empty");

    const result = execSync(
      `uvx --python 3.13 python -c "import ast; ast.parse(open('${outputFile}').read()); print('VALID')"`,
      { encoding: "utf-8", timeout: 15_000 },
    );
    assert.match(result, /VALID/);
  });
});
