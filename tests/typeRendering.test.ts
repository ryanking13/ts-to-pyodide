import { describe, it } from "node:test";
import assert from "node:assert";
import {
  buildKnownInterfacesMap,
  renderType,
  resolveKnownInterface,
  isPromise,
  unwrapPromise,
  isVoidReturn,
  isNullable,
  needsCreateProxy,
  needsToJs,
} from "../src/typeRendering";
import { TypeIR } from "../src/ir";

describe("renderType", () => {
  const basicCases: [TypeIR, string][] = [
    [{ kind: "simple", text: "str" }, "str"],
    [{ kind: "simple", text: "bool" }, "bool"],
    [{ kind: "simple", text: "None" }, "None"],
    [{ kind: "simple", text: "Any" }, "Any"],
    [{ kind: "number" }, "int | float"],
    [{ kind: "other", nodeKind: "x", location: "y" }, "Any"],
    [{ kind: "parameterReference", name: "T" }, "Any"],
  ];

  for (const [input, expected] of basicCases) {
    it(`${input.kind} → ${expected}`, () => {
      assert.strictEqual(renderType(input), expected);
    });
  }

  it("callable → Any", () => {
    const ir: TypeIR = { kind: "callable", signatures: [] };
    assert.strictEqual(renderType(ir), "Any");
  });

  it("union", () => {
    const ir: TypeIR = {
      kind: "union",
      types: [
        { kind: "simple", text: "str" },
        { kind: "simple", text: "None" },
      ],
    };
    assert.strictEqual(renderType(ir), "str | None");
  });

  it("array", () => {
    const ir: TypeIR = { kind: "array", type: { kind: "simple", text: "str" } };
    assert.strictEqual(renderType(ir), "list[str]");
  });

  it("tuple", () => {
    const ir: TypeIR = {
      kind: "tuple",
      types: [{ kind: "simple", text: "str" }, { kind: "number" }],
    };
    assert.strictEqual(renderType(ir), "tuple[str, int | float]");
  });

  it("reference no args renders as Any", () => {
    const ir: TypeIR = { kind: "reference", name: "KVNamespace", typeArgs: [] };
    assert.strictEqual(renderType(ir), "Any");
  });

  it("Promise reference with args keeps name", () => {
    const ir: TypeIR = {
      kind: "reference",
      name: "Promise",
      typeArgs: [{ kind: "simple", text: "str" }],
    };
    assert.strictEqual(renderType(ir), "Promise[str]");
  });

  it("non-Promise reference renders as Any", () => {
    const ir: TypeIR = {
      kind: "reference",
      name: "SomeInterface",
      typeArgs: [{ kind: "simple", text: "str" }],
    };
    assert.strictEqual(renderType(ir), "Any");
  });

  it("Record<string, string> renders as dict[str, str]", () => {
    const ir: TypeIR = {
      kind: "reference",
      name: "Record",
      typeArgs: [
        { kind: "simple", text: "str" },
        { kind: "simple", text: "str" },
      ],
    };
    assert.strictEqual(renderType(ir), "dict[str, str]");
  });

  it("Record<string, number> renders as dict[str, int | float]", () => {
    const ir: TypeIR = {
      kind: "reference",
      name: "Record",
      typeArgs: [
        { kind: "simple", text: "str" },
        { kind: "number" },
      ],
    };
    assert.strictEqual(renderType(ir), "dict[str, int | float]");
  });

  it("Headers renders as class name via knownInterfaces", () => {
    const ir: TypeIR = {
      kind: "reference",
      name: "Headers",
      typeArgs: [],
    };
    const known = new Map([["Headers", "Headers"]]);
    assert.strictEqual(renderType(ir, known), "Headers");
  });

  it("paren", () => {
    const ir: TypeIR = { kind: "paren", type: { kind: "simple", text: "str" } };
    assert.strictEqual(renderType(ir), "(str)");
  });

  it("operator strips to inner", () => {
    const ir: TypeIR = {
      kind: "operator",
      operatorName: "readonly",
      type: { kind: "array", type: { kind: "simple", text: "str" } },
    };
    assert.strictEqual(renderType(ir), "list[str]");
  });

  it("spread", () => {
    const ir: TypeIR = { kind: "spread", type: { kind: "simple", text: "str" } };
    assert.strictEqual(renderType(ir), "*str");
  });

  it("ArrayBuffer renders as JsBuffer", () => {
    const ir: TypeIR = { kind: "reference", name: "ArrayBuffer", typeArgs: [] };
    assert.strictEqual(renderType(ir), "JsBuffer");
  });

  it("Uint8Array renders as JsBuffer", () => {
    const ir: TypeIR = { kind: "reference", name: "Uint8Array", typeArgs: [] };
    assert.strictEqual(renderType(ir), "JsBuffer");
  });

  it("Float64Array renders as JsBuffer", () => {
    const ir: TypeIR = { kind: "reference", name: "Float64Array", typeArgs: [] };
    assert.strictEqual(renderType(ir), "JsBuffer");
  });

  it("known interface reference renders as class name", () => {
    const known = buildKnownInterfacesMap(["Videos_iface"]);
    const ir: TypeIR = { kind: "reference", name: "Videos_iface", typeArgs: [] };
    assert.strictEqual(renderType(ir, known), "Videos");
  });

  it("unknown interface reference still renders as Any", () => {
    const known = buildKnownInterfacesMap(["Videos_iface"]);
    const ir: TypeIR = { kind: "reference", name: "Other_iface", typeArgs: [] };
    assert.strictEqual(renderType(ir, known), "Any");
  });

  it("union with known interface renders class name", () => {
    const known = buildKnownInterfacesMap(["Item_iface"]);
    const ir: TypeIR = {
      kind: "union",
      types: [
        { kind: "reference", name: "Item_iface", typeArgs: [] },
        { kind: "simple", text: "None" },
      ],
    };
    assert.strictEqual(renderType(ir, known), "Item | None");
  });
});

