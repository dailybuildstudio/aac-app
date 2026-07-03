# 🌀 Find Shelter Now (Florida) + Eiren — v1

A two-product system: a free public-facing site (**Find Shelter Now**) and a shelter-operations dashboard (**Eiren**), sharing one backend.

---

## Product overview

**One company, two products, one shared backend.**

```
                     ┌─────────────────────────┐
                     │   ONE BACKEND (shared)  │
                     │  - shelter database     │
                     │  - REST/JSON API        │
                     │  - auth (operators only)│
                     │  - scraper fallback     │
                     └────────┬────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
   ┌──────────▼──────────┐         ┌──────────▼──────────┐
   │  Find Shelter Now   │         │       Eiren         │
   │   PUBLIC, READ      │         │  OPERATOR, WRITE    │
   │   no auth · SEO     │         │  login · dashboard  │
   │   PWA · offline     │         │  multi-org · ops    │
   │   seekers, families │         │  shelter staff      │
   └─────────────────────┘         └─────────────────────┘
```

**Find Shelter Now** is the front door for Florida residents in a housing crisis or facing evacuation. Free, anonymous, mobile-first, English + Spanish, offline-capable.

**Eiren** is the operator product — a SaaS-style dashboard for shelter staff to update bed availability, status, and program info in seconds. Eiren *feeds* the data that Find Shelter Now displays.

---

## Why this product, why now

- Florida is currently mid-disaster: "worst Florida fire season in 30–40 years" (April 2026); severe drought across the Southeast.
- Existing data infrastructure is *open and free* — FEMA NSS ArcGIS REST API, FloridaDisaster.org shelter portal, Red Cross map — but the **front door is consistently bad.** FEMA's own mobile app is rated **1.3 stars** with documented bugs.
- Documented gaps that cost lives:
  - **Spanish-language access** (multiple academic + journalistic sources confirm this is *deadly*)
  - **Pet-friendly filtering** (44% of Katrina evacuation refusals cited pets)
  - **Trust/anonymity** for undocumented populations who fear government channels
- Florida-specific advantages:
  - Best-in-class disaster shelter data (state portal publishes real-time during activations)
  - 27 Continuums of Care to potentially partner with for the homelessness side
  - 21% Hispanic state population (Spanish-first pays off most here)

**Intended outcome of v1:** a Florida resident in housing crisis or facing evacuation can open the site on any phone (online or offline), in English or Spanish, find a shelter that matches their needs (pet-friendly, special-needs, last-resort), see whether it's open or full (during hurricane activations), and get there — without surrendering any personal information.

**Scope decision (locked):** Florida-only, dual-mode (Hurricane + Year-Round homeless directory), one brand on the public side, separate brand on the operator side.

---

## Competitive landscape

The space has direct + adjacent players. Find Shelter Now's wedge is the **hurricane-shelter + Spanish-first + dual-mode + free-and-anonymous + Florida-specific** combination — none of the existing players hit all five.

| Product | Pattern | Public side | Operator side | Gap we fill |
|---|---|---|---|---|
| **HC Shelter Tracking** | Closest match | Authorized seekers only | Real-time bed counts | Not free / not public / not Florida-focused |
| **ShelterBridge** | Mobile + provider portal | Beds, waitlist, meals | Provider updates | No hurricane mode, no Spanish-first |
| **Shelter App** | Web + iOS + Android | Map/list view | Provider bed updates | No hurricane mode, US-wide / shallow per state |
| **OurCalling** | Big directory | Search by city/category | Curated only | No real-time, no hurricane |
| **FindHelp / Aunt Bertha** | The giant — 552k programs | Seeker portal | Provider "claim & update" | Generic; not disaster-tuned; not anonymous |
| **Bitfocus Clarity (HMIS)** | Backend system of record | API only | Full case management | Operator-only; no public consumer face |
| **Red Cross Open Shelter Map** | Disaster-only, big org | Public map | Internal Red Cross ops | Disaster-only, not year-round, US-wide / shallow per state |
| **FEMA NSS / FEMA app** | Federal data | Public app (1.3 ★) | National provider data | Bad UX; no Spanish-first; no homeless side |

