# ts-to-pyodide

Generate Python runtime wrappers from TypeScript `.d.ts` type definitions for [Pyodide](https://pyodide.org/).

Parses `.d.ts` files and produces Python classes that wrap the underlying JS objects via Pyodide's `JsProxy`, giving you typed, Pythonic access to JavaScript objects and functions.

## Install

```bash
npm install -g ts-to-pyodide
```

## Usage

The input directory must contain a `tsconfig.json` and the TypeScript type definitions you want to convert.

### Generate Python wrappers

```bash
npx ts-to-pyodide render <input-dir> <output.py>
```

This produces two files:
- `<output.py>` — the generated wrapper classes
- `prelude.py` — runtime helpers that is imported by `<output.py>` (written next to `<output.py>`)

### Render only specific bindings

Use `--only` to render specific classes and their transitive dependencies:

```bash
npx ts-to-pyodide render <input-dir> <output.py> --only KVNamespace,R2Bucket,D1Database
```

This is useful when working with large type packages like `@cloudflare/workers-types` — instead of generating wrappers for all 700+ interfaces, you get only the ones you need.

### Output raw IR as JSON

```bash
npx ts-to-pyodide ir <input-dir> <output.json>
```

### Example: Cloudflare Workers types

```bash
mkdir my-project && cd my-project

cat > package.json << 'EOF'
{
  "dependencies": {
    "@cloudflare/workers-types": "*",
    "typescript": "~5.3.0"
  }
}
EOF

cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "esnext",
    "module": "esnext",
    "moduleResolution": "nodenext",
    "lib": ["esnext"],
    "types": ["@cloudflare/workers-types"]
  },
  "include": ["node_modules/@cloudflare/workers-types/index.d.ts"]
}
EOF

npm install

# Generate wrappers for KV, R2, and D1 only
npx ts-to-pyodide render . bindings.py --only KVNamespace,R2Bucket,D1Database

# Or generate everything
npx ts-to-pyodide render . bindings.py
```

### Output structure

The generated `bindings.py` imports from `prelude.py` (which is placed alongside it):

```python
from __future__ import annotations
from prelude import *

class KVNamespace:
    _binding: Any

    @classmethod
    def from_js(cls, js_obj: JsProxy) -> KVNamespace:
        ...

    async def get(self, key: str) -> str | None:
        return _jsnull_to_none(await self._binding.get(key))

    async def put(self, key: str, value: str) -> None:
        await self._binding.put(key, value)
    ...
```

### Using the generated wrappers in Pyodide

```python
from bindings import KVNamespace

# Wrap an existing JS binding (e.g. from env)
kv = KVNamespace.from_js(env.MY_KV)

# Use with Python syntax
value = await kv.get("my-key")
await kv.put("my-key", "hello")
```

## Development

```bash
npm install
npm test          # Run all tests
npm run check     # TypeScript type check
npm run build     # Compile to dist/
```
