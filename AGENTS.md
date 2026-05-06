# AGENTS.md — ts-to-pyodide

## Project Overview

ts-to-pyodide generates **Python runtime wrappers** from TypeScript `.d.ts` type definitions for Cloudflare Workers bindings. It parses `.d.ts` files into an intermediate representation (IR) using ts-morph, then a TypeScript renderer produces executable Python wrapper classes.

The IR extraction is forked from [pyodide/ts-to-python](https://github.com/pyodide/ts-to-python) (which generates `.pyi` type stubs). We reuse the same IR and parser but have a completely different rendering backend.

## Build System & Commands

- **Package manager**: npm
- **Run all tests**: `npm test`
- **Type check**: `npm run check`
- **Render Python wrappers**: `npm run run -- render <input-dir> <output.py>`
- **Output raw IR JSON**: `npm run run -- ir <input-dir> <output.json>`
- **Build**: `npm run build`

## Testing

TDD approach: every feature was added as a failing test first. All tests run via `npm test`.

| File | Purpose |
|------|---------|
| `tests/ir.test.ts` | IR extraction from `.d.ts` |
| `tests/naming.test.ts` | `camelToSnake`, `sanitizePythonName`, `jsAttrAccess`, keyword completeness |
| `tests/typeRendering.test.ts` | `renderType`, `isPromise`, `isNullable`, `needsToJs`, `needsCreateProxy`, `resolveKnownInterface`, `needsToPy`, Record/Headers rendering |
| `tests/renderer.test.ts` | Fixture-based + inline assertion tests for `Renderer` class |
| `tests/e2e.test.ts` | Full pipeline: `.d.ts` → IR → Python, sub-binding wrapping, constructor support, TypedDict options, R2 bucket fixture |
| `tests/tycheck.test.ts` | Runs `ty` type checker on generated Python using real `pyodide-py` types + `js.pyi` stub |
| `tests/cli.test.ts` | CLI subcommand tests (`render`, `ir`, default, help) with self-contained fixture |
| `tests/integration.test.ts` | Full pipeline against `@cloudflare/workers-types` npm package (env-gated) |

### Test Fixtures

Fixtures live in `tests/fixtures/{name}/`. Two kinds:

**renderInterface fixtures** (`input.d.ts` + `ir.json` + `expected.py`) — test single class rendering:
`sync_method`, `greeter`, `math_params`, `async_delete`, `readonly_properties`, `d1database`, `hyperdrive`, `overloads`, `generic_method`, `sub_binding_property`, `buffer_types`, `get_accessor`

**renderFile fixtures** (`input.d.ts` + `expected.py`) — test full pipeline with prelude, multiple classes, sub-binding wrapping:
`sub_binding_wrap`, `declare_module`, `constructor`, `kwparams`, `r2_bucket`

## Architecture

```
.d.ts files ──→ [ts-morph AST] ──→ [astToIR.ts] ──→ IR ──→ [renderer.ts] ──→ .py wrappers
```

### Where to Look

| Task | File |
|------|------|
| Understand the IR schema | `src/ir.ts` |
| Change how TS is parsed to IR | `src/astToIR.ts` |
| Change wrapper Python output | `src/renderer.ts` |
| Change naming conventions | `src/naming.ts` |
| Change type annotations / native types | `src/typeRendering.ts` |
| Change CLI behavior | `src/main.ts` |
| Add a new wrapper feature | Add test first (TDD) in `tests/renderer.test.ts` or `tests/e2e.test.ts` |
| Add a native type override | Add to `NATIVE_TYPES` in `src/typeRendering.ts` + helper in prelude |
| Debug IR shape for a TS pattern | See `tests/e2e.test.ts` for how to call `convertToIR` inline |

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Single language | TypeScript only | Simpler toolchain, direct IR access with type safety |
| Class naming | Strip `_iface` suffix | IR produces `KVNamespace_iface`, renderer outputs `class KVNamespace` |
| Method naming | camelCase → snake_case | PEP 8 |
| Async detection | `Promise<T>` return → `async def` | Unwrap Promise, return inner type T |
| Overloads | `@overload` stubs + `*args, **kwargs` impl | Forward all args to JS binding |
| Reserved words | Append `_`, use `getattr()` for JS access | `from` → `from_()` |
| `_binding` type | `Any` (not `JsProxy`) | pyodide's `JsProxy` stubs lack `__getattr__`, type checker can't resolve attribute access |
| null/undefined | Always wrap with `_jsnull_to_none` | IR conflates null/undefined/void into `None`; safe overshoot |
| Arg conversion | Inline in call expression | `to_js(param)` in arg list, not reassigning variable (avoids ty type errors) |
| Generated prelude | Static, uses real pyodide imports | `import js` + `from pyodide.ffi import JsBuffer, JsProxy, create_proxy, to_js` with helpers |
| Forward references | `from __future__ import annotations` | Lazy annotation evaluation avoids `NameError` when class A references class B defined later |
| Type checking | `ty` with pyodide-py + `js.pyi` stub | Real type resolution; `js` module stub via `--extra-search-path` |
| Constructor support | `declare class` with constructor → `__init__` calling `js.ClassName.new()` | Pyodide's `.new()` maps to JS `Reflect.construct()` |
| `from_js` classmethod | All wrapper types get `from_js(cls, js_obj)` | Wraps existing JsProxy without calling constructor |
| No-constructor types | Interfaces without constructor skip `__init__` | Users interact via `from_js` or sub-binding wrapping |
| Sub-binding wrapping | Wrap via `from_js` classmethod | `D1PreparedStatement.from_js(self._binding.prepare(query))` |
| Data bag interfaces | TypedDict with snake_case keys | Interfaces with only properties, no methods → `TypedDict(total=False)` |
| Options parameters | Keep as TypedDict param, not kwparams | `put(key, value, options: R2PutOptions \| None)` instead of destructuring |
| Key conversion | `_to_js_opts` / `_from_js_opts` helpers | snake_case ↔ camelCase key conversion + None filtering |
| Record type | `Record<K, V>` → `dict[K, V]` | Inbound: `.to_py()`, outbound: `to_js()` |
| Native type overrides | `NATIVE_TYPES` registry in typeRendering.ts | Custom type annotation + conversion for `Headers`, extensible for `Blob`, `URL`, etc. |
| Headers | `dict[str, str] \| list[tuple[str, str]] \| JsProxy` | Adopted from workers-py; `_to_js_headers` helper converts at call site |
| `import js` | Added to prelude | Required for `js.ClassName.new()` and `js.Headers.new()` |
| Non-global constructors | `js.ClassName` for all, fail at runtime if not global | `declare module` types aren't on `globalThis`; TODO: import from submodules |
| TS lib filtering | Exclude `node_modules/typescript/lib/` files | Prevents JS builtins (Object, Math, String) from generating wrappers |
| `declare class` IR | Single entry with constructors merged | Refactored from upstream's two-entry split (`ClassName` + `ClassName_iface`) |

## Type Classification

The renderer classifies interfaces into three categories:

| Category | Detection | Rendering | Example |
|----------|-----------|-----------|---------|
| **Wrapper class** | Has methods, or has constructors | `class` with `_binding`, `from_js`, `__init__` (if constructor) | `R2Bucket`, `HTMLRewriter`, `R2Object` |
| **Data bag (TypedDict)** | Properties only, no methods, no constructors, no reserved-word keys | `TypedDict` with snake_case keys | `R2GetOptions`, `R2Conditional`, `R2UploadedPart` |
| **Duplicate `None`** | `isNullable` check on optional params/properties/kwparams | `= None` without extra `\| None` when type already contains `None` |

## PyProxy Boundary Rules

### Rule 1: dict/list → JS via `to_js()`
Interface/array-typed params get `to_js(param)` inline in the call. Detected by `needsToJs()`.

### Rule 2: Callable → JS via `create_proxy()`
Callable-typed params get `create_proxy(param)`. Detected by `needsCreateProxy()`. Takes priority over `to_js`.

### Rule 3: Data bags → JS via `_to_js_opts()`
TypedDict params use `_to_js_opts()` which converts snake_case keys to camelCase and filters None values.

### Rule 4: Native types → JS via custom helpers
Params with native type overrides (e.g. `Headers`) use custom helpers (e.g. `_to_js_headers`). Only for non-union types; union params fall through to `to_js()`.

### Rule 5: JS null → Python via `_jsnull_to_none()`
Nullable returns (union containing `None`) wrap the call result.

### Rule 6: Data bags ← JS via `_from_js_opts()`
TypedDict-typed returns/properties use `_from_js_opts()` which converts camelCase keys to snake_case.

### Rule 7: Record ← JS via `.to_py()`
`Record<K, V>` returns/properties use `.to_py()` for plain dict conversion.

## Type Rendering Rules

- **Primitives** (`str`, `bool`, `None`, `Any`, `Never`, `int | float`): rendered as-is
- **`Promise<T>`**: kept as `Promise[T]` for async detection; the renderer unwraps it
- **`Record<K, V>`**: rendered as `dict[K, V]`; inbound `.to_py()`, outbound `to_js()`
- **Known interfaces**: reference types matching generated classes render as the class name
- **Native types**: `Headers` → `dict[str, str] | list[tuple[str, str]] | JsProxy` (extensible via `NATIVE_TYPES`)
- **Buffer types**: `ArrayBuffer`, `ArrayBufferLike`, `ArrayBufferView`, TypedArrays → `JsBuffer`
- **All other reference types**: rendered as `Any`
- **Generic type params** (`parameterReference`): rendered as `Any`
- **Callable types**: rendered as `Any`
- **Unknown constructs** (`OtherTypeIR`): rendered as `Any`

## Findings

### Constructor Name Discrepancies
- `KVNamespace` in .d.ts → `KvNamespace` at runtime
- `Queue` in .d.ts → `WorkerQueue` at runtime
- `AnalyticsEngineDataset` in .d.ts → `AnalyticsEngine` at runtime
- `VectorizeIndex` in .d.ts → `VectorizeIndexImpl` at runtime

### IR Extraction Patterns
- `declare class` → single IR entry with `constructors` field (refactored from upstream's two-entry split)
- `declare var X: { prototype: X, new(): X }` + `interface X` → two IR entries (legacy pattern, not yet unified)
- `interface` → IR entry with `_iface` suffix
- `declare module "..."` → classes extracted alongside top-level declarations

## Common Coding conventions

- Do not remove existing comments unless it is obvously redundant.
- Keep the existing code style and formatting.
- Always use uv for Python dependency and package management and testing.