**Differentiators:** Spanish-first (not bolted on), pet/special-needs/last-resort filters built in from day one, true offline-first PWA designed for hurricane connectivity reality, zero-PII architecture for trust with undocumented populations, dual-mode (hurricane + year-round homeless) under one brand.

---

## Find Shelter Now (public product)

**Working name:** Find Shelter Now (Florida) — `findsheltern[ow]`. Open question for launch: name may be too broad given dual-mode scope.

**One sentence:** A Spanish-first, anonymous, mobile-first PWA for Florida that shows real-time hurricane shelter status during state-declared emergencies and a year-round directory of homeless shelters, with honest limits about what we know and don't know.

**Two modes from one homepage:**

1. **🌀 Hurricane Mode** (auto-active when FL declares emergency)
   - Live data from `apps.floridadisaster.org/shelters` (5-min cached proxy)
   - In v1.5+: also live from Eiren operator updates
   - Shelter status badges: **Open / Full / Closed / Limited / Weather-Only / By Referral**
   - Filters: pet-friendly, special-needs, shelter-of-last-resort
   - "What to bring" + driving directions per shelter
   - Spanish + English; Haitian Creole as a fast-follow

2. **🏠 Year-Round Mode** (FL homeless shelter directory, always on)
   - Static directory of FL shelters (curated from CoC websites + 211)
   - In v1.5+: live bed counts where Eiren operators are publishing
   - Hours, services, eligibility, contact info
   - **No real-time bed availability in v1.** HUD/HMIS data is private. We do not pretend to know.
   - Always says: *"To check if a bed is available tonight, call **211** or the shelter directly."*

### Hard guardrails (non-negotiable)

- **Zero PII collection on the public side, ever.** No accounts, no signup, no email capture, no contact forms.
- **No fingerprinting analytics.** Plausible at most; ideally none in v1.
- **Quick-exit button** on every page (one tap → neutral site + clears history if technically possible).
- **"Always call 211 to confirm" disclaimer** on every shelter result.
- **Data attribution:** "Source: FEMA NSS + American Red Cross + FloridaDisaster.org + verified operators via Eiren" footer.
- **Hotline routing on homepage** for needs we don't serve:
  - Domestic violence: **1-800-799-7233** (The Hotline)
  - Mental health crisis: **988**
  - General service connection: **211**
- **"Last updated" timestamp** visible on every shelter card.
- **Conservative status interpretation:** when in doubt, default to "call to confirm" rather than "open."

---

## Eiren (operator product)

**Tagline:** *Shelter Operations — update status in 10 seconds.*

A dashboard for shelter staff and CoC coordinators to update bed availability, status, and program details. Replaces phone-tag and out-of-date spreadsheets.

**Core screens (already prototyped in base):**

| Screen | Purpose |
|---|---|
| **Dashboard** | Available beds, stale-data alerts, "needs attention" vs "recently updated" cards |
| **Quick Update** | Pick program → tap status (Open / Limited / Full / Closed / Weather-Only / By Referral) → bed counter → confirm. ≤10 seconds. |
| **Dispatch (LIVE)** | Searchable program list with filters (men/women/families/youth/veterans/LGBTQ+/couples), beds-used/total, last updated, cutoff times |
| **Analytics** | Freshness SLA, updates/day, status distribution, top closure reasons, CSV export |
| **Organizations** | Multi-tenant: each provider org manages its own programs |
| **Settings** | Program CRUD with bed/family-spot counts |

**Eiren = the v1.5 facility onboarding from the original plan**, designed earlier as its own product. Shipping Eiren means we don't need to scrape — operators publish authoritative data themselves.

**Eiren guardrails:**
- Multi-tenant: each provider sees only their org's programs
- Verified onboarding only (manual approval for first 100 orgs)
- Audit log on every status change (immutable, timestamped)
- A claimed listing's address can never be edited via self-service — only hours / capacity / services. Address changes go through manual review.
- Facilities cannot delete themselves; they can mark inactive.
- Every Eiren-published listing displays a "Verified by Eiren on [date]" badge on Find Shelter Now.

