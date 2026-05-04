import { TypeIR } from "./ir";

const PRIMITIVE_SIMPLE_TYPES = new Set(["str", "bool", "None", "Any", "Never"]);

export function renderType(ir: TypeIR): string {
  switch (ir.kind) {
    case "simple":
      return ir.text;
    case "number":
      return "int | float";
    case "union":
      return ir.types.map(renderType).join(" | ");
    case "reference": {
      if (ir.name.startsWith("Promise")) {
        const args = ir.typeArgs;
        if (args.length > 0) {
          return `${ir.name}[${args.map(renderType).join(", ")}]`;
        }
        return ir.name;
      }
      return "Any";
    }
    case "array":
      return `list[${renderType(ir.type)}]`;
    case "tuple":
      return `tuple[${ir.types.map(renderType).join(", ")}]`;
    case "other":
      return "Any";
    case "paren":
      return `(${renderType(ir.type)})`;
    case "parameterReference":
      return "Any";
    case "operator":
      return renderType(ir.type);
    case "spread":
      return `*${renderType(ir.type)}`;
    case "callable":
      return "Any";
  }
}

export function isPromise(ir: TypeIR): boolean {
  return ir.kind === "reference" && ir.name.startsWith("Promise");
}

export function unwrapPromise(ir: TypeIR): TypeIR {
  if (ir.kind === "reference" && ir.typeArgs.length > 0) {
    return ir.typeArgs[0];
  }
  return { kind: "simple", text: "None" };
}

export function isVoidReturn(ir: TypeIR): boolean {
  return ir.kind === "simple" && ir.text === "None";
}

export function isNullable(ir: TypeIR): boolean {
  if (ir.kind === "union") {
    return ir.types.some((t) => t.kind === "simple" && t.text === "None");
  }
  return false;
}

export function needsCreateProxy(ir: TypeIR): boolean {
  if (ir.kind === "callable") return true;
  if (ir.kind === "union") return ir.types.some(needsCreateProxy);
  return false;
}

export function needsToJs(ir: TypeIR): boolean {
  if (needsCreateProxy(ir)) return false;
  switch (ir.kind) {
    case "simple":
      return !PRIMITIVE_SIMPLE_TYPES.has(ir.text);
    case "number":
      return false;
    case "reference":
      return true;
    case "other":
      return false;
    case "union":
      return ir.types.some(needsToJs);
    case "array":
      return true;
    default:
      return false;
  }
}
