import {
  InterfaceIR,
  CallableIR,
  SigIR,
  ParamIR,
  PropertyIR,
  TypeIR,
} from "./ir";
import {
  camelToSnake,
  isValidPythonIdentifier,
  jsAttrAccess,
  jsMethodCall,
  stripIfaceSuffix,
  toPythonName,
  PYTHON_RESERVED,
} from "./naming";
import {
  buildKnownInterfacesMap,
  isNullable,
  isPromise,
  isVoidReturn,
  NATIVE_TYPES,
  REFERENCE_TYPE_MAP,
  needsCreateProxy,
  needsToJs,
  needsToPy,
  renderType,
  resolveKnownInterface,
  unwrapPromise,
} from "./typeRendering";

const PRELUDE = `\
from __future__ import annotations
from typing import Any, Literal, TypedDict, overload
import js
from pyodide.ffi import JsBuffer, JsProxy, create_proxy, to_js

def _jsnull_to_none(value: Any) -> Any:
    try:
        from pyodide.ffi import jsnull
    except ImportError:
        return value
    if value is jsnull:
        return None
    return value

def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])

def _to_snake(s: str) -> str:
    import re
    return re.sub(r"([a-z0-9])([A-Z])", r"\\1_\\2", s).lower()

def _to_js_opts(opts: Any) -> Any:
    if opts is None:
        return None
    def _convert(v: Any) -> Any:
        if isinstance(v, dict):
            return {_to_camel(k): _convert(val) for k, val in v.items() if val is not None}
        if isinstance(v, list):
            return [_convert(item) for item in v]
        return v
    return to_js(_convert(opts))

def _from_js_opts(js_obj: Any) -> Any:
    if js_obj is None:
        return None
    def _convert(v: Any) -> Any:
        if isinstance(v, dict):
            return {_to_snake(k): _convert(val) for k, val in v.items()}
        if isinstance(v, list):
            return [_convert(item) for item in v]
        return v
    return _convert(js_obj.to_py())

def _to_js_headers(headers: dict[str, str] | list[tuple[str, str]] | JsProxy) -> JsProxy:
    if isinstance(headers, dict):
        return js.Headers.new(list(headers.items()))
    elif isinstance(headers, list):
        return js.Headers.new(headers)
    return headers
`;

/**
 * Renderer for generating Python bindings from TypeScript interfaces.
 */
export class Renderer {
  // Map of interface names to their Python class names
  // This is used to resolve interface types that are returned from methods
  private knownInterfaces: Map<string, string> = new Map();
  private dataBagNames: Set<string> = new Set();

  // TODO: accept optional constructor name map (JSON config) to emit a
  // CONSTRUCTOR_MAP dict for runtime dispatch (e.g. KVNamespace → KvNamespace).
  // Needed for downstream auto-wrapping of env bindings by constructor.name.
  renderFile(interfaces: InterfaceIR[]): string {
    const deduped = this.deduplicateInterfaces(interfaces).filter(
      (ir) => !(ir.name in REFERENCE_TYPE_MAP || stripIfaceSuffix(ir.name) in REFERENCE_TYPE_MAP),
    );
    this.knownInterfaces = buildKnownInterfacesMap(
      deduped.map((ir) => ir.name),
    );
    this.dataBagNames = this.classifyDataBags(deduped);
    const bodies = deduped.map((ir) =>
      this.dataBagNames.has(ir.name) ? this.renderTypedDict(ir) : this.renderInterface(ir),
    );
    return PRELUDE + "\n" + bodies.join("\n\n");
  }

  private classifyDataBags(interfaces: InterfaceIR[]): Set<string> {
    const candidates = new Set<string>();
    for (const ir of interfaces) {
      if (this.isDataBag(ir)) {
        candidates.add(ir.name);
        candidates.add(stripIfaceSuffix(ir.name));
      }
    }
    let changed = true;
    while (changed) {
      changed = false;
      for (const ir of interfaces) {
        if (!candidates.has(ir.name)) continue;
        if (this.hasWrapperClassRefs(ir, candidates)) {
          candidates.delete(ir.name);
          candidates.delete(stripIfaceSuffix(ir.name));
          changed = true;
        }
      }
    }
    return candidates;
  }