---

## Branding + domains

| Property | Choice | Why |
|---|---|---|
| Public brand | **Find Shelter Now** | Direct, search-friendly, English + intuitive Spanish translation (*Encuentre Refugio Ahora*) |
| Operator brand | **Eiren** | Greek *Eirēnē* = "peace." Distinctive, ownable, sounds like real software. |
| Public domain | `findsheltern[ow]` (.org preferred) | Already purchased |
| Operator domain | `eiren.app` (or subdomain `ops.findsheltern[ow]`) | Decide before Eiren launch — separate brand recommended |
| Parent company | Single legal entity owns both | Match Aunt Bertha → findhelp / Bitfocus → Clarity model |

---

## Tech stack

| Concern | Choice | Why |
|---|---|---|
| Framework | **Next.js 15 (App Router)** + TypeScript (both products) | SSR is non-negotiable for SEO ("hurricane shelters near me [zip]"). Same stack on both sides. |
| Styling | **Tailwind CSS** | Large tap targets, AAA contrast, calm palette enforced cheaply. |
| i18n | **`next-intl`** | English + Spanish in v1; structure ready for Haitian Creole + Vietnamese later. |
| Backend | **Cloudflare Workers + D1 (SQLite) + KV** | One Worker serves both products. D1 is the shelter database (Eiren writes, Find Shelter Now reads). KV caches scraper output. |
| Auth (Eiren only) | **Clerk** or **Cloudflare Access** | Operator login. Public side stays auth-free. |
| Hurricane data | **Cloudflare Worker** scraping `apps.floridadisaster.org/shelters` (5-min KV cache). Falls back to FEMA NSS ArcGIS REST. Falls back further to Eiren-operator data. | Defense in depth; safe degradation. |
| Year-round data | Static JSON in v1; D1-backed in v1.5 (Eiren operators) | Honest progression. |
| PWA | **`next-pwa`** (Workbox) — both products | Offline cache of last-known shelter list. Background sync for Eiren updates. |
| Hosting | **Cloudflare Pages** + Workers | Free tier handles serious traffic; better privacy than Vercel for this audience. |
| Maps | **Leaflet + OpenStreetMap** + **MapLibre** offline tiles | No Google Maps cost, better privacy story, sufficient for shelter pins. Offline-capable. |
| Tests | Vitest + Playwright + axe-core | Standard. |

**Explicitly rejected:**
- Firebase / Supabase backend (Cloudflare D1 + Workers is cheaper, integrated, better privacy)
- Google Maps (privacy concern + cost)
- Vercel Analytics (fingerprinting; conflicts with trust principle)
- Native iOS/Android (PWA is enough for v1)

---

## Disaster-mode + offline (the hurricane wedge)

Cell networks routinely saturate *before* landfall and stay down for hours-to-days after. This is where Find Shelter Now wins against everyone else: it's **designed for the moment the network is gone.**

### Public side (Find Shelter Now)

| Feature | What it does during a hurricane |
|---|---|
| **Service Worker + Cache API** | App shell + last-known shelter list pre-cached. App opens with no signal. |
| **IndexedDB** | Full FL shelter directory (~thousands of entries) cached on device. |
| **Background Sync** | Auto-refresh shelter status when signal returns. |
| **PWA install ("Add to Home Screen")** | One-tap launch. iOS Safari + Android Chrome supported. |
| **Stale-while-revalidate + "Last updated 2h ago" banner** | Honest UX — user knows the data may be stale. |
| **Pre-storm priming banner** | During hurricane watch: *"Save shelters for offline use →"* one-tap caches full FL directory + map tiles for the user's county. |
| **Offline maps** | OpenStreetMap tiles cached for the user's region. |
| **`tel:` links work offline** | Phone numbers function with no data — just signal. |
| **SMS fallback instructions** | "Text SHELTER to 211" cached on every page. |
| **Battery-saver mode** | Dark/dim theme toggle, no animations. |
| **Print-ready shelter card** | Physical paper backup before the storm. |
| **Last-sync timestamp prominent** | *"Updated 4h ago, offline now."* |

