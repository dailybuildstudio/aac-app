# WARN Monitor App — Build Plan

**Status:** paused before any code written. Project dir is empty.
**Last touched:** 2026-05-18

## Goal

Track WARN Act layoff notices across states (Florida-first) and turn them into a searchable dashboard with alerts.

## Open decision before resuming

Do you actually need a custom app, or just one-off lookups for a specific company?

- **One-off lookup** → no app needed. Public WARN listings (state DOL sites, federal DOL, aggregators) are searchable today. Just give Claude the company name + state.
- **Ongoing monitoring** → execute this plan.

## Open questions

1. Is there a real "WARN Firehose API"? If you don't have a URL, assume no and skip.
2. WARNTracker — usage rights? Otherwise drop.
3. Package manager: pnpm or npm?
4. GitHub remote on day one, or local-only `git init`?
5. AI provider default: Anthropic or OpenAI?

## Architecture

| Layer | Choice | Why |
|---|---|---|
| Web | Next.js (App Router) + TypeScript | RSC reads, route handlers for cron |
| UI | Tailwind + shadcn/ui | Executive look, fast |
| DB | Supabase Postgres | Hosted, RLS, easy auth later |
| Jobs | GitHub Actions cron (primary), Supabase Edge Functions (secondary) | Actions get full Node ecosystem for PDFs/Excel; Edge Functions are Deno-sandboxed |
| AI | Provider-agnostic adapter (Anthropic + OpenAI) | Env-flag toggled, `none` short-circuits |
| Email | Resend | Simple, Vercel-friendly |
| Hosting | Vercel + Supabase | Free tiers cover MVP |

## Folder structure

```
warn-app/
├─ src/
│  ├─ app/
│  │  ├─ (dashboard)/page.tsx
│  │  ├─ (dashboard)/notices/[id]/page.tsx
│  │  ├─ admin/page.tsx                 # Phase 7
│  │  ├─ api/
│  │  │  ├─ cron/ingest/route.ts        # POST, bearer-protected
│  │  │  ├─ cron/alerts/route.ts
│  │  │  └─ notices/route.ts            # filterable JSON read
│  │  └─ layout.tsx
│  ├─ components/                       # shadcn + custom
│  ├─ lib/
│  │  ├─ supabase/{server,client}.ts
│  │  ├─ filters.ts                     # URL <-> filter state
│  │  └─ llm/{index.ts,anthropic.ts,openai.ts}
│  ├─ server/
│  │  ├─ ingest/
│  │  │  ├─ sources/{types,dol,florida,ny,mock}.ts
│  │  │  ├─ normalize.ts
│  │  │  ├─ dedupe.ts
│  │  │  └─ run.ts                      # orchestrator
│  │  └─ alerts/match.ts
│  └─ types/warn.ts
├─ data/mock-warn.json                  # Phase 1
├─ supabase/migrations/
├─ scripts/ingest.ts                    # CLI entry for cron
├─ .github/workflows/ingest.yml
├─ .env.example
```

## Database schema

```sql
create table warn_notices (
  id              uuid primary key default gen_random_uuid(),
  dedupe_key      text unique not null,        -- sha256 of canonical fields
  source_name     text not null,
  source_url      text not null,
  company_name    text not null,
  state           text not null check (length(state) = 2),
  city            text,
  address         text,
  notice_date     date,
  layoff_start_date date,
  number_of_workers int,
  industry        text,
  reason          text,
  notice_type     text,
  raw_payload     jsonb not null,
  ai_summary      text,
  ai_summary_model text,
  ai_summary_at   timestamptz,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);

create index on warn_notices (state, notice_date desc);
create index on warn_notices (company_name);
create index on warn_notices using gin (
  to_tsvector('english', company_name || ' ' || coalesce(industry,'') || ' ' || coalesce(reason,''))
);

create table ingestion_runs (
  id          uuid primary key default gen_random_uuid(),
  source_name text not null,
  started_at  timestamptz not null default now(),
  finished_at timestamptz,
  status      text not null,
  rows_seen   int default 0,
  rows_new    int default 0,
  error       text
);

create table saved_searches (
  id           uuid primary key default gen_random_uuid(),
  email        text not null,
  filters      jsonb not null,
  last_alerted_at timestamptz,
  created_at   timestamptz default now()
);
```