  private hasWrapperClassRefs(ir: InterfaceIR, dataBags: Set<string>): boolean {
    for (const prop of ir.properties) {
      if (this.typeRefsWrapperClass(prop.type, dataBags)) return true;
    }
    return false;
  }

  private typeRefsWrapperClass(ir: TypeIR, dataBags: Set<string>): boolean {
    if (ir.kind === "reference") {
      return this.knownInterfaces.has(ir.name) && !dataBags.has(ir.name);
    }
    if (ir.kind === "union") {
      return ir.types.some((t) => this.typeRefsWrapperClass(t, dataBags));
    }
    if (ir.kind === "array") {
      return this.typeRefsWrapperClass(ir.type, dataBags);
    }
    return false;
  }

  // A TypeScript object that only has properties and no methods is considered a data bag
  // In python, we pass it as a TypedDict not a class which is more pythonic
  private isDataBag(ir: InterfaceIR): boolean {
    if (ir.constructors && ir.constructors.length > 0) return false;
    const hasMethods = ir.methods.some(
      (m) => m.name !== "__call__" && m.name && !m.isStatic,
    );
    return !hasMethods && ir.properties.length > 0;
  }

  private renderTypedDict(ir: InterfaceIR): string {
    const className = stripIfaceSuffix(ir.name);
    const allOptional = ir.properties.every((p) => p.isOptional);
    const total = allOptional ? ", total=False" : "";
    const lines = [`class ${className}(TypedDict${total}):`];
    for (const prop of ir.properties) {
      const pyName = toPythonName(prop.name);
      let typeStr = renderType(prop.type, this.knownInterfaces);
      if (prop.isOptional && !allOptional && !isNullable(prop.type)) {
        typeStr += " | None";
      }
      lines.push(`    ${pyName}: ${typeStr}`);
    }
    return lines.join("\n") + "\n";
  }

  private deduplicateInterfaces(interfaces: InterfaceIR[]): InterfaceIR[] {
    const byClassName = new Map<string, InterfaceIR>();
    for (const ir of interfaces) {
      const className = stripIfaceSuffix(ir.name);
      const existing = byClassName.get(className);
      if (!existing) {
        byClassName.set(className, ir);
        continue;
      }
      const existingSize = existing.methods.length + existing.properties.length;
      const newSize = ir.methods.length + ir.properties.length;
      if (newSize > existingSize) {
        byClassName.set(className, ir);
      }
    }
    return [...byClassName.values()];
  }

  renderInterface(ir: InterfaceIR): string {
    const className = stripIfaceSuffix(ir.name);
    const constructors = ir.constructors;

    const lines = [
      `class ${className}:`,
      "    _binding: Any",
    ];

    if (constructors && constructors.length > 0) {
      lines.push(...this.renderConstructor(className, constructors));
    }

    lines.push(
      "",
      "    @classmethod",
      `    def from_js(cls, js_obj: JsProxy) -> ${className}:`,
      "        instance = object.__new__(cls)",
      "        instance._binding = js_obj",
      "        return instance",
      "",
      "    @property",
      "    def js_object(self) -> JsProxy:",
      "        return self._binding",
      "",
      "    def __getattr__(self, name: str) -> Any:",
      "        return getattr(self._binding, name)",
      "",
      "    def __getitem__(self, key: str) -> Any:",
      "        return getattr(self, _to_snake(key))",
      "",
      "    def __setitem__(self, key: str, value: Any) -> None:",
      "        setattr(self, _to_snake(key), value)",
    );

    for (const prop of ir.properties) {
      const rendered = this.renderProperty(prop);
      lines.push("");
      for (const line of rendered.split("\n")) {
        lines.push(`    ${line}`);
      }
    }

    for (const method of ir.methods) {
      const rendered = this.renderMethod(method);
      if (!rendered) continue;
      lines.push("");
      for (const line of rendered.split("\n")) {
        lines.push(`    ${line}`);
      }
    }

    return lines.join("\n") + "\n";
  }

  private renderConstructor(
    className: string,
    sigs: SigIR[],
  ): string[] {
    // TODO: render typed overload stubs for multiple constructor signatures.
    return [
      "",
      `    def __init__(self, *args: Any, **kwargs: Any) -> None:`,
      `        self._binding = js.${className}.new(*args, **kwargs)`,
    ];
  }