### Operator side (Eiren)

Shelter staff often have *worse* connectivity than seekers (industrial buildings, basements). Same offline-first treatment:

- Status updates queued locally if connection drops
- Background-sync pushes updates when connection returns
- "Update saved offline — will sync when online" toast confirmation
- Critical-info read access works offline (current programs, contact info)

### Backend degraded mode

When the FL state portal scraper fails mid-storm (it will), the public site automatically falls back to operator-provided data from Eiren. So even if FloridaDisaster.org is down, Find Shelter Now stays useful — as long as operators are still updating.

---
## Folder structure (monorepo)

```
shelter-now/
├── apps/
│   ├── web/                            # Find Shelter Now (public)
│   │   ├── public/
│   │   │   ├── icons/
│   │   │   └── locales/
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── page.tsx            # homepage with two mode buttons + hotline router
│   │   │   │   ├── hurricane/
│   │   │   │   ├── housing/
│   │   │   │   ├── about/
│   │   │   │   ├── safety/
│   │   │   │   └── api/shelters/route.ts
│   │   │   ├── components/
│   │   │   ├── data/messages/{en,es}.json
│   │   │   └── lib/
│   │   ├── next.config.ts
│   │   └── package.json
│   └── eiren/                          # Operator product
│       ├── src/
│       │   ├── app/
│       │   │   ├── dashboard/
│       │   │   ├── quick-update/
│       │   │   ├── dispatch/
│       │   │   ├── analytics/
│       │   │   ├── organizations/
│       │   │   └── settings/
│       │   ├── components/
│       │   └── lib/
│       └── package.json
├── packages/
│   ├── shared/                         # types, utils used by both apps
│   ├── api-client/                     # typed client for the backend
│   └── ui/                             # shared component library
├── workers/
│   ├── api/                            # main API Worker (D1 + KV)
│   ├── shelter-proxy.ts                # FL portal scraper + cache
│   └── wrangler.toml
├── migrations/                         # D1 schema
└── README.md
```

---

## Phased roadmap

### v1.0 — Public site, scraped data (ship before next hurricane season)
1. **Phase 0 — Scaffolding:** Next.js + Tailwind + Cloudflare Pages, ESLint, CI
2. **Phase 1 — Static skeleton + homepage:** two mode buttons, hotline router, About/Safety, quick-exit, EN/ES switcher
3. **Phase 2 — Hurricane mode:** Cloudflare Worker proxy + 5-min KV cache, activation detector, county selector, ShelterCard with status badges, pet/special-needs/last-resort filters
4. **Phase 3 — Year-round mode:** static JSON of FL homeless shelters by county, "call 211" disclaimer, no fake bed counts
5. **Phase 4 — Spanish localization:** all UI strings, formal *usted* tone, ZIP labels, status badges, all CTAs
6. **Phase 5 — PWA + offline:** `next-pwa` config, precache app shell, last-known shelter list cached
7. **Phase 6 — Accessibility + safety pass:** axe-core zero violations, keyboard-only walkthrough, VoiceOver/TalkBack
8. **Phase 7 — SEO + launch prep:** server-rendered shelter pages, schema.org `EmergencyService`, sitemap, robots.txt, OG images
9. **Phase 8 — Soft launch + observe:** production deploy, Search Console, careful Reddit posts, outreach to 3 FL CoCs

### v1.5 — Eiren operator product
1. D1 schema for shelters / programs / orgs / users / status history (immutable audit log)
2. Auth (Clerk or Cloudflare Access) for operator login only
3. Eiren UI (already prototyped in base): dashboard, quick-update, dispatch, analytics, organizations, settings
4. Manual onboarding flow for first 100 orgs (Amanda or trusted partner approves)
5. "Claim this listing" flow on **existing** Find Shelter Now entries
6. Live integration: Eiren writes → Find Shelter Now reads (5-min cache)
7. Background-sync for offline-queued operator updates
8. "Verified by Eiren" badges on Find Shelter Now where applicable

