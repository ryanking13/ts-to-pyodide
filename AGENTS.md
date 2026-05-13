# AGENTS.md — ts-to-pyodide

## Project Overview

ts-to-pyodide generates **Python runtime wrappers** from TypeScript `.d.ts` type definitions for Cloudflare Workers bindings. It parses `.d.ts` files into an intermediate representation (IR) using ts-morph, then a TypeScript renderer produces executable Python wrapper classes.

The IR extraction is forked from [pyodide/ts-to-python](https://github.com/pyodide/ts-to-python) (which generates `.pyi` type stubs). We reuse the same IR and parser but have a completely different rendering backend.

## Build System & Commands

- **Package manager**: npm
- **Run all tests**: `npm test`
- **Type check**: `npm run check`
- **Render Python wrappers**: `npm run run -- render <input-dir> <output.py>`
- **Render selected bindings only**: `npm run run -- render <input-dir> <output.py> --only KVNamespace,R2Bucket,D1Database`
- **Output raw IR JSON**: `npm run run -- ir <input-dir> <output.json>`
- **Build**: `npm run build` (compiles TS to `dist/` and copies `prelude.py`)

## Testing

TDD approach: every feature was added as a failing test first. All tests run via `npm test`.

| File | Purpose |
|------|---------|
| `tests/ir.test.ts` | IR extraction from `.d.ts`, synthetic type promotion/flattening |
| `tests/naming.test.ts` | `camelToSnake`, `sanitizePythonName`, `jsAttrAccess`, reserved word handling |
| `tests/typeRendering.test.ts` | `renderType`, `isPromise`, `isNullable`, `needsToJs`, `needsCreateProxy`, `resolveKnownInterface`, `needsToPy`, Record/Headers rendering |
| `tests/renderer.test.ts` | Fixture-based + inline assertion tests for `Renderer` class |
| `tests/e2e.test.ts` | Full pipeline: `.d.ts` → IR → Python, all fixture-based e2e tests |
| `tests/tycheck.test.ts` | Runs `ty` type checker on generated Python using real `pyodide-py` types + `js.pyi` stub |
| `tests/cli.test.ts` | CLI subcommand tests (`render`, `ir`, `--only`, default, help) |
| `tests/pyodide.test.ts` | Runs generated wrappers in real Pyodide (Node.js), asserts Python-side behavior against mock JS objects |
| `tests/integration.test.ts` | Full pipeline against `@cloudflare/workers-types` npm package (env-gated) |

### Test Fixtures

Fixtures live in `tests/fixtures/{name}/`. Two kinds:

**renderInterface fixtures** (`input.d.ts` + `ir.json` + `expected.py`) — test single class rendering:
`sync_method`, `greeter`, `math_params`, `async_delete`, `readonly_properties`, `hyperdrive`, `overloads`, `generic_method`, `sub_binding_property`, `buffer_types`, `get_accessor`

**renderFile fixtures** (`input.d.ts` + `expected.py`) — test full pipeline with import header, multiple classes, sub-binding wrapping:
`sub_binding_wrap`, `declare_module`, `constructor`, `kwparams`, `r2_bucket`, `images`, `vectorize`, `ai`, `queue`, `kv_namespace`, `d1database`

## Architecture

```
.d.ts files ──→ [ts-morph AST] ──→ [astToIR.ts] ──→ IR ──→ [extract.ts] ──→ adjusted IR ──→ [renderer.ts] ──→ .py wrappers
                                                                                               ↑
                                                              [filter.ts] ──→ subset IR ────────┘  (when --only is used)
```

Output is two files:
- `<output>.py` — generated wrapper classes with `from prelude import *`
- `prelude.py` — runtime helpers, `Headers` wrapper class, re-exported types

### Where to Look

| Task | File |
|------|------|
| Understand the IR schema | `src/ir.ts` |
| Change how TS is parsed to IR | `src/astToIR.ts` |
| Change inline type promotion vs flattening | `src/extract.ts` (`promoteSyntheticTypes`) |
| Change wrapper Python output | `src/renderer.ts` |
| Change naming conventions | `src/naming.ts` |
| Change type annotations / native types | `src/typeRendering.ts` |
| Change CLI behavior | `src/main.ts` |
| Change `--only` dependency filtering | `src/filter.ts` |
| Change runtime helpers / prelude wrapper classes | `src/prelude.py` |
| Add a new wrapper feature | Add test first (TDD) in `tests/renderer.test.ts` or `tests/e2e.test.ts` |
| Add a native type override | Add to `NATIVE_TYPES` in `src/typeRendering.ts` + helper in `src/prelude.py` |
| Add a prelude wrapper class (like Headers) | Add class in `src/prelude.py`, add name to `PRELUDE_CLASSES` in `src/typeRendering.ts`, update `__all__` |
| Debug IR shape for a TS pattern | See `tests/e2e.test.ts` for how to call `convertToIR` inline |

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Single language | TypeScript only | Simpler toolchain, direct IR access with type safety |
| Class naming | Strip `_iface` suffix | IR produces `KVNamespace_iface`, renderer outputs `class KVNamespace` |
| Method naming | camelCase → snake_case | PEP 8 |
| Async detection | `Promise<T>` return → `async def` | Unwrap Promise, return inner type T |
| Overloads | `*args, **kwargs` impl | Forward all args to JS |
| Reserved words | Only hard keywords (`from`, `class`, etc.) | Append `_`, use `getattr()` for JS access. Soft keywords (`type`, `match`, `case`) are valid identifiers. |
| `_js_obj` type | `Any` (not `JsProxy`) | pyodide's `JsProxy` stubs lack `__getattr__`, type checker can't resolve attribute access |
| null/undefined | Always wrap with `_jsnull_to_none` | IR conflates null/undefined/void into `None`; safe overshoot. `jsnull` imported at module level for performance. |
| Arg conversion | Inline in call expression | `to_js(param)` in arg list, not reassigning variable (avoids ty type errors) |
| Prelude | Separate `prelude.py` file | Contains runtime helpers + `Headers` wrapper. Generated code imports via `from prelude import *`. Written alongside output by CLI. |
| Forward references | `from __future__ import annotations` | Lazy annotation evaluation avoids `NameError` when class A references class B defined later |
| Type checking | `ty` with pyodide-py + `js.pyi` stub | Real type resolution; `js` module stub via `--extra-search-path` |
| Constructor support | `declare class` with constructor → `__init__` calling `js.ClassName.new()` | Pyodide's `.new()` maps to JS `Reflect.construct()` |
| `from_js` classmethod | All wrapper types get `from_js(cls, js_obj)` | Wraps existing JsProxy without calling constructor |
| No-constructor types | Interfaces without constructor skip `__init__` | Users interact via `from_js` or sub-binding wrapping |
| Sub-binding wrapping | Wrap via `from_js` classmethod | `D1PreparedStatement.from_js(self._js_obj.prepare(query))` |
| Data bag interfaces | TypedDict with original camelCase keys | Interfaces with only properties, no methods → `TypedDict(total=False)` |
| Options parameters | Keep as TypedDict param, not kwparams | `put(key, value, options: R2PutOptions \| None)` instead of destructuring |
| No key conversion | TypedDict fields keep original JS names | Dropped camelCase↔snake_case conversion entirely. Method/property names on wrapper classes still use snake_case. |
| Record type | `Record<K, V>` → `dict[K, V]` | Inbound: `to_py()`, outbound: `to_js()` |
| Native type overrides | `NATIVE_TYPES` registry in typeRendering.ts | Custom type annotation + conversion for `Date` (datetime). Extensible for `Blob`, `URL`, etc. |
| Headers | Wrapper class in `prelude.py` via `PRELUDE_CLASSES` | Supports constructor from dict/list, in-place mutation (`writeHttpMetadata`), `.js_object` for passthrough |
| Streams | `ReadableStream`, `WritableStream`, `TransformStream` → `JsProxy` | Passthrough via `REFERENCE_TYPE_MAP`. Streams are complex objects best used directly via Pyodide's JsProxy. |
| `to_js()` wrapper unwrap | `hasattr(obj, "_js_obj")` check | `to_js()` in prelude detects wrapper class instances and returns their underlying JsProxy directly |
| `wrapArg` for wrapper classes | Generated wrapper params → `.js_object` unwrap | Non-PRELUDE wrapper class params use `param.js_object`. PRELUDE class params use `isinstance` check for flexibility. |
| Inline anonymous types | Promoted to named TypedDicts | `{color?: string; width?: number}` in a union → `ImageTransformBorder(TypedDict)`. Intersection-based synthetics still flattened. |
| `--only` selective rendering | Seed IR extraction + BFS dependency filter | `convertToIR` seeds requested interfaces; `collectDependencies` in `filter.ts` walks IR references transitively |
| `import js` | Provided by prelude | Required for `js.ClassName.new()` and `js.Headers.new()` |
| Non-global constructors | `js.ClassName` for all, fail at runtime if not global | `declare module` types aren't on `globalThis`; TODO: import from submodules |
| TS lib filtering | Exclude `node_modules/typescript/lib/` files | Prevents JS builtins (Object, Math, String) from generating wrappers |
| `declare class` IR | Single entry with constructors merged | Refactored from upstream's two-entry split (`ClassName` + `ClassName_iface`) |

## Type Classification

The renderer classifies interfaces into three categories:

| Category | Detection | Rendering | Example |
|----------|-----------|-----------|---------|
| **Wrapper class** | Has methods, or has constructors | `class` with `_js_obj`, `from_js`, `js_object`, `__init__` (if constructor) | `R2Bucket`, `R2Object`, `D1Database` |
| **Data bag (TypedDict)** | Properties only, no methods, no constructors, no hard-keyword keys | `TypedDict` with original camelCase keys | `R2GetOptions`, `R2Conditional`, `ImageTransformBorder` |
| **Promoted inline type** | Synthetic type from inline object literal, not intersection-based | Named TypedDict with PascalCase name | `ImageTransformBorder`, `D1MetaTimings` |

## Inline Type Promotion

TypeScript inline object types (e.g. `border?: {color?: string; width?: number}`) are handled by `promoteSyntheticTypes` in `src/extract.ts`:

- **Promotable** (property-level inline objects): has properties, no bases, not intersection-derived → promoted to named TypedDict (e.g. `ImageTransformBorder`)
- **Flattenable** (intersection-based): has bases, or is sig-derived, or has `Intersection` in name → properties merged into parent (old behavior)
- **Union merging**: `border?: {color, width} | {top, bottom, left, right}` → single TypedDict with all fields optional
- **Naming**: `ImageTransform__border__Union0` → strip `__Union\d+`/`__Intersection\d+` → PascalCase parts → `ImageTransformBorder`
- **Nesting**: `ImageTransform__trim__Union0__border__Union1` → `ImageTransformTrimBorder`

## PyProxy Boundary Rules

### Rule 1: dict/list → JS via `to_js()`
Interface/array-typed params get `to_js(param)` inline in the call. `to_js()` also detects wrapper class instances (via `hasattr(obj, "_js_obj")`) and returns their underlying JsProxy.

### Rule 2: Callable → JS via `create_proxy()`
Callable-typed params get `create_proxy(param)`. Detected by `needsCreateProxy()`. Takes priority over `to_js`.

### Rule 3: Data bags → JS via `to_js()`
TypedDict params use `to_js()` with `dict_converter=js.Object.fromEntries` (avoids dict→Map issue on older Pyodide).

### Rule 4: Native types → JS via custom helpers
Params with native type overrides (e.g. `Date`) use custom helpers (e.g. `_to_js_date`). Only for non-union types; union params fall through to `to_js()`.

### Rule 5: Prelude wrapper classes → JS via isinstance check
`Headers`-typed params emit `param.js_object if isinstance(param, Headers) else param` — accepts both wrapper and raw JsProxy.

### Rule 6: Generated wrapper classes → JS via `.js_object`
Non-PRELUDE wrapper class params emit `param.js_object` (or `param.js_object if param is not None else None` for optional).

### Rule 7: JS null → Python via `_jsnull_to_none()`
Nullable returns (union containing `None`) wrap the call result.

### Rule 8: Data bags ← JS via `to_py()`
TypedDict-typed returns/properties use `to_py()` which recursively converts JsProxy→dict/list with `_jsnull_to_none` on values.

### Rule 9: Record ← JS via `to_py()`
`Record<K, V>` returns/properties use `to_py()` for plain dict conversion.

## Type Rendering Rules

- **Primitives** (`str`, `bool`, `None`, `Any`, `Never`, `int | float`): rendered as-is
- **`Promise<T>`**: kept as `Promise[T]` for async detection; the renderer unwraps it
- **`Record<K, V>`**: rendered as `dict[K, V]`; inbound `to_py()`, outbound `to_js()`
- **Known interfaces**: reference types matching generated classes or PRELUDE_CLASSES render as the class name
- **Native types**: `Date` → `datetime` (extensible via `NATIVE_TYPES`)
- **Prelude classes**: `Headers` → `Headers` (wrapper class in prelude, registered via `PRELUDE_CLASSES`)
- **Buffer types**: `ArrayBuffer`, `ArrayBufferLike`, `ArrayBufferView`, TypedArrays → `JsBuffer`
- **Stream types**: `ReadableStream`, `WritableStream`, `TransformStream` → `JsProxy`
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
- `--only` flag seeds the IR extraction with requested interfaces via `convertToIR(files, seedInterfaces)`

## Common Coding conventions

- Do not remove existing comments unless it is obviously redundant.
- Keep the existing code style and formatting.
- Always use uv for Python dependency and package management and testing.
- When a user asks to create a test fixture from existing types e.g. @cloudflare/workers-types,
  make sure to copy the exact same type from the source, not parse and recreate it.