  private renderMethod(method: CallableIR): string {
    const jsName = method.name;

    // TODO: Should we support callable interfaces somehow?
    if (!jsName || jsName === "__call__") return "";
    if (!isValidPythonIdentifier(jsName)) return "";
    // Skip "new" — constructor rendering is handled by renderConstructor
    if (jsName === "new" && method.isStatic) return "";
    // TODO: (check if this breaks anything) Pyodide add these methods automatically to make JS objects behave like Python objects
    // Let's skip them to avoid conflicts for now
    const SKIP_DUNDERS = new Set(["__getitem__", "__setitem__", "__delitem__", "__contains__"]);
    if (SKIP_DUNDERS.has(jsName)) return "";

    const sigs = method.signatures;
    if (sigs.length === 0) return "";

    const pyName = toPythonName(jsName);

    // Filter out kwparams-destructured sigs — we keep the original options parameter
    // and render it as a TypedDict instead of spreading into keyword args.
    const nonKwSigs = sigs.filter((s) => !s.kwparams?.length);
    const effectiveSigs = nonKwSigs.length > 0 ? nonKwSigs : sigs;

    if (effectiveSigs.length === 1) {
      return this.renderSingleSig(jsName, pyName, effectiveSigs[0]);
    }

    return this.renderOverloadImpl(jsName, pyName, effectiveSigs);
  }

  private renderSingleSig(
    jsName: string,
    pyName: string,
    sig: SigIR,
  ): string {
    const params = sig.params;
    const spreadParam = sig.spreadParam;
    let returns = sig.returns;

    const isAsync = isPromise(returns);
    if (isAsync) {
      returns = unwrapPromise(returns);
    }

    const paramStrs = ["self", ...params.map((p) => this.renderParam(p))];
    if (spreadParam) {
      const spName = camelToSnake(spreadParam.name);
      const spType = renderType(spreadParam.type, this.knownInterfaces);
      paramStrs.push(`*${spName}: ${spType}`);
    }

    const paramList = paramStrs.join(", ");
    const returnType = renderType(returns, this.knownInterfaces);

    const argParts = params.map((p) => this.wrapArg(p));
    if (spreadParam) {
      argParts.push(`*${spreadParam.name}`);
    }
    const argList = argParts.join(", ");

    let rawCall = jsMethodCall("self._binding", jsName, argList);
    if (isAsync) {
      rawCall = `await ${rawCall}`;
    }

    const body = this.wrapReturn(rawCall, returns);
    const prefix = isAsync ? "async " : "";

    return `${prefix}def ${pyName}(${paramList}) -> ${returnType}:\n${body}`;
  }


  private renderOverloadStub(pyName: string, sig: SigIR): string {
    let returns = sig.returns;

    const isAsync = isPromise(returns);
    if (isAsync) {
      returns = unwrapPromise(returns);
    }

    const paramStrs = ["self", ...sig.params.map((p) => this.renderParam(p))];
    const paramList = paramStrs.join(", ");
    const returnType = renderType(returns, this.knownInterfaces);
    const prefix = isAsync ? "async " : "";

    return `@overload\n${prefix}def ${pyName}(${paramList}) -> ${returnType}: ...`;
  }

  private analyzeOverloadArgs(sigs: SigIR[]): {
    maxParams: number;
    toJsOpts: boolean[];
    toJs: boolean[];
  } {
    const maxParams = Math.max(...sigs.map((s) => s.params.length));
    const toJsOpts: boolean[] = new Array(maxParams).fill(false);
    const toJs: boolean[] = new Array(maxParams).fill(false);

    for (let i = 0; i < maxParams; i++) {
      for (const sig of sigs) {
        const param = sig.params[i];
        if (!param) continue;
        if (this.isDataBagType(param.type)) {
          toJsOpts[i] = true;
        } else if (needsToJs(param.type)) {
          toJs[i] = true;
        }
      }
      // _to_js_opts subsumes to_js for that position
      if (toJsOpts[i]) toJs[i] = false;
    }
    return { maxParams, toJsOpts, toJs };
  }

