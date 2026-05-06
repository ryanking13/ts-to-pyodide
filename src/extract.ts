import { SourceFile } from "ts-morph";
import {
  adjustFunction,
  adjustInterfaceIR,
  getExtraBases,
  handleBuiltinBases,
} from "./adjustments.js";

import { convertFiles, ConversionResult, TopLevels } from "./astToIR.js";
import { InterfaceIR } from "./ir.js";

function topologicalSortClasses(
  nameToCls: Map<string, InterfaceIR>,
): InterfaceIR[] {
  type AnotatedClass = InterfaceIR & { sorted?: boolean; visited?: boolean };
  const result: InterfaceIR[] = [];
  function visit(cls: AnotatedClass) {
    if (cls.sorted) {
      return;
    }
    if (cls.visited) {
      throw new Error("Cycle");
    }
    cls.visited = true;
    for (const { name } of cls.bases) {
      const superClass = nameToCls.get(name);
      if (!superClass) {
        throw new Error(`Unknown super: ${cls.name} < ${name}`);
      }
      visit(superClass);
    }
    cls.sorted = true;
    result.push(cls);
  }
  for (const cls of nameToCls.values()) {
    visit(cls);
  }
  return result;
}

function fixupClassBases(nameToCls: Map<string, InterfaceIR>): void {
  handleBuiltinBases(nameToCls);
  const classes = topologicalSortClasses(nameToCls);
  const classNameToIndex = new Map(classes.map((cls, idx) => [cls.name, idx]));
  for (const cls of classes) {
    cls.extraBases ??= [];
    cls.extraBases.push(...getExtraBases(cls.name));
    if (cls.extraBases.length > 0) {
      cls.concrete = true;
    } else {
      for (const { name: sName } of cls.bases) {
        const s = nameToCls.get(sName);
        if (s?.concrete) {
          cls.concrete = true;
          break;
        }
        if (s?.jsobject) {
          cls.jsobject = true;
        }
      }
    }
    if (!cls.jsobject && !cls.concrete) {
      cls.extraBases.push("Protocol");
    }
    if (cls.jsobject) {
      cls.extraBases.push("_JsObject");
    }
    cls.bases.sort(({ name: a }, { name: b }) => {
      return classNameToIndex.get(b)! - classNameToIndex.get(a)!;
    });
  }
}

function adjustIR(topLevels: TopLevels): void {
  const classes = topLevels.ifaces;
  // Deduplicate interfaces with the same name, keeping the richer one.
  // TODO: Duplicates arise from declare module extraction and interface merging.
  //       Handle it properly instead of choosing the richer one.
  const nameToCls = new Map<string, InterfaceIR>();
  for (const cls of classes) {
    const existing = nameToCls.get(cls.name);
    if (!existing || cls.methods.length + cls.properties.length > existing.methods.length + existing.properties.length) {
      nameToCls.set(cls.name, cls);
    }
  }
  if (nameToCls.size < classes.length) {
    topLevels.ifaces = [...nameToCls.values()];
  }
  fixupClassBases(nameToCls);
  classes.forEach(adjustInterfaceIR);
  topLevels.callables.forEach(adjustFunction);
  for (const iface of topLevels.ifaces) {
    iface.methods.forEach(adjustFunction);
  }
}

export function convertToIR(files: SourceFile[]): ConversionResult {
  const result = convertFiles(files);
  adjustIR(result.topLevels);
  return result;
}
