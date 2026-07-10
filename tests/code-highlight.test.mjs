import assert from "node:assert/strict";
import test from "node:test";

import { highlightPythonLine } from "../frontend/code-highlight.js";

test("highlights tokens without rewriting generated markup", () => {
  const html = highlightPythonLine('def greet(name="Ada"): # hello');
  assert.match(html, /token-keyword">def<\/span>/);
  assert.match(html, /token-string">&quot;Ada&quot;<\/span>/);
  assert.match(html, /token-comment"># hello<\/span>/);
  assert.equal(html.includes('class=<span class="token-string"'), false);
});

test("escapes code before emitting highlighted spans", () => {
  const html = highlightPythonLine('value = "<script>&"');
  assert.equal(html.includes("<script>"), false);
  assert.match(html, /&lt;script&gt;&amp;/);
});

test("does not treat a comment marker inside a string as a comment", () => {
  const html = highlightPythonLine('message = "# not a comment"');
  assert.equal(html.includes("token-comment"), false);
  assert.match(html, /token-string/);
});