### v2 — Self-service + scale
1. Auto-verification against HUD CoC database (homeless) and FL DEM shelter registry (hurricane)
2. Net-new entries that don't match either source still require manual approval
3. Push notifications (opt-in only, no PII)
4. Haitian Creole + Vietnamese localization
5. State expansion (Georgia, Texas, Louisiana — same hurricane belt)

---

## Revenue model — three options to choose between

| Model | Public side | Operator side | Pros | Cons |
|---|---|---|---|---|
| **A. Grant-funded nonprofit** | Free | Free | Mission-aligned; trust; eligible for FEMA/HUD/foundation grants | Fundraising overhead; precarious |
| **B. Freemium SaaS for Eiren** | Free | Free for ≤3 programs; paid tier for orgs with analytics, multi-org, API access | Predictable revenue; doesn't compromise public mission | Requires sales motion; small-shelter ARPU low |
| **C. B2G (sell to government)** | Free | Sell unified system to county/state Emergency Management agencies | Higher contract values; aligns with their mandate | Slow procurement cycles; political |

**Recommended starting point:** **A → B hybrid.** Launch as nonprofit-style for the public side (grants pay infra). Eiren as freemium when v1.5 ships — small shelters always free, paid tier kicks in only at multi-org scale (CoCs, faith-based networks, county systems).

---

## Partnership outreach (post-launch only)

Order by leverage-to-effort:

1. **Florida Coalition to End Homelessness (FCH)** — `fchonline.org` — represents 27 FL CoCs. One email puts you in front of all of them. Frame: *"I built a free public directory; would you review for accuracy?"*
2. **Tampa Hillsborough Homeless Initiative (THHI)** — large, vocal CoC; could endorse early.
3. **Hispanic Access Foundation** — already publishes a wildfire toolkit; Spanish-first audience overlap. Frame: *"I'd love feedback on our Spanish translation."*
4. **National VOAD** — 110-member coalition; harder reach but possible.
5. **County Emergency Management offices** — start with Miami-Dade, Hillsborough, Orange.

Don't pursue any until v1 is live and stable. A working product is the best opener.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Wrong shelter data costs trust | Disclaimer + 211 fallback on every result. "Last updated" timestamp. Conservative status interpretation. |
| FL portal HTML changes break the scraper | Worker has try/catch + "data temporarily unavailable, call 211" fallback. Daily health-check ping. Eiren operator data as further fallback (v1.5+). |
| Spanish translation tone is off | One bilingual reviewer pass before launch. Hispanic Access partnership is the cleanest source. |
| Inbound asks for DV / mental health / refugee | Hotline router on every page handles politely; firm "we focus on FL hurricanes + housing" stance. |
| Bot traffic mistaken for product-market fit | Track *user actions* (filter clicks, language switch, time-on-shelter) — bots don't do those. Plausible only post-launch. |
| Crowded space (Shelter App, ShelterBridge, FindHelp) | Win on the wedge: Spanish-first + hurricane-tuned + offline-first + Florida depth. Don't try to be national or generic. |
| Liability for publishing shelter info | Aggregating PUBLIC data with attribution; disclaimer + "verify via 211" is the standard of care. Add ToS disclaiming warranty before launch. |
| Eiren onboarding gets gamed (fake facility) | Multi-step verification: facility ID → org domain email → callback to listed phone → manual approval for first 100. Auto-verify against HUD CoC + FL DEM registries thereafter. |
| Address-poisoning attack via Eiren | Address field is read-only via self-service. Address changes go through manual review. |
| Domain "Find Shelter Now" too broad for dual-mode brand | Decide before launch: keep the name with explicit scope statement, or rebrand. Default: keep + explicit scope. |

---

## Verification (before declaring v1 launch-ready)

