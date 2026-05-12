import { InterfaceIR, visitTopLevel } from "./ir.js";
import { stripIfaceSuffix } from "./naming.js";

export function collectDependencies(
  roots: string[],
  allIfaces: InterfaceIR[],
): InterfaceIR[] {
  const byName = new Map<string, InterfaceIR>();
  for (const ir of allIfaces) {
    byName.set(ir.name, ir);
    byName.set(stripIfaceSuffix(ir.name), ir);
  }

  const needed = new Set<string>();
  const visited = new Set<string>();
  const queue: string[] = [];

  for (const root of roots) {
    queue.push(root);
    queue.push(root + "_iface");
  }

  while (queue.length > 0) {
    const name = queue.pop()!;
    if (visited.has(name)) continue;
    visited.add(name);
    const ir = byName.get(name);
    if (!ir) continue;
    needed.add(ir.name);

    const refs: string[] = [];
    visitTopLevel(
      {
        *visitReferenceType(rt) {
          refs.push(rt.name);
        },
      },
      ir,
    );

    for (const ref of refs) {
      if (!visited.has(ref)) {
        queue.push(ref);
      }
    }

    for (const base of ir.bases) {
      if (!visited.has(base.name)) {
        queue.push(base.name);
      }
    }
  }

  return allIfaces.filter((ir) => needed.has(ir.name));
}