describe("resolveKnownInterface", () => {
  const known = buildKnownInterfacesMap(["Videos_iface", "Item_iface"]);

  it("direct reference resolves", () => {
    assert.strictEqual(
      resolveKnownInterface({ kind: "reference", name: "Videos_iface", typeArgs: [] }, known),
      "Videos",
    );
  });

  it("nullable union with known reference resolves", () => {
    assert.strictEqual(
      resolveKnownInterface(
        { kind: "union", types: [
          { kind: "reference", name: "Item_iface", typeArgs: [] },
          { kind: "simple", text: "None" },
        ] },
        known,
      ),
      "Item",
    );
  });

  it("unknown reference returns undefined", () => {
    assert.strictEqual(
      resolveKnownInterface({ kind: "reference", name: "Other", typeArgs: [] }, known),
      undefined,
    );
  });

  it("simple type returns undefined", () => {
    assert.strictEqual(
      resolveKnownInterface({ kind: "simple", text: "str" }, known),
      undefined,
    );
  });

  it("union with multiple non-None types returns undefined", () => {
    assert.strictEqual(
      resolveKnownInterface(
        { kind: "union", types: [
          { kind: "reference", name: "Videos_iface", typeArgs: [] },
          { kind: "reference", name: "Item_iface", typeArgs: [] },
        ] },
        known,
      ),
      undefined,
    );
  });
});

describe("isPromise", () => {
  it("Promise reference", () => {
    assert.ok(isPromise({ kind: "reference", name: "Promise", typeArgs: [] }));
  });
  it("Promise_iface reference", () => {
    assert.ok(
      isPromise({ kind: "reference", name: "Promise_iface", typeArgs: [] }),
    );
  });
  it("non-Promise reference", () => {
    assert.ok(
      !isPromise({ kind: "reference", name: "KVNamespace", typeArgs: [] }),
    );
  });
  it("simple type", () => {
    assert.ok(!isPromise({ kind: "simple", text: "str" }));
  });
});

