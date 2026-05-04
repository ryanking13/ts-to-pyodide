import { describe, it } from "node:test";
import assert from "node:assert";
import { readFileSync } from "fs";
import { resolve } from "path";
import { Renderer } from "../src/renderer";
import { InterfaceIR, CallableIR, SigIR, ParamIR, PropertyIR, TypeIR } from "../src/ir";

const FIXTURES_DIR = resolve(import.meta.dirname!, "fixtures");

function loadFixture(name: string): { ir: InterfaceIR; expected: string } {
  const ir = JSON.parse(
    readFileSync(resolve(FIXTURES_DIR, name, "ir.json"), "utf-8"),
  );
  const expected = readFileSync(
    resolve(FIXTURES_DIR, name, "expected.py"),
    "utf-8",
  );
  return { ir, expected };
}

function irInterface(
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

function irMethod(
  name: string,
  signatures: SigIR[] = [],
  isStatic = false,
): CallableIR {
  return { kind: "callable", name, signatures, isStatic };
}

function irSig(
  params: ParamIR[] = [],
  returns: TypeIR = { kind: "simple", text: "None" },
): SigIR {
  return { params, returns };
}

function irSigWithSpread(
  params: ParamIR[] = [],
  spreadParam: ParamIR | undefined,
  returns: TypeIR = { kind: "simple", text: "None" },
): SigIR {
  return { params, spreadParam, returns };
}

function irParam(
  name: string,
  type: TypeIR,
  isOptional = false,
): ParamIR {
  return { name, type, isOptional };
}

function irProperty(
  name: string,
  type: TypeIR,
  isReadonly = false,
  isOptional = false,
): PropertyIR {
  return { name, type, isReadonly, isOptional, isStatic: false };
}

function promiseOf(inner: TypeIR): TypeIR {
  return { kind: "reference", name: "Promise", typeArgs: [inner] };
}

function nullable(inner: TypeIR): TypeIR {
  return { kind: "union", types: [inner, { kind: "simple", text: "None" }] };
}

function callableType(
  params: ParamIR[] = [],
  returns: TypeIR = { kind: "simple", text: "None" },
): TypeIR {
  return { kind: "callable", signatures: [irSig(params, returns)] };
}

const renderer = new Renderer();

describe("fixture tests", () => {
  const fixtures = [
    "sync_method",
    "greeter",
    "math_params",
    "async_delete",
    "readonly_properties",
    "d1database",
    "hyperdrive",
    "overloads",
    "generic_method",
    "sub_binding_property",
  ];

  for (const name of fixtures) {
    it(name, () => {
      const { ir, expected } = loadFixture(name);
      assert.strictEqual(renderer.renderInterface(ir), expected);
    });
  }
});

describe("class structure", () => {
  it("skips __call__", () => {
    const result = renderer.renderInterface(
      irInterface("X_iface", [
        irMethod("__call__", [irSig()]),
        irMethod("real_method", [irSig()]),
      ]),
    );
    assert.ok(!result.includes("__call__"));
    assert.ok(result.includes("real_method"));
  });

  it("strips _iface suffix", () => {
    const result = renderer.renderInterface(irInterface("KVNamespace_iface"));
    assert.ok(result.includes("class KVNamespace:"));
    assert.ok(!result.includes("_iface"));
  });
});

describe("async detection", () => {
  it("Promise<string> unwraps return type", () => {
    const result = renderer.renderInterface(
      irInterface("KV_iface", [
        irMethod("get", [
          irSig(
            [irParam("key", { kind: "simple", text: "str" })],
            promiseOf({ kind: "simple", text: "str" }),
          ),
        ]),
      ]),
    );
    assert.ok(result.includes("async def get(self, key: str) -> str:"));
    assert.ok(result.includes("return await self._binding.get(key)"));
  });

  it("Promise<str | None> unwraps with jsnull_to_none", () => {
    const result = renderer.renderInterface(
      irInterface("KV_iface", [
        irMethod("get", [
          irSig(
            [irParam("key", { kind: "simple", text: "str" })],
            promiseOf(nullable({ kind: "simple", text: "str" })),
          ),
        ]),
      ]),
    );
    assert.ok(result.includes("async def get(self, key: str) -> str | None:"));
    assert.ok(
      result.includes("_jsnull_to_none(await self._binding.get(key))"),
    );
  });

  it("sync method not affected", () => {
    const result = renderer.renderInterface(
      irInterface("D1_iface", [
        irMethod("prepare", [
          irSig(
            [irParam("query", { kind: "simple", text: "str" })],
            { kind: "simple", text: "str" },
          ),
        ]),
      ]),
    );
    assert.ok(!result.includes("async"));
    assert.ok(!result.includes("await"));
  });
});

describe("optional params", () => {
  it("trailing optional", () => {
    const result = renderer.renderInterface(
      irInterface("Vectorize_iface", [
        irMethod("query", [
          irSig(
            [
              irParam("vector", { kind: "simple", text: "Any" }),
              irParam("options", { kind: "simple", text: "Any" }, true),
            ],
            promiseOf({ kind: "simple", text: "Any" }),
          ),
        ]),
      ]),
    );
    assert.ok(
      result.includes(
        "async def query(self, vector: Any, options: Any | None = None) -> Any:",
      ),
    );
  });
});

describe("properties", () => {
  it("writable property has setter", () => {
    const result = renderer.renderInterface(
      irInterface("Config_iface", [], [
        irProperty("name", { kind: "simple", text: "str" }),
      ]),
    );
    assert.ok(result.includes("@property"));
    assert.ok(result.includes("@name.setter"));
    assert.ok(result.includes("self._binding.name = value"));
  });
});

describe("snake_case conversion", () => {
  it("camelCase method", () => {
    const result = renderer.renderInterface(
      irInterface("KV_iface", [
        irMethod("getWithMetadata", [
          irSig(
            [irParam("key", { kind: "simple", text: "str" })],
            promiseOf({ kind: "simple", text: "Any" }),
          ),
        ]),
      ]),
    );
    assert.ok(result.includes("async def get_with_metadata(self, key: str)"));
    assert.ok(result.includes("self._binding.getWithMetadata(key)"));
  });

  it("camelCase property", () => {
    const result = renderer.renderInterface(
      irInterface("Hyperdrive_iface", [], [
        irProperty("connectionString", { kind: "simple", text: "str" }, true),
      ]),
    );
    assert.ok(result.includes("def connection_string(self) -> str:"));
    assert.ok(result.includes("self._binding.connectionString"));
  });

  it("acronym handling", () => {
    const result = renderer.renderInterface(
      irInterface("X_iface", [
        irMethod("parseHTML", [irSig([], { kind: "simple", text: "Any" })]),
        irMethod("getURLList", [irSig([], { kind: "simple", text: "Any" })]),
      ]),
    );
    assert.ok(result.includes("def parse_html(self)"));
    assert.ok(result.includes("def get_url_list(self)"));
  });
});

describe("overloads", () => {
  it("multiple sigs produce @overload stubs + *args impl", () => {
    const { ir } = loadFixture("overloads");
    const result = renderer.renderInterface(ir);
    assert.strictEqual(
      result.split("@overload").length - 1,
      2,
    );
    assert.ok(
      result.includes("async def first(self, col_name: str) -> Any | None: ..."),
    );
    assert.ok(result.includes("async def first(self) -> Any | None: ..."));
    assert.ok(
      result.includes(
        "async def first(self, *args: Any, **kwargs: Any) -> Any:",
      ),
    );
  });

  it("single sig no @overload", () => {
    const result = renderer.renderInterface(
      irInterface("X_iface", [
        irMethod("run", [
          irSig(
            [irParam("query", { kind: "simple", text: "str" })],
            promiseOf({ kind: "simple", text: "Any" }),
          ),
        ]),
      ]),
    );
    assert.ok(!result.includes("@overload"));
  });
});

describe("rest params", () => {
  it("spread param", () => {
    const result = renderer.renderInterface(
      irInterface("Stmt_iface", [
        irMethod("bind", [
          irSigWithSpread(
            [],
            irParam("values", { kind: "simple", text: "Any" }),
            { kind: "simple", text: "Any" },
          ),
        ]),
      ]),
    );
    assert.ok(result.includes("def bind(self, *values: Any) -> Any:"));
    assert.ok(result.includes("self._binding.bind(*values)"));
  });

  it("params plus spread", () => {
    const result = renderer.renderInterface(
      irInterface("X_iface", [
        irMethod("log", [
          irSigWithSpread(
            [irParam("message", { kind: "simple", text: "str" })],
            irParam("args", { kind: "simple", text: "Any" }),
          ),
        ]),
      ]),
    );
    assert.ok(
      result.includes("def log(self, message: str, *args: Any) -> None:"),
    );
    assert.ok(result.includes("self._binding.log(message, *args)"));
  });
});

describe("reserved words", () => {
  it("from property gets underscore + getattr", () => {
    const result = renderer.renderInterface(
      irInterface("Email_iface", [], [
        irProperty("from", { kind: "simple", text: "str" }, true),
      ]),
    );
    assert.ok(result.includes("def from_(self) -> str:"));
    assert.ok(result.includes('getattr(self._binding, "from")'));
  });

  it("del method gets underscore + getattr", () => {
    const result = renderer.renderInterface(
      irInterface("X_iface", [irMethod("del", [irSig()])]),
    );
    assert.ok(result.includes("def del_(self) -> None:"));
    assert.ok(result.includes('getattr(self._binding, "del")()'));
  });
});

describe("nullable returns", () => {
  it("sync nullable wraps with _jsnull_to_none", () => {
    const result = renderer.renderInterface(
      irInterface("D1Session_iface", [
        irMethod("getBookmark", [
          irSig([], nullable({ kind: "simple", text: "str" })),
        ]),
      ]),
    );
    assert.ok(result.includes("def get_bookmark(self) -> str | None:"));
    assert.ok(
      result.includes("_jsnull_to_none(self._binding.getBookmark())"),
    );
  });

  it("non-nullable not wrapped", () => {
    const result = renderer.renderInterface(
      irInterface("KV_iface", [
        irMethod("delete", [
          irSig(
            [irParam("key", { kind: "simple", text: "str" })],
            promiseOf({ kind: "simple", text: "None" }),
          ),
        ]),
      ]),
    );
    assert.ok(!result.includes("_jsnull_to_none"));
  });

  it("nullable property wraps", () => {
    const result = renderer.renderInterface(
      irInterface("R2Object_iface", [], [
        irProperty(
          "httpMetadata",
          { kind: "simple", text: "Any" },
          true,
          true,
        ),
      ]),
    );
    assert.ok(
      result.includes("_jsnull_to_none(self._binding.httpMetadata)"),
    );
  });
});

describe("arg conversion", () => {
  it("interface-typed param gets to_js", () => {
    const result = renderer.renderInterface(
      irInterface("KV_iface", [
        irMethod("put", [
          irSig(
            [
              irParam("key", { kind: "simple", text: "str" }),
              irParam("value", { kind: "simple", text: "str" }),
              irParam(
                "options",
                { kind: "reference", name: "Opts_iface", typeArgs: [] },
                true,
              ),
            ],
            promiseOf({ kind: "simple", text: "None" }),
          ),
        ]),
      ]),
    );
    assert.ok(result.includes("to_js(options)"));
    assert.ok(!result.includes("to_js(key)"));
  });

  it("primitives not converted", () => {
    const result = renderer.renderInterface(
      irInterface("X_iface", [
        irMethod("f", [
          irSig([
            irParam("name", { kind: "simple", text: "str" }),
            irParam("count", { kind: "number" }),
            irParam("flag", { kind: "simple", text: "bool" }),
          ]),
        ]),
      ]),
    );
    assert.ok(!result.includes("to_js"));
  });
});

describe("callable param conversion", () => {
  it("callable param gets create_proxy", () => {
    const result = renderer.renderInterface(
      irInterface("State_iface", [
        irMethod("blockConcurrencyWhile", [
          irSig(
            [
              irParam(
                "callback",
                callableType([], promiseOf({ kind: "simple", text: "Any" })),
              ),
            ],
            promiseOf({ kind: "simple", text: "Any" }),
          ),
        ]),
      ]),
    );
    assert.ok(result.includes("create_proxy(callback)"));
    assert.ok(!result.includes("to_js"));
  });

  it("mixed callable and regular params", () => {
    const result = renderer.renderInterface(
      irInterface("X_iface", [
        irMethod("on", [
          irSig([
            irParam("selector", { kind: "simple", text: "str" }),
            irParam(
              "handler",
              callableType(
                [irParam("el", { kind: "simple", text: "Any" })],
              ),
            ),
          ]),
        ]),
      ]),
    );
    assert.ok(result.includes("create_proxy(handler)"));
    assert.ok(!result.includes("create_proxy(selector)"));
  });
});

describe("renderFile", () => {
  it("includes prelude with pyodide imports", () => {
    const result = renderer.renderFile([irInterface("X_iface")]);
    assert.ok(result.includes("from typing import Any, overload"));
    assert.ok(result.includes("from pyodide.ffi import JsProxy, create_proxy, to_js"));
    assert.ok(result.includes("def _jsnull_to_none"));
  });

  it("prelude comes before class body", () => {
    const result = renderer.renderFile([irInterface("X_iface")]);
    const preludeEnd = result.indexOf("class X:");
    assert.ok(preludeEnd > 0);
    assert.ok(result.indexOf("from pyodide.ffi import JsProxy") < preludeEnd);
  });

  it("multiple interfaces in one file", () => {
    const result = renderer.renderFile([
      irInterface("A_iface", [irMethod("f", [irSig()])]),
      irInterface("B_iface", [irMethod("g", [irSig()])]),
    ]);
    assert.ok(result.includes("class A:"));
    assert.ok(result.includes("class B:"));
    const classCount = result.split("def __init__").length - 1;
    assert.strictEqual(classCount, 2);
  });
});
