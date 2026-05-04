# Implementation Plan: Python Runtime Wrapper Backend

## Goal

Generate executable Python wrapper classes from TypeScript `.d.ts` type definitions. The wrappers provide a Pythonic API for Cloudflare Workers bindings: snake_case naming, async methods, and delegation to the underlying JsProxy.

## Architecture

Single TypeScript project. The entire pipeline runs in Node.js:

```
.d.ts files ──→ [ts-morph AST] ──→ [astToIR.ts] ──→ IR ──→ [renderer.ts] ──→ .py wrappers
```

### Key Files

```
ts-to-pyodide/
├── src/
│   ├── main.ts               # CLI: outputs JSON IR
│   ├── extract.ts            # convertToIR() — pipeline entry
│   ├── astToIR.ts            # TS AST → IR (from ts-to-python)
│   ├── ir.ts                 # IR type definitions
│   ├── renderer.ts           # Renderer class: IR → Python wrapper strings
│   ├── naming.ts             # camelToSnake, sanitizePythonName, jsAttrAccess
│   ├── typeRendering.ts      # renderType, isPromise, isNullable, needsToJs
│   ├── irToString.ts         # Kept as dependency of astToIR
│   └── adjustments.ts        # TYPE_TEXT_MAP, BUILTIN_NAMES
├── tests/
│   ├── fixtures/             # {input.d.ts, ir.json, expected.py} per case
│   ├── ir.test.ts            # IR extraction
│   ├── naming.test.ts        # Name conversion utilities
│   ├── typeRendering.test.ts # Type analysis utilities
│   ├── renderer.test.ts      # Renderer class (fixture + inline)
│   ├── e2e.test.ts           # Full pipeline + known IR gaps
│   └── tycheck.test.ts       # ty type checker on generated output
└── package.json
```

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | TypeScript only | Single toolchain, direct IR access with type safety |
| Class naming | Strip `_iface` suffix | `KVNamespace_iface` → `class KVNamespace` |
| Method naming | camelCase → snake_case | PEP 8 |
| Async | `Promise<T>` → `async def` + `await` | Unwrap Promise, return inner T |
| Overloads | `@overload` stubs + `*args, **kwargs` impl | Forward all args |
| Reserved words | Append `_`, use `getattr()` | `from` → `from_()` |
| `_binding` type | `Any` | pyodide's `JsProxy` stubs lack `__getattr__` |
| Arg conversion | Inline `to_js(param)` in call | Avoids type reassignment errors |
| Prelude | Static, uses `pyodide.ffi` imports | `jsnull` guarded with try/except for Python 3.12 compat |
| Type checking | `ty` with pyodide-py in `.venv-ty` | Real pyodide type resolution |

## What's Implemented

### Features covered:
- Sync/async methods, Promise unwrapping
- Optional parameters, rest params (`...args`)
- Readonly/writable properties
- camelCase → snake_case (methods, params, properties)
- Overloaded methods (`@overload` + `*args` impl)
- Python reserved word escaping
- Nullable return wrapping (`_jsnull_to_none`)
- dict/list/array arg conversion (`to_js()` inline)
- Callable param conversion (`create_proxy()`)
- `_iface` suffix stripping, `__call__` skipping

## Remaining Work

### High Priority

1. **Binding type filtering** — only generate wrappers for binding interfaces, skip builtins/infrastructure
2. **Constructor name map** — `.d.ts` name → runtime `constructor.name`
3. **CLI for file output** — `main.ts` currently outputs IR JSON; need it to also run renderer and write `.py` files
4. **Wrapper-specific type mapping** — `ArrayBuffer` → `bytes`, `ReadableStream` → `AsyncIterable[bytes]`

### Medium Priority

5. **kwparams handling** — the IR destructures TS option objects into keyword args
6. **`__getattr__` fallback** — pass unknown attributes through to JsProxy
7. **`js_object` escape hatch** — expose raw JsProxy
8. **Test with real cloudflare-workers .d.ts** — full pipeline on wrangler types output

### Known Limitations (future work)

9. **Sub-binding wrapping** — `D1Database.prepare()` → `D1PreparedStatement`, `StreamBinding.video()` → `StreamVideoHandle` return raw JsProxy
10. **Fluent/builder pattern** — `ImageTransformer.transform().output()` chaining
11. **Generic type params** — currently ignored
12. **Discriminated union types** — email attachments, image info responses

### Known IR Gaps
- **`get`/`set` accessors** in interfaces (`get body(): ReadableStream`) are dropped by `astToIR.ts` — it only handles `PropertySignature`, not `GetAccessor`/`SetAccessor` AST nodes. Affects `R2ObjectBody.body`, `R2ObjectBody.bodyUsed`, and many Event properties. Documented with a test.
- **`declare module` blocks** (`cloudflare:workers`, `cloudflare:pipelines`, etc.) are not extracted by `convertFiles()`.

### Type Rendering
Non-Promise reference types (e.g., `ArrayBuffer`, `KVNamespacePutOptions_iface`) render as `Any` in type annotations. Generic type params (`T`) also render as `Any`. Only `Promise` keeps its name (for async detection by the renderer). This is intentional — the annotations are informational and these types don't exist in the generated Python.