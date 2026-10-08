#!/usr/bin/env python3
"""
data_splice.py — safely rewrite ONE array inside dashboard-data.js.

dashboard-data.js is NOT pure JSON (it is `const SEED_DATA = { ... }` with
unquoted keys and trailing statements), so we cannot JSON-parse the whole file.
This does a targeted, brace-balanced splice of a single top-level array
(e.g. `intel`, `tickets`, `tasks`) and leaves the rest byte-for-byte intact.
A `.preedit` backup is written before every change.

Usage:
    python3 data_splice.py <dashboard-data.js> <arrayKey> <rows.json>

<rows.json> is a JSON array of row objects. Each row is emitted as a JS object
literal. Nested arrays whose items are objects are emitted as compact
{text,id,link,meta} literals (the shape the Intel renderer understands); other
values are JSON-encoded as-is.

It also stamps a sibling `<arrayKey>Updated` timestamp if one exists in the file
(e.g. `intelUpdated`), else inserts it right after the spliced array.
"""
import sys, json, re, datetime, shutil


def find_array(src, key):
    """Return (start, end) span of `key: [ ... ],` (bare-key form), or None."""
    m = re.search(r'\b' + re.escape(key) + r'\s*:\s*\[', src)
    if not m:
        return None
    i = src.index('[', m.start())
    depth = 0
    j = i
    while j < len(src):
        c = src[j]
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                end = j + 1
                k = end
                while k < len(src) and src[k] in ' \t\r\n':
                    k += 1
                if k < len(src) and src[k] == ',':
                    end = k + 1
                return (m.start(), end)
        j += 1
    return None


def js_val(v):
    """Encode a scalar/array/object as a JS literal (JSON is valid JS)."""
    return json.dumps(v, ensure_ascii=False)


def js_signal_array(arr):
    """Compact {text,id,link,meta} literals for per-source signal lists."""
    out = []
    for x in (arr or []):
        if isinstance(x, str):
            out.append(js_val(x))
        elif isinstance(x, dict):
            parts = [f + ":" + js_val(x[f]) for f in ("text", "id", "link", "meta") if x.get(f) is not None]
            out.append("{" + ",".join(parts) + "}")
        else:
            out.append(js_val(x))
    return "[" + ",".join(out) + "]"


def render_row(r):
    """Emit one row object. Lists-of-objects use the compact signal form."""
    fields = []
    for k, v in r.items():
        if isinstance(v, list) and v and isinstance(v[0], (dict, str)):
            fields.append(k + ":" + js_signal_array(v))
        else:
            fields.append(k + ":" + js_val(v))
    return "  {" + ", ".join(fields) + "}"


def now_iso():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def main():
    if len(sys.argv) != 4:
        print("usage: data_splice.py <dashboard-data.js> <arrayKey> <rows.json>", file=sys.stderr)
        sys.exit(2)
    path, key, rows_json = sys.argv[1], sys.argv[2], sys.argv[3]
    src = open(path, encoding="utf-8").read()
    rows = json.load(open(rows_json, encoding="utf-8"))
    if not isinstance(rows, list):
        print("ERROR: rows.json must be a JSON array", file=sys.stderr)
        sys.exit(1)

    span = find_array(src, key)
    if not span:
        print(f"ERROR: could not locate `{key}: [ ... ]` block", file=sys.stderr)
        sys.exit(1)

    body = ",\n".join(render_row(r) for r in rows)
    new_block = f"{key}: [\n{body}\n],"

    shutil.copy(path, path + ".preedit")
    out = src[:span[0]] + new_block + src[span[1]:]

    stamp_key = key + "Updated"
    if re.search(r'\b' + re.escape(stamp_key) + r'\s*:', out):
        out = re.sub(r'\b' + re.escape(stamp_key) + r'\s*:\s*[^,\n]+',
                     f'{stamp_key}: {js_val(now_iso())}', out, count=1)
    else:
        out = out.replace(new_block, new_block + f"\n{stamp_key}: {js_val(now_iso())},", 1)

    open(path, "w", encoding="utf-8").write(out)
    print(f"OK: wrote {len(rows)} rows to `{key}` and stamped {stamp_key} ({now_iso()})")


if __name__ == "__main__":
    main()
