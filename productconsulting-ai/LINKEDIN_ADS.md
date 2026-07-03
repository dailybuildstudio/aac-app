# LinkedIn Ad Copy Pack — productconsulting.ai

*Three ad variants, each with a different angle. Run them as a small A/B/C test — let CPL (cost per booking) pick the winner. Don't trust CTR alone; CTR can be high on bad-fit clicks.*

**Targeting note:** LinkedIn Single Image Ads tend to outperform Carousels for senior B2B. Sponsored Content (in-feed) > Message ads for first-touch cold.

**Audience to test first:**
- **Job titles:** Founder, CEO, Co-Founder, Head of Product, VP Product, CPO, Chief Product Officer
- **Company size:** 11–500 employees (skip enterprise, too long a sales cycle for the audit price point)
- **Industry:** Software, Internet, Financial Services, Retail (your domain depth)
- **Geo:** United States to start; expand to UK/Canada after first 30 days if learnings hold
- **Exclude:** Marketing/sales/HR titles; consulting firms (peers, not customers)
- **Budget to test:** $25–50/day across the three ads for 7 days, then narrow to the winner

---

## Ad A — Pain-led (the MIT stat)

**Hook:**
> 95% of enterprise GenAI pilots deliver zero measurable P&L impact (MIT, 2025).

**Body:**
> The fix isn't a better model. It's the product judgment around it: picking the right bet, scoping it so it ships, making sure people actually use it.
>
> I help seed–Series A teams turn AI ambition into features that ship and get used. Fixed-scope AI Product Audit from $3,000 — two weeks, ranked roadmap, concrete first-build recommendation.

**CTA button:** **Book a free 30-min teardown**
**Destination URL:** `https://cal.com/amanda-shelton/teardown`

**Visual direction:** A clean dark hero with the "95%" stat in bold gradient text (you can repurpose your hero design). Single image, no text overlay on the image (LinkedIn dings creatives with >20% text).

---

## Ad B — Framework download (lead magnet)

**Hook:**
> The 5-dimension scoring model I use in paid AI Product Audits — free.

**Body:**
> Built for product leaders deciding which AI features to build next:
>
> ▸ The opinionated scoring rubric for ranking opportunities
> ▸ Stage-by-stage weighting (seed, scale-up, enterprise)
> ▸ The "what NOT to build" checklist that's saved teams quarters of wasted work
> ▸ A worked example of a real prioritization
>
> Drop your email. I'll send it.

**CTA button:** **Download**
**Destination URL:** `https://productconsulting.ai#framework` (the lead-magnet section)

**Visual direction:** A mockup of the PDF cover — your name + "The AI Product Audit Scoring Framework" — on a deep gradient background. Looks like a real deliverable, not a generic eBook.

**Why this one matters:** Most senior buyers won't book a call cold. The framework download gives you their email so you can nurture them (`NURTURE_SEQUENCE.md`). Expect a higher click-through and a lower-cost-per-lead than Ad A — but also a longer path to booking.

---

## Ad C — Fractional product positioning

**Hook:**
> Stop running AI strategy. Start shipping AI features.

**Body:**
> Most "AI transformation" engagements end with a deck and a six-figure invoice. Six months later, the team is still shipping the same product.
>
> I work two ways:
>
> ▸ **AI Product Audit** — $3,000 flat, 2 weeks, ranked roadmap.
> ▸ **Fractional Head of AI Product** — 2–3 days/week, embedded, owning the work.
>
> Senior product judgment in the work — not arm's length.

**CTA button:** **Learn more**
**Destination URL:** `https://productconsulting.ai`

**Visual direction:** Your headshot, clean white or off-white background, your headline overlaid in bold. People-led ads typically outperform pure-text designs in B2B advisory categories.

---

## How to run the test

1. **Set up all three ads** in one Campaign in LinkedIn Campaign Manager.
2. **Even budget split** — let LinkedIn's auto-optimize favor whichever ad wins.
3. **Define the conversion event** in LinkedIn (it should be "booking confirmed" — once Cal.com → your site is wired with a conversion event in Phase 3, this lights up).
4. **Run for 7 days minimum** before judging. LinkedIn ads have a slower learning curve than Meta/Google.
5. **Kill the loser at day 7.** Double budget on the winner.

## Naming convention for tracking
- `pcAI-2026q2-pain-95pct` — Ad A
- `pcAI-2026q2-magnet-framework` — Ad B
- `pcAI-2026q2-position-fractional` — Ad C

Use the same naming in any UTM tags so analytics matches campaign source-of-truth.

## Don't forget
- **Privacy policy URL** must be on the destination site (it is — `/privacy.html`).
- **Conversion tracking** has to be wired before ads can optimize properly. Plausible + LinkedIn Insight Tag is the cleanest pair.
- **Don't run ads to `workers.dev`** — only to `productconsulting.ai`. Workers.dev URLs look sketchy in the ad preview.
