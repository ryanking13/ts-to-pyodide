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
  needsCreateProxy,
  needsToJs,
  needsToPy,
  renderType,
  resolveKnownInterface,
  unwrapPromise,
} from "./typeRendering";

const PRELUDE = `\
from __future__ import annotations
from typing import Any, overload
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

def _build_opts(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}
`;

/**
 * Renderer for generating Python bindings from TypeScript interfaces.
 */
export class Renderer {
  // Map of interface names to their Python class names
  // This is used to resolve interface types that are returned from methods
  private knownInterfaces: Map<string, string> = new Map();

  // TODO: accept optional constructor name map (JSON config) to emit a
  // CONSTRUCTOR_MAP dict for runtime dispatch (e.g. KVNamespace → KvNamespace).
  // Needed for downstream auto-wrapping of env bindings by constructor.name.
  renderFile(interfaces: InterfaceIR[]): string {
    const deduped = this.deduplicateInterfaces(interfaces);
    this.knownInterfaces = buildKnownInterfacesMap(
      deduped.map((ir) => ir.name),
    );
    const bodies = deduped.map((ir) => this.renderInterface(ir));
    return PRELUDE + "\n" + bodies.join("\n\n");
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

    const sigs = method.signatures;
    if (sigs.length === 0) return "";

    const pyName = toPythonName(jsName);

    const kwSig = sigs.find((s) => s.kwparams?.length);
    if (kwSig) {
      return this.renderKwparamsSig(jsName, pyName, kwSig);
    }

    if (sigs.length === 1) {
      return this.renderSingleSig(jsName, pyName, sigs[0]);
    }

    const parts: string[] = [];
    for (const sig of sigs) {
      parts.push(this.renderOverloadStub(pyName, sig));
    }
    parts.push(this.renderOverloadImpl(jsName, pyName, sigs));
    return parts.join("\n");
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

  private renderKwparamsSig(
    jsName: string,
    pyName: string,
    sig: SigIR,
  ): string {
    const params = sig.params;
    const kwparams = sig.kwparams!;
    let returns = sig.returns;

    const isAsync = isPromise(returns);
    if (isAsync) {
      returns = unwrapPromise(returns);
    }

    const paramStrs = ["self", ...params.map((p) => this.renderParam(p))];
    paramStrs.push("*");
    for (const kw of kwparams) {
      const kwName = toPythonName(kw.name);
      const kwType = renderType(kw.type, this.knownInterfaces);
      if (isNullable(kw.type)) {
        paramStrs.push(`${kwName}: ${kwType} = None`);
      } else {
        paramStrs.push(`${kwName}: ${kwType} | None = None`);
      }
    }

    const paramList = paramStrs.join(", ");
    const returnType = renderType(returns, this.knownInterfaces);

    const argParts = params.map((p) => this.wrapArg(p));

    const bodyLines: string[] = [];
    const kwArgs = kwparams.map(
      (kw) => `${kw.name}=${toPythonName(kw.name)}`,
    ).join(", ");
    bodyLines.push(`    _opts = _build_opts(${kwArgs})`);

    argParts.push("to_js(_opts) if _opts else None");
    const argList = argParts.join(", ");

    let rawCall = jsMethodCall("self._binding", jsName, argList);
    if (isAsync) {
      rawCall = `await ${rawCall}`;
    }

    const returnBody = this.wrapReturn(rawCall, returns);
    bodyLines.push(returnBody);

    const prefix = isAsync ? "async " : "";
    return `${prefix}def ${pyName}(${paramList}) -> ${returnType}:\n${bodyLines.join("\n")}`;
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

  private renderOverloadImpl(
    jsName: string,
    pyName: string,
    sigs: SigIR[],
  ): string {
    const anyAsync = sigs.some((s) => isPromise(s.returns));
    const prefix = anyAsync ? "async " : "";
    let call = jsMethodCall("self._binding", jsName, "*args, **kwargs");
    if (anyAsync) {
      call = `await ${call}`;
    }

    return (
      `${prefix}def ${pyName}(self, *args: Any, **kwargs: Any) -> Any:\n` +
      `    return ${call}`
    );
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

    const toPy = needsToPy(typeIR);
    let getterBody: string;
    if (wrapperClass && nullable) {
      getterBody =
        `    _v = ${rawExpr}\n` +
        `    return ${wrapperClass}.from_js(_v) if _v is not None else None`;
    } else if (wrapperClass) {
      getterBody = `    return ${wrapperClass}.from_js(${rawExpr})`;
    } else if (toPy && nullable) {
      getterBody =
        `    _v = ${rawExpr}\n` +
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
    const nullable = isNullable(returns);
    const toPy = needsToPy(returns);

    if (isVoidReturn(returns)) {
      return `    ${rawCall}`;
    }
    if (wrapperClass && nullable) {
      return (
        `    _v = ${rawCall}\n` +
        `    return ${wrapperClass}.from_js(_v) if _v is not None else None`
      );
    }
    if (wrapperClass) {
      return `    return ${wrapperClass}.from_js(${rawCall})`;
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
    if (needsToJs(param.type)) {
      if (param.isOptional) {
        return `to_js(${name}) if ${name} is not None else None`;
      }
      return `to_js(${name})`;
    }
    return name;
  }
}
