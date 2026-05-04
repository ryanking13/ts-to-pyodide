# AGENTS.md — ts-to-pyodide

## Project Overview

ts-to-pyodide generates **Python runtime wrappers** from TypeScript `.d.ts` type definitions for Cloudflare Workers bindings. It parses `.d.ts` files into an intermediate representation (IR) using ts-morph, then a TypeScript renderer produces executable Python wrapper classes.

The IR extraction is forked from [pyodide/ts-to-python](https://github.com/pyodide/ts-to-python) (which generates `.pyi` type stubs). We reuse the same IR and parser but have a completely different rendering backend.

## Build System & Commands

- **Package manager**: npm
- **Run all tests**: `npm test`
- **Type check**: `npm run check`
- **Run IR extraction**: `npm run run -- <input-dir> <output.json>`
- **Build**: `npm run build`

## Testing

TDD approach: every feature was added as a failing test first. All tests run via `npm test`.

| File | Purpose |
|------|---------|
| `tests/ir.test.ts` | IR extraction from `.d.ts` |
| `tests/naming.test.ts` | `camelToSnake`, `sanitizePythonName`, `jsAttrAccess`, keyword completeness |
| `tests/typeRendering.test.ts` | `renderType`, `isPromise`, `isNullable`, `needsToJs`, `needsCreateProxy` |
| `tests/renderer.test.ts` | Fixture-based + inline assertion tests for `Renderer` class |
| `tests/e2e.test.ts` | Full pipeline: `.d.ts` → IR → Python, plus known IR gap tests |
| `tests/tycheck.test.ts` | Runs `ty` type checker on generated Python using real `pyodide-py` types |

Test fixtures live in `tests/fixtures/{name}/` with three files each: `input.d.ts`, `ir.json`, `expected.py`.

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
| Change type annotations | `src/typeRendering.ts` |
| Add a new wrapper feature | Add test first (TDD) in `tests/renderer.test.ts` |
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
| Generated prelude | Static, uses real pyodide imports | `from pyodide.ffi import JsProxy, create_proxy, to_js` with `jsnull` try/except guard |
| Type checking | `ty` with pyodide-py in `.venv-ty` | Real type resolution from pyodide stubs |

## Generated Prelude

Every `renderFile()` output starts with:

```python
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
```

- `jsnull` available in pyodide-py ≥0.29 (Python 3.13+), guarded with try/except for 3.12
- `create_proxy` and `to_js` imported from `pyodide.ffi`

## PyProxy Boundary Rules

### Rule 1: dict/list → JS via `to_js()`
Interface/array-typed params get `to_js(param)` inline in the call. Detected by `needsToJs()` — returns true for `reference` and `array` IR types.

### Rule 2: Callable → JS via `create_proxy()`
Callable-typed params get `create_proxy(param)`. Detected by `needsCreateProxy()` — returns true for `callable` IR types. Takes priority over `to_js`.

### Rule 3: JS null → Python via `_jsnull_to_none()`
Nullable returns (union containing `None`) wrap the call result. Detected by `isNullable()`.

## Type Rendering Rules

- **Primitives** (`str`, `bool`, `None`, `Any`, `Never`, `int | float`): rendered as-is
- **`Promise<T>`**: kept as `Promise[T]` for async detection; the renderer unwraps it
- **All other reference types**: rendered as `Any` — includes `ArrayBuffer`, `ReadableStream`, `KVNamespacePutOptions_iface`, etc. These types don't exist in the generated Python.
- **Generic type params** (`parameterReference`): rendered as `Any` — `T` in `Promise<T | null>` becomes `Any | None`
- **Callable types**: rendered as `Any`
- **Unknown constructs** (`OtherTypeIR`): rendered as `Any`

## Known IR Gaps

### `get`/`set` accessor syntax not captured
TypeScript `get body(): ReadableStream` in interfaces uses `GetAccessor` AST nodes, which `astToIR.ts`'s `groupMembers()` doesn't handle. These properties are silently dropped from the IR. Affects: `R2ObjectBody.body`, `R2ObjectBody.bodyUsed`, `WebSocketRequestResponsePair.request/response`, many `Event` properties. Documented with a test in `e2e.test.ts`.

### `declare module` blocks not extracted
Types inside `declare module "cloudflare:*"` blocks (e.g., `Pipeline<T>`, workflow types) are not extracted by `convertFiles()`.

## Findings

### Constructor Name Discrepancies
- `KVNamespace` in .d.ts → `KvNamespace` at runtime
- `Queue` in .d.ts → `WorkerQueue` at runtime
- `AnalyticsEngineDataset` in .d.ts → `AnalyticsEngine` at runtime
- `VectorizeIndex` in .d.ts → `VectorizeIndexImpl` at runtime

### Python Keywords
Hardcoded in `naming.ts` as `PYTHON_KEYWORDS` (35 hard keywords) + `PYTHON_SOFT_KEYWORDS` (`_`, `case`, `match`, `type`). No builtin shadowing protection — method/property names are always behind `self.` so shadowing doesn't apply.

## Common Coding conventions

- Do not remove existing comments unless it is obvously redundant.
- Keep the existing code style and formatting.
- Always use uv for Python dependency and package management and testing.