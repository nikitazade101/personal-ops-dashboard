# Personal Ops Dashboard — Skeleton

A single-file, zero-build **personal operations dashboard** you can adapt to any
role. It renders a sidebar of configurable sections (tables + rich cards),
persists edits in the browser's `localStorage`, and is **re-seeded from a plain
data file** that an automation (cron/agent/script) can rewrite on a schedule.

It was abstracted from a working dashboard into a clean, anonymized skeleton:
**no real names, IDs, URLs, or org-specific data** — just the architecture,
the logic, and the automation pattern, plus an AI build prompt so any assistant
can extend it for you.

> Think of it as a "personal control plane": one page that pulls together your
> tasks, tickets, cases, meetings, intel, projects and quick links, refreshed
> automatically each morning by a background job.

---

## What's in the box

| File | Purpose |
|---|---|
| `dashboard.html` | The entire UI + logic (HTML/CSS/vanilla JS, no framework, no build step). |
| `dashboard-data.js` | The **seed data**. A `SEED_DATA` object the page loads on first run and after a version bump. Automation rewrites this file. |
| `scripts/data_splice.py` | Safe, brace-balanced splicer that rewrites ONE array/object inside `dashboard-data.js` without JSON-parsing the whole (non-JSON) file. |
| `scripts/metrics_transform.py` | Example transform: folds raw per-source API payloads into a dashboard schema (`entities[]`). Model your own source transforms on this. |
| `scripts/bump_version.sh` | Bumps the cache-bust version in **lockstep** (the one gotcha — see below). |
| `scripts/serve.sh` | Serves the folder on `127.0.0.1` (localhost-only) for local viewing. |
| `AI_BUILD_PROMPT.md` | A ready-to-paste prompt so any AI agent can extend this skeleton for your role and wire your real data sources. |
| `cron/refresh_job.md` | The daily-refresh job spec (what a scheduler/agent should do each run). |
| `theme-dark.css` | Optional **dark variant** — a drop-in `:root` palette swap. One `<link>` line re-themes the whole app (also supports OS-driven or a runtime toggle). See the file header. |
| `.github/workflows/refresh.yml` | Sample **GitHub Actions** workflow implementing the refresh job (schedule → gather → splice → lockstep-bump → verify → commit). Template gather steps to replace with your sources. |

---

## 30-second start

```bash
cd dashboard-skeleton
bash scripts/serve.sh 8899        # serves on http://127.0.0.1:8899
# open http://127.0.0.1:8899/dashboard.html
```

Edit any row inline (✏️ / 🗑️ / **+ Add**), or edit `dashboard-data.js` directly
and bump the version (below) to re-seed.

---

## Core architecture (how it actually works)

1. **One config array drives everything.** `SECTIONS` in `dashboard.html` lists
   every sidebar entry. Each entry is either:
   - a **table** (`type:"table"`) — declare `cols` (display) and `fields` (edit
     form); the generic `renderTable` handles sort, add, edit, delete, CSV; or
   - a **custom** card view (`custom:true`) — dispatched in `renderCustom(key,…)`
     to a `render<Thing>` function.

   Add a section = add one line to `SECTIONS` (+ a `render` fn if custom). No
   other wiring.

2. **Data model = one plain object.** `SEED_DATA` holds one key per section
   (`entities`, `tasks`, `tickets`, `intel`, `projects`, `links`, …). Renderers
   read `db[sectionKey]`.

3. **Persistence = localStorage, re-seedable.** `load()` reads from
   localStorage; on first run (or when `DATA_VERSION` increases) it re-seeds from
   `SEED_DATA`. The **Reset Data** button forces a re-seed. This is what lets a
   background job rewrite `dashboard-data.js` and have the browser pick it up.

4. **Automation rewrites the data file, not the HTML.** A scheduled job pulls
   from your sources, synthesises per-entity rows, and splices them into
   `dashboard-data.js` using `scripts/data_splice.py`. See `cron/refresh_job.md`.

5. **Overview + Intel** are the two "synthesis" views: the Overview shows KPIs
   and a "This Week" agenda; the Intel view shows one rich card per entity with
   expandable per-source sections (tasks, tickets, messages, email, risks,
   highlights). Everything else is a straightforward table or card list.

---

## The one gotcha: cache-bust **lockstep**

The browser caches `dashboard-data.js`. Two values must be bumped **together**
every time the data changes, or the page serves stale data:

- `DATA_VERSION = N` (JS constant in `dashboard.html`)
- `<script src="dashboard-data.js?v=N">` (query string in the same file)

If they drift, the page shows old data with no error. Always bump both:

```bash
bash scripts/bump_version.sh dashboard.html   # reads current N, writes N+1 to BOTH, verifies they match
```

Any automation that writes `dashboard-data.js` **must** run this (or an
equivalent lockstep bump) at the end of its run.

---

## Make it yours (any role)

- Rename sections in `SECTIONS` to your world (support cases → incidents,
  customers → clients/projects/teams/assets, SIMs → Jira issues, etc.).
- Point the badges/links helpers (`idLink`, `caseLink`) at **your** systems
  (Jira, GitHub, ServiceNow, Linear …) — they're one-liners near the top.
- Define your sources in `cron/refresh_job.md` and let the AI prompt wire them.

Nothing here is tied to any particular employer, product, or tool — swap the
labels and link templates and it's your dashboard.

---

## Safety notes

- `serve.sh` binds to `127.0.0.1` only. Never expose this on `0.0.0.0`.
- `dashboard-data.js` is plain text — don't put secrets/tokens in it. It holds
  display data only; credentials belong in your automation's environment.
- `data_splice.py` writes a `.preedit` backup before every edit.
