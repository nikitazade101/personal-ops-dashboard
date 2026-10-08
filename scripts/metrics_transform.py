#!/usr/bin/env python3
"""
metrics_transform.py — EXAMPLE: fold raw per-entity source payloads into the
dashboard's `cases` object schema, then splice it into dashboard-data.js.

This is a worked template for a "source transform". Your real source (a
ticketing API, a support-case export, an incident tool, a CSV, …) will return a
different shape — adapt `parse_payload` to it. The OUTPUT shape is what the
dashboard's Cases tab + Intel cards expect:

  cases.customers[] = {
    name, liveCases: [],
    windows: { "7d":{sev1..5,total,avgDays}, "30d":{...}, "90d":{...}, "ytd":{...} },
    topServices: [ {service, total}, ... ]   # ranked, top 8
  }

Usage:
    python3 metrics_transform.py <dashboard-data.js> <Name1> <payload1.json> [<Name2> <payload2.json> ...]

Each payload file is the raw JSON your source returns for that entity.
Here we assume a generic shape of per-service rows with severity counts per
window; EDIT the field names in parse_payload to match your source.
"""
import json, sys, re
from datetime import datetime, timezone

# Map your source's window keys -> the dashboard's short keys.
WIN_MAP = {"last7Days": "7d", "last30Days": "30d", "last90Days": "90d", "yearToDate": "ytd"}


def find_object(src, key):
    """Return (start, end) span of `key: { ... },` by matching BALANCED braces.

    A regex cannot do this safely — nested arrays/objects fool `.*?`. We walk
    from the opening `{` and track brace depth to find its true close, then
    swallow a trailing comma. This is why the splice is reliable.
    """
    m = re.search(r'\b' + re.escape(key) + r'\s*:\s*\{', src)
    if not m:
        return None
    i = src.index('{', m.start())
    depth = 0
    j = i
    while j < len(src):
        c = src[j]
        if c == '{':
            depth += 1
        elif c == '}':
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


def parse_payload(raw):
    """raw = dict from your source API. Returns {windows, topServices}.

    EXPECTED EXAMPLE INPUT (edit to match your real source):
      { "services": [
          { "service": "Compute",
            "metrics": {
              "last30Days": { "total": 8, "severity": {"1":0,"2":1,"3":3,"4":4,"5":0}, "avgDurationDays": 6.0 },
              "yearToDate": { "total": 46 }, ... } }, ... ] }
    """
    windows = {k: {"sev1": 0, "sev2": 0, "sev3": 0, "sev4": 0, "sev5": 0,
                   "total": 0, "_durSum": 0.0, "_durN": 0} for k in WIN_MAP.values()}
    services = []
    for svc in raw.get("services", []):
        name = svc.get("service", "?")
        metrics = svc.get("metrics", {})
        ytd_total = 0
        for api_win, short_win in WIN_MAP.items():
            w = metrics.get(api_win, {})
            tot = w.get("total", 0) or 0
            windows[short_win]["total"] += tot
            sev = w.get("severity", {}) or {}
            for i in range(1, 6):
                windows[short_win][f"sev{i}"] += int(sev.get(str(i), 0) or 0)
            avg = w.get("avgDurationDays")
            if avg is not None and tot:
                windows[short_win]["_durSum"] += avg * tot
                windows[short_win]["_durN"] += tot
            if short_win == "ytd":
                ytd_total = tot
        if ytd_total:
            services.append({"service": name, "total": ytd_total})
    for w in windows.values():
        w["avgDays"] = round(w["_durSum"] / w["_durN"], 1) if w["_durN"] else None
        del w["_durSum"]; del w["_durN"]
    services.sort(key=lambda s: -s["total"])
    return {"windows": windows, "topServices": services[:8], "liveCases": []}


def main():
    if len(sys.argv) < 4 or (len(sys.argv) - 2) % 2 != 0:
        print("usage: metrics_transform.py <dashboard-data.js> <Name> <payload.json> [...]", file=sys.stderr)
        sys.exit(2)
    data_js = sys.argv[1]
    pairs = sys.argv[2:]
    customers = []
    for i in range(0, len(pairs), 2):
        name, pfile = pairs[i], pairs[i + 1]
        raw = json.load(open(pfile, encoding="utf-8"))
        c = parse_payload(raw)
        c["name"] = name
        customers.append(c)

    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    cases_obj = {"updated": now, "liveUpdated": None, "customers": customers}

    src = open(data_js, encoding="utf-8").read()
    block = "cases: " + json.dumps(cases_obj, ensure_ascii=False).replace("\n", "") + ","

    span = find_object(src, "cases")
    if not span:
        print("ERROR: could not locate `cases: { ... }` block", file=sys.stderr)
        sys.exit(1)

    import shutil
    shutil.copy(data_js, data_js + ".preedit")
    out = src[:span[0]] + block + src[span[1]:]
    open(data_js, "w", encoding="utf-8").write(out)
    print(f"OK: wrote {len(customers)} entities to cases ({now})")


if __name__ == "__main__":
    main()
