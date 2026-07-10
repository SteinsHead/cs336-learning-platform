const KEYWORDS = new Set([
  "as", "assert", "async", "await", "break", "class", "continue", "def",
  "del", "elif", "else", "except", "finally", "for", "from", "global",
  "if", "import", "in", "is", "lambda", "nonlocal", "not", "or", "pass",
  "raise", "return", "try", "while", "with", "yield", "and",
]);

const CONSTANTS = new Set(["True", "False", "None", "inf"]);

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function span(kind, value) {
  return `<span class="token-${kind}">${escapeHtml(value)}</span>`;
}

export function highlightPythonLine(line) {
  const source = String(line || "");
  let html = "";
  let index = 0;
  while (index < source.length) {
    const char = source[index];
    if (char === "#") {
      html += span("comment", source.slice(index));
      break;
    }
    if (char === '"' || char === "'") {
      const quote = char;
      let end = index + 1;
      let escaped = false;
      while (end < source.length) {
        const current = source[end];
        if (escaped) {
          escaped = false;
        } else if (current === "\\") {
          escaped = true;
        } else if (current === quote) {
          end += 1;
          break;
        }
        end += 1;
      }
      html += span("string", source.slice(index, end));
      index = end;
      continue;
    }
    const identifier = source.slice(index).match(/^[A-Za-z_][A-Za-z0-9_]*/)?.[0];
    if (identifier) {
      if (KEYWORDS.has(identifier)) html += span("keyword", identifier);
      else if (CONSTANTS.has(identifier)) html += span("constant", identifier);
      else html += escapeHtml(identifier);
      index += identifier.length;
      continue;
    }
    const number = source.slice(index).match(/^\d+(?:\.\d+)?(?:[eE][+-]?\d+)?/)?.[0];
    if (number) {
      html += span("number", number);
      index += number.length;
      continue;
    }
    html += escapeHtml(char);
    index += 1;
  }
  return html;
}
