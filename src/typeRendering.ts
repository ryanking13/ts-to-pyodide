import { TypeIR } from "./ir";
import { logger } from "./logger";
import { stripIfaceSuffix } from "./naming";

const PRIMITIVE_SIMPLE_TYPES = new Set(["str", "bool", "None", "Any", "Never"]);

export type NativeTypeInfo = {
  pyType: string;
  toPy?: string;
  toJs?: string;
};

export const NATIVE_TYPES: Record<string, NativeTypeInfo> = {
  Headers: {
    pyType: "dict[str, str] | list[tuple[str, str]] | JsProxy",
    toJs: "_to_js_headers",
  },
  Date: {
    pyType: "datetime",
    toJs: "_to_js_date",
    toPy: "_from_js_date",
  },
};

export const REFERENCE_TYPE_MAP: Record<string, string> = {
  ArrayBuffer: "JsBuffer",
  ArrayBufferLike: "JsBuffer",
  ArrayBufferView_iface: "JsBuffer",
  Uint8Array: "JsBuffer",
  Int8Array: "JsBuffer",
  Uint16Array: "JsBuffer",
  Int16Array: "JsBuffer",
  Uint32Array: "JsBuffer",
  Int32Array: "JsBuffer",
  Float32Array: "JsBuffer",
  Float64Array: "JsBuffer",
  BigInt64Array: "JsBuffer",
  BigUint64Array: "JsBuffer",
  Uint8ClampedArray: "JsBuffer",
};

export function renderType(
  ir: TypeIR,
  knownInterfaces?: Map<string, string>,
): string {
  switch (ir.kind) {
    case "simple":
      return ir.text;
    case "number":
      return "int | float";
    case "union": {
      const parts = ir.types.map((t) => renderType(t, knownInterfaces));
      return [...new Set(parts)].join(" | ");
    }
    case "reference": {
      if (ir.name.startsWith("Promise")) {
        const args = ir.typeArgs;
        if (args.length > 0) {
          return `${ir.name}[${args.map((t) => renderType(t, knownInterfaces)).join(", ")}]`;
        }
        return ir.name;
      }
      if ((ir.name === "Record" || ir.name === "Map") && ir.typeArgs.length === 2) {
        const k = renderType(ir.typeArgs[0], knownInterfaces);
        const v = renderType(ir.typeArgs[1], knownInterfaces);
        return `dict[${k}, ${v}]`;
      }
      const resolved = knownInterfaces?.get(ir.name);
      if (resolved) return resolved;
      const native = NATIVE_TYPES[ir.name];
      if (native) return native.pyType;
      const mapped = REFERENCE_TYPE_MAP[ir.name];
      if (mapped) return mapped;
      return "Any";
    }
    case "array":
      return `list[${renderType(ir.type, knownInterfaces)}]`;
    case "tuple":
      return `tuple[${ir.types.map((t) => renderType(t, knownInterfaces)).join(", ")}]`;
    case "other":
      return "Any";
    case "paren":
      return `(${renderType(ir.type, knownInterfaces)})`;
    case "parameterReference":
      return "Any";
    case "operator":
      return renderType(ir.type, knownInterfaces);
    case "spread":
      return `*${renderType(ir.type, knownInterfaces)}`;
    case "callable":
      return "Any";
  }
}

export function resolveKnownInterface(
  ir: TypeIR,
  knownInterfaces: Map<string, string>,
): string | undefined {
  if (ir.kind === "reference") {
    return knownInterfaces.get(ir.name);
  }
  // TODO: unions with multiple known interfaces (e.g. Videos_iface | Audio_iface)
  // need runtime dispatch (constructor.name check) to pick the right wrapper class.
  if (ir.kind === "union") {
    const nonNone = ir.types.filter(
      (t) => !(t.kind === "simple" && t.text === "None"),
    );
    if (nonNone.length === 1 && nonNone[0].kind === "reference") {
      return knownInterfaces.get(nonNone[0].name);
    }
    const knownInUnion = nonNone.filter(
      (t) => t.kind === "reference" && knownInterfaces.has(t.name),
    );
    if (knownInUnion.length > 1) {
      const names = knownInUnion.map(
        (t) => t.kind === "reference" ? t.name : "",
      );
      logger.warn(
        `Union has multiple known interfaces [${names.join(", ")}], cannot auto-wrap`,
      );
    }
  }
  return undefined;
}

export function buildKnownInterfacesMap(
  names: string[],
): Map<string, string> {
  const map = new Map<string, string>();
  for (const name of names) {
    const className = stripIfaceSuffix(name);
    map.set(name, className);
    map.set(className, className);
  }
  return map;
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

export function needsToPy(ir: TypeIR): boolean {
  if (ir.kind === "reference" && (ir.name === "Record" || ir.name === "Map")) return true;
  if (ir.kind === "union") {
    return ir.types.some((t) => !(t.kind === "simple" && t.text === "None") && needsToPy(t));
  }
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
