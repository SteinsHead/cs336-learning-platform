const PYODIDE_VERSION = "0.27.7";
let pyodidePromise = null;

function loadRuntime() {
  if (!pyodidePromise) {
    pyodidePromise = (async () => {
      importScripts(`https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/pyodide.js`);
      return self.loadPyodide({ indexURL: `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/` });
    })();
  }
  return pyodidePromise;
}

const TEST_HELPERS = String.raw`
import json as _json
import math as _math

_TEST_RESULTS = []

def _record(name, passed, detail=""):
    _TEST_RESULTS.append({"name": str(name), "passed": bool(passed), "detail": str(detail)})

def _expect(name, actual, expected):
    passed = actual == expected
    _record(name, passed, "" if passed else f"expected {expected!r}, got {actual!r}")

def _expect_close(name, actual, expected, rel_tol=1e-7, abs_tol=1e-9):
    passed = _math.isclose(float(actual), float(expected), rel_tol=rel_tol, abs_tol=abs_tol)
    _record(name, passed, "" if passed else f"expected {expected!r}, got {actual!r}")

def _expect_sequence_close(name, actual, expected, rel_tol=1e-7, abs_tol=1e-9):
    actual = list(actual)
    expected = list(expected)
    passed = len(actual) == len(expected) and all(
        _math.isclose(float(left), float(right), rel_tol=rel_tol, abs_tol=abs_tol)
        for left, right in zip(actual, expected)
    )
    _record(name, passed, "" if passed else f"expected {expected!r}, got {actual!r}")

def _expect_raises(name, operation, error_type=Exception):
    try:
        operation()
    except error_type:
        _record(name, True)
    except Exception as error:
        _record(name, False, f"expected {error_type.__name__}, got {type(error).__name__}: {error}")
    else:
        _record(name, False, f"expected {error_type.__name__}, but no error was raised")
`;

self.onmessage = async (event) => {
  const { id, type, code = "", tests = "" } = event.data || {};
  try {
    const pyodide = await loadRuntime();
    if (type === "init") {
      self.postMessage({ id, ok: true, type: "ready", version: PYODIDE_VERSION });
      return;
    }

    if (type !== "run") throw new Error("Unknown worker request.");
    const stdout = [];
    pyodide.setStdout({ batched: (message) => stdout.push(message) });
    pyodide.setStderr({ batched: (message) => stdout.push(message) });
    const wrappedTests = String(tests)
      .split("\n")
      .map((line) => `    ${line}`)
      .join("\n");
    const program = `${code}\n\n${TEST_HELPERS}\n\ntry:\n${wrappedTests}\nexcept Exception as _test_error:\n    _record("代码执行", False, f"{type(_test_error).__name__}: {_test_error}")\n\n_json.dumps({"tests": _TEST_RESULTS, "passed": sum(1 for item in _TEST_RESULTS if item["passed"]), "total": len(_TEST_RESULTS)})`;
    const raw = await pyodide.runPythonAsync(program);
    const result = JSON.parse(String(raw));
    self.postMessage({ id, ok: true, type: "result", ...result, stdout });
  } catch (error) {
    self.postMessage({ id, ok: false, type: "error", error: String(error?.message || error), stack: String(error?.stack || "") });
  }
};