  private classifyReturnConversion(returns: TypeIR): string {
    const wrapperClass = resolveKnownInterface(returns, this.knownInterfaces);
    const isDataBag = wrapperClass ? this.dataBagNames.has(wrapperClass) : false;
    const nullable = isNullable(returns);
    const toPy = needsToPy(returns);

    if (isVoidReturn(returns)) return "void";
    if (wrapperClass && !isDataBag) return nullable ? "wrapper_nullable" : "wrapper";
    if (isDataBag) return nullable ? "databag_nullable" : "databag";
    if (toPy) return nullable ? "topy_nullable" : "topy";
    if (nullable) return "nullable";
    return "plain";
  }

  private emitReturnWrap(rawCall: string, kind: string, sig?: SigIR): string {
    let wrapperClass: string | undefined;
    if (sig && (kind === "wrapper" || kind === "wrapper_nullable")) {
      const ret = isPromise(sig.returns) ? unwrapPromise(sig.returns) : sig.returns;
      wrapperClass = resolveKnownInterface(ret, this.knownInterfaces);
    }
    switch (kind) {
      case "void":
        return rawCall;
      case "wrapper_nullable":
        return `_jsnull_to_none(${rawCall})`;
      case "wrapper":
        return `${wrapperClass}.from_js(${rawCall})` ;
      case "databag_nullable":
        return `_from_js_opts(_jsnull_to_none(${rawCall}))`;
      case "databag":
        return `_from_js_opts(${rawCall})`;
      case "topy_nullable":
        return `_jsnull_to_none(${rawCall}).to_py()`;
      case "topy":
        return `(${rawCall}).to_py()`;
      case "nullable":
        return `_jsnull_to_none(${rawCall})`;
      default:
        return rawCall;
    }
  }

  private renderOverloadImpl(
    jsName: string,
    pyName: string,
    sigs: SigIR[],
  ): string {
    const anyAsync = sigs.some((s) => isPromise(s.returns));
    const prefix = anyAsync ? "async " : "";

    const { maxParams, toJsOpts, toJs } = this.analyzeOverloadArgs(sigs);
    const needsArgConversion = toJsOpts.some(Boolean) || toJs.some(Boolean);

    const returnKinds = sigs.map((s) => {
      const ret = isPromise(s.returns) ? unwrapPromise(s.returns) : s.returns;
      return this.classifyReturnConversion(ret);
    });
    const uniqueKinds = new Set(returnKinds);
    const uniformReturn = uniqueKinds.size === 1;

    const argVar = needsArgConversion ? "_a" : "args";
    const kwVar = "kwargs";

    const lines: string[] = [];
    lines.push(`${prefix}def ${pyName}(self, *args: Any, **kwargs: Any) -> Any:`);

    if (needsArgConversion) {
      lines.push("    _a = list(args)");
      for (let i = 0; i < maxParams; i++) {
        if (toJsOpts[i]) {
          lines.push(`    if len(_a) > ${i} and isinstance(_a[${i}], dict):`);
          lines.push(`        _a[${i}] = _to_js_opts(_a[${i}])`);
        } else if (toJs[i]) {
          lines.push(`    if len(_a) > ${i}:`);
          lines.push(`        _a[${i}] = to_js(_a[${i}])`);
        }
      }
    }

    let rawCall = jsMethodCall("self._binding", jsName, `*${argVar}, **${kwVar}`);
    if (anyAsync) rawCall = `await ${rawCall}`;

    if (uniformReturn) {
      const wrapped = this.emitReturnWrap(rawCall, returnKinds[0], sigs[0]);
      lines.push(`    return ${wrapped}`);
    } else {
      // Find the discriminating param position: first position where different
      // return-kind groups have different param types (str vs list, etc.)
      const dispatchPos = this.findDispatchPosition(sigs, returnKinds);
      if (dispatchPos !== undefined) {
        lines.push(`    _r = ${rawCall}`);
        const grouped = this.groupByReturnKind(sigs, returnKinds);
        let first = true;
        for (const [kind, groupSigs] of grouped) {
          const paramType = groupSigs[0].params[dispatchPos]?.type;
          const condition = this.emitDispatchCondition(dispatchPos, paramType);
          const kw = first ? "if" : "elif";
          lines.push(`    ${kw} ${condition}:`);
          lines.push(`        return ${this.emitReturnWrap("_r", kind, groupSigs[0])}`);
          first = false;
        }
        lines.push(`    return _r`);
      } else {
        // Fallback: use the safest conversion (nullable if any nullable)
        const anyNullable = returnKinds.some((k) => k.includes("nullable") || k === "nullable");
        const wrapped = anyNullable
          ? `_jsnull_to_none(${rawCall})`
          : rawCall;
        lines.push(`    return ${wrapped}`);
      }
    }

    return lines.join("\n");
  }

