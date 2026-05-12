import { SourceFile } from "ts-morph";
import {
  adjustFunction,
  adjustInterfaceIR,
  getExtraBases,
  handleBuiltinBases,
} from "./adjustments.js";

import { convertFiles, ConversionResult, TopLevels } from "./astToIR.js";
import { InterfaceIR, PropertyIR, TypeIR, visitTopLevel, replaceIR } from "./ir.js";
import { stripIfaceSuffix } from "./naming.js";

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
        // Ignore unknown super classes
        // Superclasses coming from Web APIs etc. are not defined in the input
        continue;
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

/**
 * Convert a synthetic double-underscore name to a clean PascalCase name.
 * e.g. "ImageTransform__border__Union0" → "ImageTransformBorder"
 *      "ImageTransform__trim__Union0__border__Union1" → "ImageTransformTrimBorder"
 */
function syntheticNameToClean(name: string): string {
  const stripped = name.replace(/__(?:Union|Intersection)\d+/g, "");
  const parts = stripped.split("__").filter(Boolean);
  return parts
    .map((part) => stripIfaceSuffix(part))
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join("");
}

function shouldFlattenSynthetic(ir: InterfaceIR): boolean {
  if (ir.bases.length > 0) return true;
  if (ir.properties.length === 0) return true;
  const suffix = ir.name.substring(ir.name.indexOf("__"));
  if (/Intersection\d+/.test(suffix)) return true;
  if (/__array$/.test(ir.name)) return true;
  return false;
}

/**
 * Promote property-level inline object types to named TypedDict interfaces,
 * while still flattening intersection-based and sig-derived synthetics.
 *
 * Promotable: has properties, no bases, not intersection-derived.
 * Flattenable: intersection-based, sig-derived, has bases, or empty.
 */
function promoteSyntheticTypes(topLevels: TopLevels): void {
  const ifaces = topLevels.ifaces;
  const byName = new Map(ifaces.map((ir) => [ir.name, ir]));

  const synthetics: InterfaceIR[] = [];
  const sigDerived = new Set<string>();
  const toPromote = new Set<string>();
  const toFlatten = new Set<string>();

  for (const ir of ifaces) {
    const idx = ir.name.indexOf("__");
    if (idx === -1) continue;
    synthetics.push(ir);
    // Synthetic types from method signature parameters (contain __Sig\d+__)
    // should be removed but NOT promoted to named types.
    const suffix = ir.name.substring(idx);
    if (/Sig\d+/.test(suffix)) {
      sigDerived.add(ir.name);
      toFlatten.add(ir.name);
    } else if (shouldFlattenSynthetic(ir)) {
      toFlatten.add(ir.name);
    } else {
      toPromote.add(ir.name);
    }
  }
  if (synthetics.length === 0) return;

  flattenSyntheticSubset(topLevels, byName, synthetics, toFlatten, sigDerived);

  const promotable = synthetics.filter((ir) => toPromote.has(ir.name));
  if (promotable.length === 0) return;

  const renameMap = new Map<string, string>();
  const cleanGroups = new Map<string, InterfaceIR[]>();

  for (const ir of promotable) {
    const cleanName = syntheticNameToClean(ir.name);
    renameMap.set(ir.name, cleanName);
    let group = cleanGroups.get(cleanName);
    if (!group) {
      group = [];
      cleanGroups.set(cleanName, group);
    }
    group.push(ir);
  }

  const promoted = new Map<string, InterfaceIR>();
  const existingNames = new Set(topLevels.ifaces.map((ir) => ir.name));

  for (const [cleanName, variants] of cleanGroups) {
    if (existingNames.has(cleanName) && !renameMap.has(cleanName)) {
      for (const v of variants) {
        renameMap.delete(v.name);
      }
      continue;
    }

    const allProps = new Map<string, PropertyIR>();
    const propPresence = new Map<string, number>();

    for (const variant of variants) {
      for (const prop of variant.properties) {
        const existing = allProps.get(prop.name);
        if (!existing) {
          allProps.set(prop.name, { ...prop });
          propPresence.set(prop.name, 1);
        } else {
          propPresence.set(prop.name, (propPresence.get(prop.name) || 0) + 1);
          if (JSON.stringify(existing.type) !== JSON.stringify(prop.type)) {
            const a = existing.type;
            const b = prop.type;
            if (
              a.kind === "simple" && b.kind === "simple" &&
              a.text.startsWith("Literal[") && b.text.startsWith("Literal[")
            ) {
              existing.type = { kind: "simple", text: "bool" };
            } else {
              existing.type = { kind: "union", types: [a, b] };
            }
          }
        }
      }
    }

    if (variants.length > 1) {
      for (const [propName, prop] of allProps) {
        if ((propPresence.get(propName) || 0) < variants.length) {
          prop.isOptional = true;
        }
      }
    }

    promoted.set(cleanName, {
      kind: "interface",
      name: cleanName,
      methods: [],
      properties: [...allProps.values()],
      typeParams: [],
      bases: [],
    });
  }

  topLevels.ifaces = topLevels.ifaces.filter((ir) => !toPromote.has(ir.name));

  for (const ir of promoted.values()) {
    topLevels.ifaces.push(ir);
  }

  for (const ir of topLevels.ifaces) {
    rewriteSyntheticReferences(ir, renameMap);
  }

  for (const ir of topLevels.ifaces) {
    ir.bases = ir.bases.filter((b) => !toPromote.has(b.name));
  }
}

function flattenSyntheticSubset(
  topLevels: TopLevels,
  byName: Map<string, InterfaceIR>,
  synthetics: InterfaceIR[],
  toFlatten: Set<string>,
  sigDerived: Set<string>,
): void {
  const flattenTargets = synthetics.filter((ir) => toFlatten.has(ir.name));
  if (flattenTargets.length === 0) return;

  const parentToChildren = new Map<string, InterfaceIR[]>();
  for (const ir of flattenTargets) {
    const idx = ir.name.indexOf("__");
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
      topLevels.ifaces.push(parent);
      byName.set(parentName, parent);
    }
  }

  for (const [parentName, children] of parentToChildren) {
    const parent = byName.get(parentName)!;

    const allProps = new Map<string, PropertyIR>();
    for (const child of children) {
      if (!sigDerived.has(child.name)) {
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
      }
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
    parent.bases = parent.bases.filter((b) => !toFlatten.has(b.name));
  }

  topLevels.ifaces = topLevels.ifaces.filter((ir) => !toFlatten.has(ir.name));
}

function rewriteSyntheticReferences(
  ir: InterfaceIR,
  renameMap: Map<string, string>,
): void {
  visitTopLevel(
    {
      *visitReferenceType(rt) {
        const newName = renameMap.get(rt.name);
        if (newName) {
          rt.name = newName;
        }
      },
      *visitUnionType(ut) {
        yield;
        const seen = new Set<string>();
        ut.types = ut.types.filter((t) => {
          const key =
            t.kind === "reference"
              ? `ref:${t.name}`
              : t.kind === "simple"
                ? `simple:${t.text}`
                : JSON.stringify(t);
          if (seen.has(key)) return false;
          seen.add(key);
          return true;
        });
        if (ut.types.length === 1) {
          replaceIR(ut, ut.types[0]);
        }
      },
    },
    ir,
  );
}

function adjustIR(topLevels: TopLevels): void {
  promoteSyntheticTypes(topLevels);
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

export function convertToIR(
  files: SourceFile[],
  seedInterfaces?: string[],
): ConversionResult {
  const result = convertFiles(files, seedInterfaces);
  adjustIR(result.topLevels);
  return result;
}
