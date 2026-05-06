// When updating this list (e.g. updated supported Python version),
// run `python -c "import keyword; print('\n'.join(sorted(keyword.kwlist)))"`
// and
// run `python -c "import keyword; print('\n'.join(sorted(keyword.softkwlist)))"`
const PYTHON_KEYWORDS = new Set([
  "False", "None", "True",
  "and", "as", "assert", "async", "await",
  "break",
  "class", "continue",
  "def", "del",
  "elif", "else", "except",
  "finally", "for", "from",
  "global",
  "if", "import", "in", "is",
  "lambda",
  "nonlocal", "not",
  "or",
  "pass",
  "raise", "return",
  "try",
  "while", "with",
  "yield",
]);

const PYTHON_SOFT_KEYWORDS = new Set([
  "_", "case", "match", "type",
]);

export const PYTHON_RESERVED = new Set([
  ...PYTHON_KEYWORDS,
  ...PYTHON_SOFT_KEYWORDS,
]);

// Pyodide's JsProxy adds these as Python generator protocol methods,
// shadowing actual JS methods with the same name (e.g. SendEmail.send).
// We use _call_js_method (js.Reflect.get) to bypass the interception.
export const PYODIDE_SHADOWED = new Set([
  "send", "throw", "close",
]);

export function camelToSnake(name: string): string {
  return name
    .replace(/([A-Z]+)([A-Z][a-z])/g, "$1_$2")  // e.g. URLList -> URL_List
    .replace(/([a-z0-9])([A-Z])/g, "$1_$2")     // e.g. myMethod -> my_Method
    .toLowerCase();
}

export function sanitizePythonName(name: string): string {
  if (PYTHON_RESERVED.has(name)) {
    return name + "_";
  }
  return name;
}

export function toPythonName(jsName: string): string {
  return sanitizePythonName(camelToSnake(jsName));
}

export function stripIfaceSuffix(name: string): string {
  if (name.endsWith("_iface")) {
    return name.slice(0, -"_iface".length);
  }
  return name;
}

export function isValidPythonIdentifier(name: string): boolean {
  return /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(name);
}

export function jsAttrAccess(obj: string, jsName: string): string {
  if (PYTHON_RESERVED.has(jsName)) {
    return `getattr(${obj}, "${jsName}")`;
  }
  return `${obj}.${jsName}`;
}

export function jsMethodCall(
  obj: string,
  jsName: string,
  args: string,
): string {
  if (PYODIDE_SHADOWED.has(jsName)) {
    const callArgs = args ? `${obj}, "${jsName}", ${args}` : `${obj}, "${jsName}"`;
    return `_call_js_method(${callArgs})`;
  }
  if (PYTHON_RESERVED.has(jsName)) {
    return `getattr(${obj}, "${jsName}")(${args})`;
  }
  return `${obj}.${jsName}(${args})`;
}