`dedupe_key = sha256(lower(company) | state | city | notice_date | layoff_start_date | workers)`
Upsert with `on conflict (dedupe_key) do update set raw_payload=..., updated_at=now()` — idempotent.

## Ingestion strategy

WarnSource interface:

```ts
interface WarnSource {
  name: string;
  fetch(): Promise<RawNotice[]>;
  normalize(raw: RawNotice): WarnNotice;
}
```

Orchestrator iterates sources: fetch → normalize → dedupe → upsert. Per-source errors logged in `ingestion_runs`, don't break the run.

Source priority:

- **DOL** — CSV/Excel, national baseline. Use `xlsx`.
- **NY Open Data** — SODA JSON API, easiest for testing dedup.
- **Florida** — floridajobs.org HTML + PDF. Hardest, do last in Phase 3. `cheerio` + `pdf-parse`.
- **TX, CA, WA** — HTML scraping via `cheerio` as time permits.
- **WARNTracker** — skip unless ToS confirmed.
- **WARN Firehose API** — unknown; treat as not-real until URL provided.

## Dashboard UX

Single page:

```
┌────────────────────────────────────────────────────────┐
│  WARN Monitor                          [Florida ▾] [⚙] │
├────────────────────────────────────────────────────────┤
│  KPI strip: 30-day workers | notices | top industry    │
├────────────────────────────────────────────────────────┤
│  Filters (sticky): search · state · date · industry ·  │
│                    workers≥ · notice_type              │
├────────────────────────────────────────────────────────┤
│  Table: Company | State | City | Notice date | Workers │
│  Row click → /notices/[id] detail page                 │
└────────────────────────────────────────────────────────┘
```

Filters live in URL (shareable, back/forward works). Detail page = full record + AI summary + raw source link. No charts for MVP.

## Alerts

- User saves filter → `saved_searches` row.
- Cron every 30 min queries each saved search for new rows since `last_alerted_at`, sends digest via Resend.
- Update `last_alerted_at` only after successful send.
- Email-only for MVP. No SMS/Slack.

## API strategy

- Reads: Server Components → Supabase direct. Public `GET /api/notices` for programmatic use.
- Writes: ingestion server-only. `POST /api/cron/ingest` protected by `CRON_SECRET` bearer.
- No auth Phase 1–5. Supabase Auth optional in Phase 6 if needed for "my saved searches" UI.

## Deployment

- Vercel for Next.js, auto-deploy on `main`.
- Supabase for DB + storage.
- Scheduled ingestion: GitHub Actions cron (every 6 hours) running `pnpm tsx scripts/ingest.ts`.
- Alerts: same pattern, faster cadence.
- Secrets: `.env.local` dev; Vercel env + Actions secrets prod. Never committed.

## Phases

| Phase | Deliverable | Scope |
|---|---|---|
| **1. Mock + dashboard** | `create-next-app`, shadcn init, `data/mock-warn.json`, table + filters wired to in-memory data | 1 sitting |
| **2. Supabase** | Migrations, client setup, swap mock for live reads, env wiring | 0.5 sitting |
| **3. Real ingestion** | WarnSource interface, DOL + NY adapters, then FL, dedup, idempotency, `scripts/ingest.ts`, GH Actions workflow | Biggest — FL alone could be a day |
| **4. Search/filter polish** | Full-text search, URL state, server-side pagination, sortable columns | 0.5 sitting |
| **5. AI summaries** | `lib/llm/` adapter, summary backfill script, detail page integration | 0.5 sitting |
| **6. Alerts** | `saved_searches` table, save-search UI, Resend integration, cron | 1 sitting |
| **7. Admin/debug** | `/admin`: ingestion_runs viewer, manual re-run, merge-duplicates, raw_payload inspector | 1 sitting |

## Hard requirements (do not skip)

- No hardcoded secrets — env vars only.
- Error handling + logging on every scraper.
- Idempotent ingestion (dedupe_key + upsert).
- Dedup uses: company, location, notice date, layoff date, worker count.
- Clean executive-friendly UI.
- Working MVP over engineering elegance.

## To resume

1. Answer the open questions above.
2. Decide: app vs. one-off lookup.
3. If building, say "start Phase 1" and I'll scaffold.
