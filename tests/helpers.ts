import { Project, SyntaxKind } from "ts-morph";
import { Converter as AstConverter } from "../src/astToIR";
import { TypeNode } from "ts-morph";
import { resolve } from "path";
import {
  InterfaceIR,
  CallableIR,
  SigIR,
  ParamIR,
  PropertyIR,
  TypeIR,
} from "../src/ir";

export const FIXTURES_DIR = resolve(import.meta.dirname!, "fixtures");

export const FIXTURE_NAMES = [
  "sync_method",
  "greeter",
  "math_params",
  "async_delete",
  "readonly_properties",

  "hyperdrive",
  "overloads",
  "generic_method",
  "sub_binding_property",
  "buffer_types",
  "get_accessor",
];

export function typeToIR(t: TypeNode) {
  const c = new AstConverter();
  return c.typeToIR(t);
}

export function makeProject(): Project {
  return new Project({
    tsConfigFilePath: resolve(import.meta.dirname!, "tsconfig.test.json"),
    libFolderPath: resolve(import.meta.dirname!, "..", "node_modules/typescript/lib"),
  });
}

let n = 0;
export function getTypeNode(type: string): TypeNode {
  n++;
  const fname = `/getTypeNode_$${n}.ts`;
  const project = makeProject();
  project.createSourceFile(fname, `type A = ${type};`);
  const file = project.getSourceFileOrThrow(fname);
  const alias = file.getFirstDescendantByKind(SyntaxKind.TypeAliasDeclaration)!;
  return alias.getTypeNode()!;
}

export function irInterface(
  name: string,
  methods: CallableIR[] = [],
  properties: PropertyIR[] = [],
): InterfaceIR {
  return {
    kind: "interface",
    name,
    methods,
    properties,
    typeParams: [],
    bases: [],
  };
}

export function irMethod(
  name: string,
  signatures: SigIR[] = [],
  isStatic = false,
): CallableIR {
  return { kind: "callable", name, signatures, isStatic };
}

export function irSig(
  params: ParamIR[] = [],
  returns: TypeIR = { kind: "simple", text: "None" },
): SigIR {
  return { params, returns };
}

export function irSigWithSpread(
  params: ParamIR[] = [],
  spreadParam: ParamIR | undefined,
  returns: TypeIR = { kind: "simple", text: "None" },
): SigIR {
  return { params, spreadParam, returns };
}

export function irSigWithKwparams(
  params: ParamIR[],
  kwparams: ParamIR[],
  returns: TypeIR = { kind: "simple", text: "None" },
): SigIR {
  return { params, kwparams, returns };
}

export function irParam(
  name: string,
  type: TypeIR,
  isOptional = false,
): ParamIR {
  return { name, type, isOptional };
}

export function irProperty(
  name: string,
  type: TypeIR,
  isReadonly = false,
  isOptional = false,
): PropertyIR {
  return { name, type, isReadonly, isOptional, isStatic: false };
}

export function promiseOf(inner: TypeIR): TypeIR {
  return { kind: "reference", name: "Promise", typeArgs: [inner] };
}

export function nullable(inner: TypeIR): TypeIR {
  return { kind: "union", types: [inner, { kind: "simple", text: "None" }] };
}

export function callableType(
  params: ParamIR[] = [],
  returns: TypeIR = { kind: "simple", text: "None" },
): TypeIR {
  return { kind: "callable", signatures: [irSig(params, returns)] };
}

export function refType(name: string): TypeIR {
  return { kind: "reference", name, typeArgs: [] };
}
