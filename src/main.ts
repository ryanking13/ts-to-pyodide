#!/usr/bin/env node
import { Project } from "ts-morph";
import { convertToIR } from "./extract.js";
import { Renderer } from "./renderer.js";
import { writeFileSync, readFileSync, mkdirSync } from "fs";
import { resolve, dirname } from "path";

Error.stackTraceLimit = Infinity;

const USAGE = `\
Usage:
  ts-to-pyodide render <input-dir> <output.py>   Generate Python wrappers
  ts-to-pyodide ir <input-dir> <output.json>      Output raw IR as JSON

If no subcommand is given, defaults to "render".`;

function loadProject(projPath: string) {
  const tsConfigFilePath = resolve(projPath, "tsconfig.json");
  const project = new Project({
    tsConfigFilePath,
    libFolderPath: resolve(projPath, "node_modules/typescript/lib"),
  });
  const tsconfig = JSON.parse(
    readFileSync(tsConfigFilePath, { encoding: "utf8" }),
  ) as { include: string[] };
  const globs = tsconfig["include"].map((x) => resolve(projPath, x));
  const allFiles = project.addSourceFilesAtPaths(globs);
  allFiles.push(...project.resolveSourceFileDependencies());
  const tsLibPrefix = resolve(projPath, "node_modules/typescript/lib") + "/";
  return allFiles.filter((f) => !f.getFilePath().startsWith(tsLibPrefix));
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "--help" || args[0] === "-h") {
    console.log(USAGE);
    process.exit(0);
  }

  let subcommand: string;
  let projPath: string;
  let outFile: string;

  if (args[0] === "render" || args[0] === "ir") {
    subcommand = args[0];
    if (args.length < 3) {
      console.error(`Error: ${subcommand} requires <input-dir> <output-file>`);
      console.error(USAGE);
      process.exit(1);
    }
    projPath = args[1];
    outFile = args[2];
  } else {
    // Default: treat as "render <input-dir> <output-file>"
    subcommand = "render";
    if (args.length < 2) {
      console.error("Error: requires <input-dir> <output-file>");
      console.error(USAGE);
      process.exit(1);
    }
    projPath = args[0];
    outFile = args[1];
  }

  const files = loadProject(projPath);
  const result = convertToIR(files);

  if (subcommand === "ir") {
    writeFileSync(outFile, JSON.stringify(result, null, 2));
    console.log(`IR written to ${outFile}`);
  } else {
    const renderer = new Renderer();
    const python = renderer.renderFile(result.topLevels.ifaces);
    const outDir = dirname(resolve(outFile));
    mkdirSync(outDir, { recursive: true });
    writeFileSync(outFile, python);
    const preludeDest = resolve(outDir, "prelude.py");
    writeFileSync(preludeDest, renderer.getPrelude());
    const classCount = (python.match(/^class /gm) || []).length;
    console.log(`Generated ${classCount} classes → ${outFile}`);
    console.log(`Prelude → ${preludeDest}`);
  }
}

main();
