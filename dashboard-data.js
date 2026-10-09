/* =============================================================================
 * dashboard-data.js  —  SEED DATA (anonymized placeholders)
 * -----------------------------------------------------------------------------
 * This file is NOT pure JSON — it is a JS module that defines `SEED_DATA`.
 * The dashboard loads it on first run (and whenever DATA_VERSION increases).
 *
 * A background refresh job rewrites the `cases`, `intel`, `tasks` and
 * `tickets` sections here using scripts/data_splice.py, then bumps the
 * cache-bust version in LOCKSTEP (scripts/bump_version.sh).
 *
 * One top-level key per section (matches SECTIONS[].key in dashboard.html).
 * All names/IDs/URLs below are fictional placeholders — replace with your own.
 * ========================================================================== */
const SEED_DATA = {

  /* owner identity (shown in the Overview hero) */
  ownerName: "Alex Doe",
  ownerAlias: "adoe",

  /* freshness stamp — the stale-data banner reads this */
  generatedAt: null,

  /* -- Entities: your tracked customers / clients / projects / assets ------- */
  entities: [
    { name:"Entity Alpha",  kind:"Customer", role:"Primary",   allocation:0.40, tags:"compute, storage", region:"EU",   start:"2026-01-01", end:"2026-12-31", status:"active",    ticket:"TCK-1001", notes:"Flagship account." },
    { name:"Entity Bravo",  kind:"Customer", role:"Secondary", allocation:0.15, tags:"data, analytics",  region:"US",   start:"2026-03-01", end:"2026-12-31", status:"active",    ticket:"TCK-1002", notes:"" },
    { name:"Entity Charlie",kind:"Project",  role:"Owner",     allocation:0.10, tags:"platform",         region:"APAC", start:"2026-02-15", end:"2026-09-30", status:"active",    ticket:"TCK-1003", notes:"" },
    { name:"Entity Delta",  kind:"Customer", role:"Standby",   allocation:0.05, tags:"networking",       region:"EU",   start:"2026-05-01", end:"2026-12-31", status:"active",    ticket:"TCK-1004", notes:"" },
    { name:"Entity Echo",   kind:"Client",   role:"Secondary", allocation:0.08, tags:"security",         region:"US",   start:"2025-11-01", end:"2026-04-30", status:"completed", ticket:"TCK-1005", notes:"Wrapped Q2." }
  ],

  /* -- Daily Tasks: auto-compiled, grouped by `source` --------------------- */
  tasksUpdated: null,
  tasks: [
    { source:"Message", text:"Review the migration proposal thread",       from:"#team-alpha", priority:"High",   link:"https://example.com/thread/1" },
    { source:"Ticket",  text:"TCK-1001 — latency spike needs triage",        priority:"P2",     link:"https://example.com/issue/TCK-1001" },
    { source:"Task",    text:"Draft the weekly report for Entity Bravo",     priority:"",       link:"" },
    { source:"Email",   text:"Meeting summary: Entity Alpha quarterly sync", from:"calendar",   link:"" }
  ],

  /* -- Cases: aggregated metrics per entity (rewritten by refresh job) ------ *
   * windows: 7d / 30d / 90d / ytd, each { sev1..sev5, total, avgDays }.
   * topServices: ranked list of { service, total }. liveCases: on-demand IDs. */
  cases: {
    updated: null,
    liveUpdated: null,
    customers: [
      { name:"Entity Alpha",   windows:{ "7d":{sev1:0,sev2:0,sev3:1,sev4:1,sev5:0,total:2,avgDays:3.1}, "30d":{sev1:0,sev2:1,sev3:3,sev4:4,sev5:0,total:8,avgDays:6.0}, "90d":{total:21,avgDays:7.4}, ytd:{total:46,avgDays:8.2} }, topServices:[{service:"Compute",total:18},{service:"Storage",total:12},{service:"Networking",total:6}], liveCases:[] },
      { name:"Entity Bravo",   windows:{ "7d":{total:0}, "30d":{sev1:0,sev2:0,sev3:2,sev4:3,sev5:1,total:6,avgDays:5.5}, "90d":{total:14}, ytd:{total:33} }, topServices:[{service:"Analytics",total:15},{service:"Data Transfer",total:9}], liveCases:[] },
      { name:"Entity Charlie", windows:{ "7d":{total:1}, "30d":{sev1:0,sev2:1,sev3:1,sev4:2,sev5:0,total:4}, "90d":{total:9}, ytd:{total:17} }, topServices:[{service:"Platform",total:11}], liveCases:[] },
      { name:"Entity Delta",   windows:{ "7d":{total:0}, "30d":{sev1:0,sev2:0,sev3:0,sev4:1,sev5:0,total:1}, "90d":{total:3}, ytd:{total:7} }, topServices:[{service:"Networking",total:5}], liveCases:[] }
    ]
  },

  /* -- My Tickets: assigned to the owner (rewritten by refresh job) --------- */
  tickets: [

],
ticketsUpdated: "2026-10-09T13:49:33+00:00",

  /* -- Trainings: manual list ---------------------------------------------- */
  trainings: [
    { name:"Security Fundamentals (annual)", due:"2026-11-30", status:"pending", link:"https://example.com/training/sec" },
    { name:"Advanced Networking",            due:"2026-12-15", status:"ongoing", link:"" }
  ],

  /* -- On-call ------------------------------------------------------------- */
  oncallDuty: [
    { entity:"Entity Alpha", person:"you",        shift:"09:00–17:00 UTC" },
    { entity:"Entity Bravo", person:"J. Smith",   shift:"17:00–01:00 UTC" }
  ],
  oncallUpcoming: [
    { day:"Mon", entity:"Entity Alpha",   shift:"09:00–17:00 UTC", person:"you" },
    { day:"Tue", entity:"Entity Charlie", shift:"09:00–17:00 UTC", person:"", gap:true }
  ],

  /* -- Standbys (feeds the Overview "This Week" agenda) -------------------- */
  standbys: [
    { entity:"Entity Alpha", event:"Peak event", date:"2026-10-11", time:"14:00–17:00 UTC", role:"Standby", ticket:"TCK-3001" }
  ],

  /* -- Wins / review highlights -------------------------------------------- */
  goals: [
    { title:"Cut Entity Alpha incident volume 30% QoQ", status:"achieved", notes:"Root-caused a recurring config drift; built a guardrail." },
    { title:"Led onboarding for 2 new entities",         status:"ongoing",  notes:"" }
  ],

  /* -- Projects ------------------------------------------------------------ */
  projects: [
    { name:"Monitoring Rollout", status:"active",    description:"Standardised dashboards + alerts across all entities.", link:"https://example.com/project/mon" },
    { name:"Runbook Library",    status:"completed", description:"Authored 12 runbooks for the top failure modes.",     link:"" }
  ],

  /* -- Reviews (table) ----------------------------------------------------- */
  reviews: [
    { entity:"Entity Alpha", topic:"Workload review", ticket:"TCK-4001", status:"done",    date:"2026-09-20", owner:"you", notes:"7 findings, all tracked." },
    { entity:"Entity Bravo", topic:"Design review",   ticket:"TCK-4002", status:"pending", date:"2026-10-20", owner:"you", notes:"" }
  ],

  /* -- Certs / skills ------------------------------------------------------ */
  skills: [
    { name:"Cloud Architect — Professional", issuer:"Example Cert Body", level:"Professional", date:"2025-06", badge:"https://example.com/verify/abc", img:"" },
    { name:"Security Specialty",             issuer:"Example Cert Body", level:"Specialty",     date:"2025-09", badge:"",                               img:"" }
  ],

  /* -- Intel: per-entity rollup (rewritten daily by refresh job) ----------- *
   * Each row: health GREEN|AMBER|RED, chi (score), summary (one-liner),
   * cadence {last,next,prep}, and per-source arrays of {text,id,link,meta}.
   * `sources` holds a short freshness label per source. */
  intelUpdated: "2026-10-09T13:49:33+00:00",
  intel: [

],

  /* -- Manual extra risks (merged with Intel risks on the Risks tab) ------- */
  risks: [
    { entity:"Portfolio", text:"Sev3 shared dependency affects Alpha + Charlie" }
  ],

  /* -- Quick links --------------------------------------------------------- */
  links: [
    { label:"Ticketing system", url:"https://example.com/tickets", icon:"🎫" },
    { label:"Monitoring",       url:"https://example.com/metrics", icon:"📈" },
    { label:"Team wiki",        url:"https://example.com/wiki",    icon:"📚" }
  ]
};