  private emitDispatchCondition(pos: number, paramType?: TypeIR): string {
    if (!paramType) return `len(args) <= ${pos}`;
    if (paramType.kind === "array" ||
        (paramType.kind === "reference" && paramType.name === "Array")) {
      return `isinstance(args[${pos}], list)`;
    }
    if (paramType.kind === "simple" && paramType.text === "str") {
      return `isinstance(args[${pos}], str)`;
    }
    if (paramType.kind === "simple" && paramType.text === "bool") {
      return `isinstance(args[${pos}], bool)`;
    }
    if (paramType.kind === "number") {
      return `isinstance(args[${pos}], (int, float))`;
    }
    return `isinstance(args[${pos}], str)`;
  }

  private findDispatchPosition(
    sigs: SigIR[],
    returnKinds: string[],
  ): number | undefined {
    const maxParams = Math.max(...sigs.map((s) => s.params.length));
    for (let pos = 0; pos < maxParams; pos++) {
      const kindsByParamSimpleType = new Map<string, Set<string>>();
      for (let i = 0; i < sigs.length; i++) {
        const param = sigs[i].params[pos];
        if (!param) continue;
        const simpleKey = renderType(param.type, this.knownInterfaces);
        let kinds = kindsByParamSimpleType.get(simpleKey);
        if (!kinds) {
          kinds = new Set();
          kindsByParamSimpleType.set(simpleKey, kinds);
        }
        kinds.add(returnKinds[i]);
      }
      if (kindsByParamSimpleType.size >= 2) {
        const allSetsDisjoint = [...kindsByParamSimpleType.values()].every(
          (setA, idxA, arr) =>
            arr.every(
              (setB, idxB) =>
                idxA === idxB || [...setA].every((k) => !setB.has(k)),
            ),
        );
        if (allSetsDisjoint) return pos;
      }
    }
    return undefined;
  }

  private groupByReturnKind(
    sigs: SigIR[],
    returnKinds: string[],
  ): Map<string, SigIR[]> {
    const grouped = new Map<string, SigIR[]>();
    for (let i = 0; i < sigs.length; i++) {
      const kind = returnKinds[i];
      let group = grouped.get(kind);
      if (!group) {
        group = [];
        grouped.set(kind, group);
      }
      group.push(sigs[i]);
    }
    return grouped;
  }

  private renderProperty(prop: PropertyIR): string {
    const jsName = prop.name;
    if (!isValidPythonIdentifier(jsName)) return "";
    const pyName = toPythonName(jsName);
    const typeIR = prop.type;
    const isReadonly = prop.isReadonly;
    const isOptional = prop.isOptional;
    const nullable = isOptional || isNullable(typeIR);

    let typeStr = renderType(typeIR, this.knownInterfaces);
    if (isOptional && !isNullable(typeIR)) {
      typeStr += " | None";
    }

    const wrapperClass = resolveKnownInterface(typeIR, this.knownInterfaces);
    const rawExpr = jsAttrAccess("self._binding", jsName);

    const isDataBag = wrapperClass ? this.dataBagNames.has(wrapperClass) : false;
    const toPy = needsToPy(typeIR);
    let getterBody: string;
    if (wrapperClass && !isDataBag && nullable) {
      getterBody =
        `    _v = _jsnull_to_none(${rawExpr})\n` +
        `    return ${wrapperClass}.from_js(_v) if _v is not None else None`;
    } else if (wrapperClass && !isDataBag) {
      getterBody = `    return ${wrapperClass}.from_js(${rawExpr})`;
    } else if (isDataBag && nullable) {
      getterBody =
        `    _v = _jsnull_to_none(${rawExpr})\n` +
        `    return _from_js_opts(_v) if _v is not None else None`;
    } else if (isDataBag) {
      getterBody = `    return _from_js_opts(${rawExpr})`;
    } else if (toPy && nullable) {
      getterBody =
        `    _v = _jsnull_to_none(${rawExpr})\n` +
        `    return _v.to_py() if _v is not None else None`;
    } else if (toPy) {
      getterBody = `    return ${rawExpr}.to_py()`;
    } else if (nullable) {
      getterBody = `    return _jsnull_to_none(${rawExpr})`;
    } else {
      getterBody = `    return ${rawExpr}`;
    }

    const lines = [
      "@property",
      `def ${pyName}(self) -> ${typeStr}:`,
      getterBody,
    ];

    if (!isReadonly) {
      let setterLine: string;
      if (PYTHON_RESERVED.has(jsName)) {
        setterLine = `    setattr(self._binding, "${jsName}", value)`;
      } else {
        setterLine = `    self._binding.${jsName} = value`;
      }
      lines.push(
        "",
        `@${pyName}.setter`,
        `def ${pyName}(self, value: ${typeStr}) -> None:`,
        setterLine,
      );
    }

    return lines.join("\n");
  }