describe("unwrapPromise", () => {
  it("with arg", () => {
    const ir: TypeIR = {
      kind: "reference",
      name: "Promise",
      typeArgs: [{ kind: "simple", text: "str" }],
    };
    assert.deepStrictEqual(unwrapPromise(ir), { kind: "simple", text: "str" });
  });
  it("no args", () => {
    const ir: TypeIR = { kind: "reference", name: "Promise", typeArgs: [] };
    assert.deepStrictEqual(unwrapPromise(ir), {
      kind: "simple",
      text: "None",
    });
  });
});

describe("isVoidReturn", () => {
  it("None is void", () => {
    assert.ok(isVoidReturn({ kind: "simple", text: "None" }));
  });
  it("str is not void", () => {
    assert.ok(!isVoidReturn({ kind: "simple", text: "str" }));
  });
  it("number is not void", () => {
    assert.ok(!isVoidReturn({ kind: "number" }));
  });
});

describe("isNullable", () => {
  it("union with None", () => {
    assert.ok(
      isNullable({
        kind: "union",
        types: [
          { kind: "simple", text: "str" },
          { kind: "simple", text: "None" },
        ],
      }),
    );
  });
  it("union without None", () => {
    assert.ok(
      !isNullable({
        kind: "union",
        types: [{ kind: "simple", text: "str" }, { kind: "number" }],
      }),
    );
  });
  it("non-union", () => {
    assert.ok(!isNullable({ kind: "simple", text: "str" }));
    assert.ok(!isNullable({ kind: "simple", text: "None" }));
  });
});

describe("needsCreateProxy", () => {
  it("callable", () => {
    assert.ok(needsCreateProxy({ kind: "callable", signatures: [] }));
  });
  it("union with callable", () => {
    assert.ok(
      needsCreateProxy({
        kind: "union",
        types: [
          { kind: "callable", signatures: [] },
          { kind: "simple", text: "None" },
        ],
      }),
    );
  });
  it("reference", () => {
    assert.ok(
      !needsCreateProxy({ kind: "reference", name: "X", typeArgs: [] }),
    );
  });
  it("simple", () => {
    assert.ok(!needsCreateProxy({ kind: "simple", text: "str" }));
  });
});

describe("needsToJs", () => {
  it("reference needs conversion", () => {
    assert.ok(
      needsToJs({ kind: "reference", name: "Options_iface", typeArgs: [] }),
    );
  });
  it("array needs conversion", () => {
    assert.ok(
      needsToJs({ kind: "array", type: { kind: "simple", text: "Any" } }),
    );
  });
  it("union with reference", () => {
    assert.ok(
      needsToJs({
        kind: "union",
        types: [
          { kind: "simple", text: "str" },
          { kind: "reference", name: "ArrayBuffer", typeArgs: [] },
        ],
      }),
    );
  });

  for (const text of ["str", "bool", "None", "Any", "Never"]) {
    it(`primitive ${text} no conversion`, () => {
      assert.ok(!needsToJs({ kind: "simple", text }));
    });
  }

  it("number no conversion", () => {
    assert.ok(!needsToJs({ kind: "number" }));
  });
  it("other no conversion", () => {
    assert.ok(!needsToJs({ kind: "other", nodeKind: "x", location: "y" }));
  });
  it("callable no conversion (uses create_proxy instead)", () => {
    assert.ok(!needsToJs({ kind: "callable", signatures: [] }));
  });
  it("union all primitives no conversion", () => {
    assert.ok(
      !needsToJs({
        kind: "union",
        types: [
          { kind: "simple", text: "str" },
          { kind: "simple", text: "None" },
        ],
      }),
    );
  });
});
