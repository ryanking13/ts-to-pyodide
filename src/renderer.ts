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
  jsAttrAccess,
  jsMethodCall,
  stripIfaceSuffix,
  toPythonName,
  PYTHON_RESERVED,
} from "./naming";
import {
  isNullable,
  isPromise,
  isVoidReturn,
  needsCreateProxy,
  needsToJs,
  renderType,
  unwrapPromise,
} from "./typeRendering";

const PRELUDE = `\
from typing import Any, overload
from pyodide.ffi import JsProxy, create_proxy, to_js

def _jsnull_to_none(value: Any) -> Any:
    try:
        from pyodide.ffi import jsnull
    except ImportError:
        return value
    if value is jsnull:
        return None
    return value
`;

/**
 * Renderer for generating Python bindings from TypeScript interfaces.
 */
export class Renderer {
  renderFile(interfaces: InterfaceIR[]): string {
    const bodies = interfaces.map((ir) => this.renderInterface(ir));
    return PRELUDE + "\n" + bodies.join("\n\n");
  }

  renderInterface(ir: InterfaceIR): string {
    const className = stripIfaceSuffix(ir.name);

    const lines = [
      `class ${className}:`,
      "    _binding: Any",
      "",
      "    def __init__(self, binding: JsProxy) -> None:",
      "        self._binding = binding",
    ];

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


  private renderMethod(method: CallableIR): string {
    const jsName = method.name;

    // TODO: Should we support callable interfaces somehow?
    if (!jsName || jsName === "__call__") return "";

    const sigs = method.signatures;
    if (sigs.length === 0) return "";

    const pyName = toPythonName(jsName);

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
      const spType = renderType(spreadParam.type);
      paramStrs.push(`*${spName}: ${spType}`);
    }

    const paramList = paramStrs.join(", ");
    const returnType = renderType(returns);

    const argParts = params.map((p) => this.wrapArg(p));
    if (spreadParam) {
      argParts.push(`*${spreadParam.name}`);
    }
    const argList = argParts.join(", ");

    let rawCall = jsMethodCall("self._binding", jsName, argList);
    if (isAsync) {
      rawCall = `await ${rawCall}`;
    }

    const nullable = isNullable(returns);
    let body: string;
    if (isVoidReturn(returns)) {
      body = `    ${rawCall}`;
    } else if (nullable) {
      body = `    return _jsnull_to_none(${rawCall})`;
    } else {
      body = `    return ${rawCall}`;
    }
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
    const returnType = renderType(returns);
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
    const pyName = toPythonName(jsName);
    const typeIR = prop.type;
    const isReadonly = prop.isReadonly;
    const isOptional = prop.isOptional;
    const nullable = isOptional || isNullable(typeIR);

    let typeStr = renderType(typeIR);
    if (isOptional) {
      typeStr += " | None";
    }

    let getterExpr = jsAttrAccess("self._binding", jsName);
    if (nullable) {
      getterExpr = `_jsnull_to_none(${getterExpr})`;
    }

    const lines = [
      "@property",
      `def ${pyName}(self) -> ${typeStr}:`,
      `    return ${getterExpr}`,
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
    const typeStr = renderType(param.type);
    if (param.isOptional) {
      return `${name}: ${typeStr} | None = None`;
    }
    return `${name}: ${typeStr}`;
  }

  private wrapArg(param: ParamIR): string {
    const name = param.name;
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
