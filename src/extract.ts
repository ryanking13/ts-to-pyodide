import { SourceFile } from "ts-morph";
import {
  adjustFunction,
  adjustInterfaceIR,
  getExtraBases,
  handleBuiltinBases,
} from "./adjustments.js";

import { convertFiles, ConversionResult, TopLevels } from "./astToIR.js";
import { InterfaceIR, PropertyIR } from "./ir.js";

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

function flattenSyntheticTypes(topLevels: TopLevels): void {
  const ifaces = topLevels.ifaces;
  const byName = new Map(ifaces.map((ir) => [ir.name, ir]));

  const parentToChildren = new Map<string, InterfaceIR[]>();
  for (const ir of ifaces) {
    const idx = ir.name.indexOf("__");
    if (idx === -1) continue;
    const parentName = ir.name.substring(0, idx);
    let children = parentToChildren.get(parentName);
    if (!children) {
      children = [];
      parentToChildren.set(parentName, children);
    }
    children.push(ir);
  }

  for (const [parentName] of parentToChildren) {
    if (!byName.has(parentName)) {
      const parent: InterfaceIR = {
        kind: "interface",
        name: parentName,
        methods: [],
        properties: [],
        typeParams: [],
        bases: [],
      };
      ifaces.push(parent);
      byName.set(parentName, parent);
    }
  }

  const toRemove = new Set<string>();

  for (const [parentName, children] of parentToChildren) {
    const parent = byName.get(parentName)!;

    const allProps = new Map<string, PropertyIR>();
    for (const child of children) {
      for (const prop of child.properties) {
        const existing = allProps.get(prop.name);
        if (!existing) {
          allProps.set(prop.name, { ...prop });
        } else if (JSON.stringify(existing.type) !== JSON.stringify(prop.type)) {
          const a = existing.type;
          const b = prop.type;
          if (a.kind === "simple" && b.kind === "simple" &&
              a.text.startsWith("Literal[") && b.text.startsWith("Literal[")) {
            existing.type = { kind: "simple", text: "bool" };
          } else {
            existing.type = { kind: "union", types: [a, b] };
          }
        }
      }
      toRemove.add(child.name);
    }

    const unionGroups = new Map<string, InterfaceIR[]>();
    for (const child of children) {
      const parts = child.name.substring(parentName.length + 2).split("__");
      const groupKey = parts.slice(0, -1).join("__");
      if (!parts[parts.length - 1].startsWith("Union")) continue;
      let group = unionGroups.get(groupKey);
      if (!group) {
        group = [];
        unionGroups.set(groupKey, group);
      }
      group.push(child);
    }
    for (const siblings of unionGroups.values()) {
      if (siblings.length <= 1) continue;
      const propNames = siblings.map(
        (s) => new Set(s.properties.map((p) => p.name)),
      );
      const allUnionPropNames = new Set(propNames.flatMap((s) => [...s]));
      for (const name of allUnionPropNames) {
        const prop = allProps.get(name);
        if (prop && !propNames.every((names) => names.has(name))) {
          prop.isOptional = true;
        }
      }
    }

    for (const prop of allProps.values()) {
      if (!parent.properties.some((p) => p.name === prop.name)) {
        parent.properties.push(prop);
      }
    }
    parent.bases = parent.bases.filter((b) => !toRemove.has(b.name));
  }

  topLevels.ifaces = ifaces.filter((ir) => !toRemove.has(ir.name));
}

function adjustIR(topLevels: TopLevels): void {
  flattenSyntheticTypes(topLevels);
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
