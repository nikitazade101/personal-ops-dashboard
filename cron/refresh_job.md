# Daily Refresh Job — spec

The dashboard is static; a scheduled job keeps it fresh. This describes what the
job does each run, so you can implement it as a cron + script, a CI job, or an
**AI agent cron** (recommended when your sources need interactive auth and are
only reachable through MCP/agent tools rather than a plain HTTP API).

## Trigger
- Schedule: once each working morning (e.g. `07:45` your timezone), + manual run.
- Keep it hidden/quiet; it only edits files.

## Steps each run

1. **Gather, per entity, from your sources.** Examples (map to your world):
   - Tickets assigned to you → ticketing API/MCP (Jira, ServiceNow, Linear, SIM…)
   - Open cases/incidents per entity → support/incident tool (metrics + optional live list)
   - Tasks → task tracker (Asana, Jira, Trello…)
   - Messages → chat (Slack/Teams) — notable mentions/threads per entity channel
   - Email/meeting summaries → mail/calendar
   - (Skip any source with no API — note "no access" rather than writing zeros.)

2. **Synthesise** a short one-line `summary` and a `health` (GREEN/AMBER/RED)
   per entity from the gathered signal. Keep raw lists small (top N per source).

3. **Write the data file** (never the HTML):
   - Cases metrics → `scripts/metrics_transform.py dashboard-data.js <Name> <payload.json> …`
   - Intel rows → write a `rows.json` array, then
     `scripts/data_splice.py dashboard-data.js intel rows.json`
   - Tickets / tasks the same way:
     `scripts/data_splice.py dashboard-data.js tickets tickets.json`
   - Also stamp freshness: `data_splice` auto-writes `<key>Updated`; set
     `generatedAt` similarly if you want the Overview stale-banner anchored to it.

4. **Bump the cache-bust in LOCKSTEP** — the one mandatory step:
   `bash scripts/bump_version.sh dashboard.html`
   It reads the current version, writes N+1 to BOTH `DATA_VERSION` and the
   `?v=` script tag, and verifies they match. **Fail the run if it mismatches.**

5. **Verify** the data file still parses as JS (a quick `node --check`-style
   load, or `node -e "require('./dashboard-data.js')"` won't work for a bare
   `const` — instead `node -e "global.SEED_DATA=null; eval(require('fs').readFileSync('dashboard-data.js','utf8')); if(!SEED_DATA) process.exit(1)"`).
   `data_splice.py` leaves a `.preedit` backup; restore it on verify failure.

6. **Report only real changes** (new high-sev case, a crossed threshold, an
   auth gap). A quiet run is a successful run — don't notify "nothing new".

## Auth note
If a source needs interactive login (SSO/2FA), a headless cron can't tap it.
Either (a) run as an agent cron that inherits a live session, or (b) have the
job detect the auth failure, leave prior data in place, and flag "needs login"
rather than overwriting good data with zeros.
