import { describe, it } from "node:test";
import assert from "node:assert";
import {
  camelToSnake,
  sanitizePythonName,
  toPythonName,
  stripIfaceSuffix,
  jsAttrAccess,
  jsMethodCall,
} from "../src/naming";

describe("camelToSnake", () => {
  const cases: [string, string][] = [
    ["get", "get"],
    ["delete", "delete"],
    ["getWithMetadata", "get_with_metadata"],
    ["arrayBuffer", "array_buffer"],
    ["bodyUsed", "body_used"],
    ["parseHTML", "parse_html"],
    ["getURLList", "get_url_list"],
    ["innerHTML", "inner_html"],
    ["XMLHttpRequest", "xml_http_request"],
    ["r2Bucket", "r2_bucket"],
    ["d1Database", "d1_database"],
    ["kvNamespace", "kv_namespace"],
    ["a", "a"],
    ["A", "a"],
    ["AB", "ab"],
    ["connectionString", "connection_string"],
  ];

  for (const [input, expected] of cases) {
    it(`${input} → ${expected}`, () => {
      assert.strictEqual(camelToSnake(input), expected);
    });
  }
});

describe("sanitizePythonName", () => {
  const cases: [string, string][] = [
    ["get", "get"],
    ["delete", "delete"],
    ["from", "from_"],
    ["del", "del_"],
    ["class", "class_"],
    ["import", "import_"],
    ["type", "type_"],
    ["float", "float"],
    ["match", "match_"],
    ["case", "case_"],
    ["normal_name", "normal_name"],
  ];

  for (const [input, expected] of cases) {
    it(`${input} → ${expected}`, () => {
      assert.strictEqual(sanitizePythonName(input), expected);
    });
  }
});

describe("toPythonName", () => {
  const cases: [string, string][] = [
    ["get", "get"],
    ["getWithMetadata", "get_with_metadata"],
    ["delete", "delete"],
    ["from", "from_"],
    ["connectionString", "connection_string"],
  ];

  for (const [input, expected] of cases) {
    it(`${input} → ${expected}`, () => {
      assert.strictEqual(toPythonName(input), expected);
    });
  }
});

describe("stripIfaceSuffix", () => {
  const cases: [string, string][] = [
    ["KVNamespace_iface", "KVNamespace"],
    ["D1Database_iface", "D1Database"],
    ["Hyperdrive_iface", "Hyperdrive"],
    ["SomeClass", "SomeClass"],
    ["_iface", ""],
    ["iface_iface", "iface"],
  ];

  for (const [input, expected] of cases) {
    it(`${input} → ${expected}`, () => {
      assert.strictEqual(stripIfaceSuffix(input), expected);
    });
  }
});

describe("jsAttrAccess", () => {
  it("normal name", () => {
    assert.strictEqual(
      jsAttrAccess("self._binding", "host"),
      "self._binding.host",
    );
  });

  it("reserved word uses getattr", () => {
    assert.strictEqual(
      jsAttrAccess("self._binding", "from"),
      'getattr(self._binding, "from")',
    );
  });

  it("another reserved", () => {
    assert.strictEqual(jsAttrAccess("obj", "del"), 'getattr(obj, "del")');
  });
});

describe("jsMethodCall", () => {
  it("normal name", () => {
    assert.strictEqual(
      jsMethodCall("self._binding", "get", "key"),
      "self._binding.get(key)",
    );
  });

  it("no args", () => {
    assert.strictEqual(
      jsMethodCall("self._binding", "run", ""),
      "self._binding.run()",
    );
  });

  it("reserved word uses getattr", () => {
    assert.strictEqual(
      jsMethodCall("self._binding", "del", ""),
      'getattr(self._binding, "del")()',
    );
  });

  it("multiple args", () => {
    assert.strictEqual(
      jsMethodCall("self._binding", "put", "key, value"),
      "self._binding.put(key, value)",
    );
  });

  it("pyodide-shadowed send uses _call_js_method", () => {
    assert.strictEqual(
      jsMethodCall("self._binding", "send", "message"),
      '_call_js_method(self._binding, "send", message)',
    );
  });

  it("pyodide-shadowed throw uses _call_js_method", () => {
    assert.strictEqual(
      jsMethodCall("self._binding", "throw", "err"),
      '_call_js_method(self._binding, "throw", err)',
    );
  });

  it("pyodide-shadowed close with no args", () => {
    assert.strictEqual(
      jsMethodCall("self._binding", "close", ""),
      '_call_js_method(self._binding, "close")',
    );
  });
});
