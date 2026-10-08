# AI Build Prompt

Paste the block below into any capable coding assistant (Kiro, Claude, Cursor,
Copilot Chat, …), together with the three source files (`dashboard.html`,
`dashboard-data.js`, and this folder's `README.md`). It gives the assistant the
full mental model and a safe, test-backed way to extend the dashboard for your
role and wire your real data sources.

---

```
You are extending a single-file personal operations dashboard. Read README.md
first, then dashboard.html and dashboard-data.js. Do not introduce a build step,
a framework, or external runtime dependencies — it must stay a static folder
served over localhost.

ARCHITECTURE (confirm you understand before editing):
- `SECTIONS` (array in dashboard.html) drives the sidebar. Each entry is either
  a table (`type:"table"` with `cols` + `fields`) handled by the generic
  renderTable, or a custom card view (`custom:true`) dispatched in renderCustom
  to a render<Name>(div, db) function.
- Data lives in `SEED_DATA` (dashboard-data.js), one key per section. Renderers
  read db[sectionKey]. Persistence is localStorage, re-seeded whenever
  DATA_VERSION increases or via the Reset Data button.
- Cache-bust LOCKSTEP: DATA_VERSION (JS const) and the `?v=` on the
  dashboard-data.js <script> tag MUST be equal. Bump both together with
  scripts/bump_version.sh after ANY data change, or the browser serves stale
  data silently.

MY ROLE / WORLD (fill this in):
- I am a: <role, e.g. SRE / TAM / PM / consultant / analyst>.
- My "entities" are: <customers / clients / projects / services / assets>.
- My data sources + how to reach them: <e.g. Jira API, GitHub, PagerDuty,
  ServiceNow, Slack, Outlook, a CSV export, an MCP tool named X>.
- Link templates for IDs: tickets -> <url prefix>, cases -> <url prefix>.

TASKS:
1. Re-label SECTIONS and FIELD_LABELS to my world (keep keys stable or update
   every reference). Point the LINKS templates (top of dashboard.html) and the
   idLink/caseLink helpers at my systems.
2. Add any sections I need as either a table (give me cols+fields) or a custom
   card renderer (follow the existing renderIntelCards / renderCases patterns,
   including expandable <details> per source). Reuse the badge/esc helpers.
3. Replace the placeholder SEED_DATA rows with my real (or realistic sample)
   data, matching the documented schemas exactly (especially cases.customers[]
   .windows and intel[] with per-source arrays of {text,id,link,meta}).
4. Implement the daily refresh per cron/refresh_job.md for MY sources: gather
   per entity, synthesise summary+health, write via scripts/data_splice.py
   (and metrics_transform.py for case metrics), then bump_version.sh in
   lockstep. If a source needs interactive auth, make the job flag "needs login"
   instead of writing zeros.

VERIFICATION (do this before claiming done — the renderers build one big HTML
string and only assign innerHTML at the end, so a single undefined reference
blanks a whole tab with no error):
- Run a DOM-less Node harness: stub document.getElementById/createElement/
  querySelector(All), localStorage (incl removeItem), setInterval, matchMedia,
  location; load dashboard-data.js by eval (it is `const SEED_DATA = {...}`, so
  assign globalThis.SEED_DATA or eval the file text into a vm context); then
  call each render<Name> with a fake element and assert it produces non-empty
  HTML and throws nothing. Run this after EVERY edit.
- Confirm bump_version.sh reports lockstep OK.
- Grep for leftover placeholder strings ("Entity Alpha", "example.com", "TCK-")
  so none of the skeleton's dummy data ships.

STYLE: match the existing conventions — compact vanilla JS, theme via the :root
CSS variables only (never hardcode colors; set a background together with its
text color so it works if the palette changes). Keep every list item in the
Intel cards an expandable <details> with the full story.

OUTPUT: the edited files + a one-paragraph summary of what changed and the
harness result. Show diffs for any file you changed with a script/sed rather
than the editor.
```

---

## Why the verification section matters

The renderers assemble their HTML as a single string and only call
`div.innerHTML = h` at the very end. If any expression throws while building
`h` (a typo, a renamed data key, a helper that doesn't exist), the assignment
never runs and **the tab renders blank with no console error you'll notice**.
An HTML/brace lint will not catch it. The only reliable check is to actually
execute each render function against the real data in a headless Node context.
Make your assistant do this on every edit — it is the single most common way
this class of dashboard breaks.