  private renderParam(param: ParamIR): string {
    const name = toPythonName(param.name);
    const typeStr = renderType(param.type, this.knownInterfaces);
    if (param.isOptional) {
      if (isNullable(param.type)) {
        return `${name}: ${typeStr} = None`;
      }
      return `${name}: ${typeStr} | None = None`;
    }
    return `${name}: ${typeStr}`;
  }

  // TODO: fluent/builder pattern — when a non-static instance method returns its
  // own interface type (e.g. HTMLRewriter.on() → HTMLRewriter), emit `return self`
  // instead of wrapping in a new instance. However, we don't know whether the
  // function expects cloning or not...
  private wrapReturn(rawCall: string, returns: TypeIR): string {
    const wrapperClass = resolveKnownInterface(returns, this.knownInterfaces);
    const isDataBag = wrapperClass ? this.dataBagNames.has(wrapperClass) : false;
    const nullable = isNullable(returns);
    const toPy = needsToPy(returns);

    if (isVoidReturn(returns)) {
      return `    ${rawCall}`;
    }
    if (wrapperClass && !isDataBag && nullable) {
      return (
        `    _v = _jsnull_to_none(${rawCall})\n` +
        `    return ${wrapperClass}.from_js(_v) if _v is not None else None`
      );
    }
    if (wrapperClass && !isDataBag) {
      return `    return ${wrapperClass}.from_js(${rawCall})`;
    }
    if (isDataBag && nullable) {
      return (
        `    _v = _jsnull_to_none(${rawCall})\n` +
        `    return _from_js_opts(_v) if _v is not None else None`
      );
    }
    if (isDataBag) {
      return `    return _from_js_opts(${rawCall})`;
    }
    if (toPy && nullable) {
      return (
        `    _v = ${rawCall}\n` +
        `    return _v.to_py() if _v is not None else None`
      );
    }
    if (toPy) {
      return `    return (${rawCall}).to_py()`;
    }
    if (nullable) {
      return `    return _jsnull_to_none(${rawCall})`;
    }
    return `    return ${rawCall}`;
  }

  private wrapArg(param: ParamIR): string {
    const name = toPythonName(param.name);
    if (needsCreateProxy(param.type)) {
      return `create_proxy(${name})`;
    }
    const nativeToJs = this.getNativeToJs(param.type);
    if (nativeToJs) {
      if (param.isOptional) {
        return `${nativeToJs}(${name}) if ${name} is not None else None`;
      }
      return `${nativeToJs}(${name})`;
    }
    if (this.isDataBagType(param.type)) {
      return `_to_js_opts(${name})`;
    }
    if (needsToJs(param.type)) {
      if (param.isOptional) {
        return `to_js(${name}) if ${name} is not None else None`;
      }
      return `to_js(${name})`;
    }
    return name;
  }

  private isDataBagType(ir: TypeIR): boolean {
    if (ir.kind === "reference") {
      return this.dataBagNames.has(ir.name);
    }
    if (ir.kind === "array") {
      return this.isDataBagType(ir.type);
    }
    return false;
  }

  private getNativeToJs(ir: TypeIR): string | undefined {
    if (ir.kind === "reference") {
      return NATIVE_TYPES[ir.name]?.toJs;
    }
    return undefined;
  }
}