1. `npm run build && npm run start` → production build loads cleanly
2. **Homepage smoke:** two mode buttons visible, language switcher works, hotline footer visible
3. **Hurricane mode (no activation):** "no current activation" message + "set up alerts" CTA renders
4. **Hurricane mode (simulated activation):** mock FL portal response → shelters render with correct status badges, filters work
5. **Year-round mode:** county selector → list of shelters with hours, services, "call 211" disclaimer on every entry
6. **Spanish mode:** every screen translates, no English leaks, *usted* tone consistent
7. **Quick-exit:** any page → neutral site + clears back-button trail where supported
8. **Offline test:** Chrome DevTools → Offline → reload → last-known shelter list still renders + clear "offline" indicator
9. **Pre-storm priming:** "Save for offline" CTA caches county directory + map tiles
10. **Accessibility:** axe-core reports zero serious/critical; VoiceOver reads all CTAs and shelter cards correctly
11. **Lighthouse mobile (production):** Performance ≥ 90, Accessibility = 100, PWA = installable
12. **Cloudflare Worker proxy:** rate-limited (max 1 request per 5 min per ZIP); error states render gracefully
13. **Real-device smoke:** install on iPhone Safari and Android Chrome; airplane mode; navigate every page

When all 13 pass, v1 is ready to launch.

### Eiren v1.5 verification (separate)

1. Operator login + multi-tenant org isolation (no cross-org data leakage)
2. Quick-update: status change persists to D1, reflects on Find Shelter Now within cache TTL
3. Audit log: every status change immutable, timestamped, attributed
4. Background sync: offline-queued updates push when connection returns
5. Onboarding flow: facility-ID → email → phone callback → manual approval gate
6. CSV export of program data
7. Analytics: freshness SLA, updates-per-day, status distribution

---

## Out of scope for v1 (state explicitly on About page)

- Domestic violence shelters → route to **1-800-799-7233**
- Refugee/asylum services → different audience
- Real-time bed availability for homeless shelters in v1 → HMIS data is private; route to **211**. (Returns in v1.5 via Eiren operators.)
- **Public-side facility self-onboarding** — Eiren handles this in v1.5+
- Reservations or signup (for end users)
- User accounts (for end users)
- States other than Florida (v2)
- Push notifications (v2; opt-in only when added)
- Native iOS/Android app (PWA only)
- Bed-count promises of any kind (always "verify via 211")

---

## Critical files to create

```
shelter-now/
├── apps/web/                                   ← Find Shelter Now
│   ├── package.json
│   ├── next.config.ts
│   └── src/
│       ├── app/page.tsx                        ← homepage with two mode buttons
│       ├── app/hurricane/page.tsx              ← hurricane mode entry
│       ├── app/hurricane/[county]/page.tsx     ← county shelter list
│       ├── app/housing/page.tsx                ← homelessness directory entry
│       ├── app/housing/[county]/page.tsx       ← county homeless directory
│       ├── app/about/page.tsx                  ← scope + data attribution
│       ├── app/safety/page.tsx                 ← quick-exit explainer
│       ├── app/api/shelters/route.ts           ← Worker proxy entry
│       ├── components/HomeMode.tsx
│       ├── components/ShelterCard.tsx
│       ├── components/HotlineRouter.tsx        ← 211 / DV / 988
│       ├── components/QuickExit.tsx
│       ├── data/florida-counties.ts
│       ├── data/messages/{en,es}.json
│       ├── lib/florida-disaster.ts             ← FL portal adapter
│       └── lib/fema-nss.ts                     ← FEMA NSS REST adapter (fallback)
├── apps/eiren/                                 ← Operator product (v1.5)
│   └── src/app/{dashboard,quick-update,dispatch,analytics,organizations,settings}/
├── packages/shared/                            ← Types + utils for both
├── packages/api-client/                        ← Typed client for backend
├── workers/api/                                ← Main API (D1 + KV)
├── workers/shelter-proxy.ts                    ← FL portal scraper
├── migrations/                                 ← D1 schema
└── README.md
```

No existing functions or utilities to reuse — this is a greenfield repo.
