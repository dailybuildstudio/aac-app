# AI Product Audit — Worked Example

*A fully populated audit deliverable for a fictional client (**Beacon HR**) so you can see what excellence looks like before your first real engagement. Mirrors the structure in `AUDIT_TEMPLATE.md`. Replace [bracketed] sections with real client content; the rest is reusable structure and voice.*

---

# 0. Cover

**Prepared for:** Beacon HR
**Prepared by:** Amanda Shelton, MBA · productconsulting.ai
**Date:** [DATE]
**Engagement:** AI Product Audit (fixed scope — 2 weeks, $3,000 flat)

---

# 1. Executive Summary

Beacon HR has been weighing six AI feature ideas across its employee feedback platform. Most of them are either commodity bets that competitors will neutralize within a year, or ambitious scope that will burn an engineering quarter without measurable customer impact.

**Build first: AI-Summarized Survey Themes.** A weekly, per-team email that condenses the top 3 themes from open-text survey responses into one paragraph each, with a confidence score and a "drill down" link. Scores **22/25** on the framework — strong on user value, business impact, and time to value, with credible defensibility through Beacon's existing taxonomy of feedback categories.

**Build never (or buy don't build): the AI Chatbot for HR teams.** Scores 14/25 — high feasibility, near-zero defensibility, and well-served by existing vendors. Recommend buying from a partner or skipping.

**The single biggest win is what you choose NOT to ship.** Three of the six candidates have explicit "no" recommendations with reasoning included. Acting on those frees ~1 engineer-quarter for the build-first work.

**Expected impact of the build-first feature:** 18–25% lift in weekly active managers, measurable within 6 weeks of launch. (Reasoning in §5.)

---

# 2. Context & Inputs

- **Product today.** Beacon HR is a quarterly + ad-hoc employee feedback platform. Primary users: HR partners and team managers in mid-market companies (200–2,000 employees). Customers: 47. ARR: ~$3M. Series A closed 5 months ago.
- **Users / segments.** (1) HR partners — design surveys, run reports, drive org-wide insights. (2) Team managers — receive results for their team, expected to act on them. Manager engagement is the bigger growth lever; HR engagement is already strong.
- **Key metrics & current state.**
  - Weekly active managers (WAM): **34%** of seated managers. Target: 60%.
  - Survey open-text response rate: **48%** of employees.
  - Time-to-insight for managers: median **23 minutes** of reading per survey cycle (per session analytics).
- **Stated AI ambitions.** Two themes from kickoff: (a) "Help managers get to the point faster," (b) "Make our feedback platform feel modern alongside competitors that have shipped AI features."
- **Constraints.** 7 engineers, two of whom have shipped LLM features before. Limited fine-tuning capacity. Data is mostly text (survey responses), already labeled with category tags. Compliance: SOC 2 Type II in progress; no model can train on customer data.
- **Inputs reviewed.** Product walkthrough (kickoff call, 60 min). 3 stakeholder interviews (Head of Product, Lead Engineer, Customer Success Lead). 6 months of analytics (Mixpanel export). Internal "AI ideas" Notion doc shared by Head of Product. Public-facing landing pages of 4 competitors.

---

# 3. The Opportunity Scoring Model

Each opportunity scored 1–5 on five dimensions, summed to a 5–25 priority score.

| Dimension | What it measures |
|-----------|------------------|
| **User Value** | How much it improves the user's core job |
| **Business Impact** | How directly it moves a measurable metric |
| **Feasibility** | How realistic given team, data, and tools (5 = easy) |
| **Time to Value** | How fast it ships meaningful results (5 = weeks) |
| **Defensibility** | Whether it compounds advantage vs. commodity bolt-on |

---

# 4. Opportunity Inventory

| # | Opportunity | Value | Impact | Feasibility | TTV | Defensibility | **Priority** |
|---|-------------|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | **AI-summarized survey themes** (per team, weekly) | 5 | 5 | 4 | 4 | 4 | **22** |
| 2 | **Open-text auto-categorization** for HR partners | 4 | 4 | 5 | 5 | 3 | **21** |
| 3 | **Suggested coaching prompts** for managers | 4 | 4 | 3 | 3 | 4 | **18** |
| 4 | **AI sentiment scoring** displayed at-a-glance | 3 | 3 | 5 | 5 | 2 | **18** |
| 5 | **AI chatbot for HR partners** | 3 | 3 | 4 | 4 | 1 | **15** |
| 6 | **AI-generated survey question suggestions** | 2 | 2 | 5 | 5 | 2 | **16** |

Short notes on each:

**1. AI-summarized survey themes (build first).** Hits the explicit user pain — managers spend 23 minutes reading raw responses. Compresses that to 90 seconds. Beacon's existing feedback-category taxonomy makes this defensible (most competitors don't have one, so their summaries are vague). Risk: bad summaries on small teams (low N) — mitigate with a confidence score and a "data too thin" guardrail.

**2. Open-text auto-categorization for HR partners.** Already half-built internally with rule-based logic. Moving to an LLM-based classifier improves accuracy. Easy win, ships in 3 weeks. Lower priority than #1 because HR partners are not the engagement gap.

**3. Suggested coaching prompts for managers.** Powerful when it's right; risky when it's wrong (advice to a manager is high-stakes). Defensibility is good — feedback to coaching connection becomes Beacon's signature. But the cost of being wrong is high; needs careful UX (suggested, not prescribed) and a confidence floor.

**4. AI sentiment scoring.** Easy to build, nice in the demo. Defensibility-2: every competitor will ship this by end of year. Low marginal value to the user — they can already read the sentiment from the existing emoji breakdown.

**5. AI chatbot for HR partners.** Commodity. Vendors already do this well. Reclaim the quarter; don't build.

**6. AI-generated survey question suggestions.** Generic, no defensibility, and HR partners specifically don't want "AI" writing their survey — they want control. User research from interviews confirms.

---

# 5. The Build-First Recommendation: AI-Summarized Survey Themes

**The user moment.** It's Monday morning. A team manager opens their weekly Beacon digest. Right now: a graph + a list of 14 raw open-text comments. They skim, get overwhelmed, save-for-later, don't return.

After the build: the same email opens with three short paragraphs:
- "**Recognition** (12 of 18 responses, high confidence): Your team feels recognized when you publicly share customer wins. Less so when feedback is given 1:1."
- "**Workload** (7 of 18 responses, medium confidence): Concerns about workload spikes during quarter-end. Several mentions of late-night Slack messages from leadership."
- "**Growth** (4 of 18 responses, low confidence — small signal): A few mentions of wanting more cross-functional exposure. Worth probing in 1:1s."

Each paragraph links to the source responses. Confidence is shown explicitly. A small "Was this helpful?" reaction loop trains the model further over time.

**Success metric.**
- **Primary:** Weekly active managers (WAM) lifts from 34% → **50%** within 60 days of launch.
- **Secondary:** Email click-through rate doubles (current 9% → target 18%).
- **Counter-metric:** Manager-reported "I trust the summary" stays above 70% (measured via in-product micro-survey).

**Why this one first.**
- Top scores on value, impact, and TTV.
- Beacon's taxonomy advantage makes it defensible.
- Engineering load is moderate (3–4 weeks for v1) — your two LLM-experienced engineers can own it without disrupting other roadmap work.

**De-risk before commitment.**
- **Week -1: Wizard-of-Oz test.** Hand-summarize 10 real recent surveys. Send to 10 friendly managers. Measure open + engagement. If <40% engagement, the *concept* isn't strong enough yet — pause, don't build.
- **Week 0: 50-survey eval set.** Score the model's output against expert summaries for 50 real surveys. Don't ship until you hit 80% expert agreement on theme identification.

**Rough shape of work.**
- Phase 1 (Wks 1–3): Eval set + first prompt iteration + confidence-scoring scaffolding.
- Phase 2 (Wks 4–5): UX implementation in weekly email + in-product view.
- Phase 3 (Wks 6–8): Closed beta with 5 design partners, instrumentation.
- Phase 4 (Wk 9+): GA rollout with feature flag, measure WAM.

**What would make this fail.**
- Trying to scale beyond one feature (the AI chatbot temptation).
- No confidence threshold = a wrong summary on a sensitive theme (e.g., harassment signal misclassified as "workload"). Plan for that case with a "low confidence" guardrail that defaults to "showing raw responses."
- Treating it as a feature ship vs. an ongoing model-quality program.

---

# 6. The Roadmap

**Now (0–8 weeks).** Build #1 (AI-Summarized Survey Themes). Run the de-risk steps before commitment.

**Next (8 weeks–2 quarters).** Build #2 (Open-text auto-categorization for HR partners). The model groundwork from #1 transfers directly; ~half the effort. Then evaluate #3 with what we've learned from confidence-scoring.

**Later / revisit.** #4 (sentiment), #6 (question suggestions) — revisit only if #1–3 underperform and you need to refresh the AI story for customers. Otherwise, skip.

---

# 7. What NOT to Do (and Why)

| Don't | Why |
|---|---|
| Build the **AI chatbot for HR partners** (#5) | Commodity. Every competitor either has one or will. Buying from a partner (Zendesk, Intercom, Ada) is faster, cheaper, and removes a maintenance burden. |
| Build **AI-generated survey questions** (#6) | HR partners want control; user research confirms aversion to AI-written questions. Building would erode trust more than it adds value. |
| Build **all six features as a "platform"** | Common trap in companies behind on AI. Six features at 30% each won't move WAM. One feature at 90% will. Pick. |
| Use any **third-party AI vendor that trains on customer data** | Compliance-blocking given the SOC 2 work in progress. Reasonable vendors offer no-train terms — verify in writing. |
| Add an **"AI-Powered" badge** to the marketing site before any feature ships | Sets expectations you can't yet meet. Lead with the feature outcome ("Cut managers' weekly survey-reading time by 90%"), not the AI label. |

---

# 8. Foundations Check

- **Data readiness:** Strong. Existing feedback-category taxonomy is the unfair advantage. Recommend formalizing it as a versioned schema before scaling AI features.
- **Adoption plan:** Currently weak. The build-first feature must include a launch campaign aimed at managers (not just an in-app banner). Customer Success Lead is the natural owner.
- **Measurement:** WAM and email CTR are well-instrumented. The "trust" counter-metric needs a new in-product micro-survey — small Lift, ~3 days of eng work.
- **Team capability:** 2 of 7 engineers have shipped LLM features. Sufficient for #1 + #2. Consider one new senior hire if pursuing the broader roadmap aggressively.

---

# 9. Recommended Next Step

Based on this audit, the highest-leverage next move is to turn the **AI-Summarized Survey Themes** recommendation into a shippable plan and de-risk it before commitment.

That's exactly what an **AI Product Sprint** (4–6 weeks, $12k–$18k) does — we'd run the Wizard-of-Oz test, build the 50-survey eval set, draft the spec, and hand your team a ready-to-build plan with confidence thresholds defined.

If you'd rather have ongoing product judgment on call as you execute, an **Advisory Retainer** is the lighter-touch path.

Either way, the audit's primary value is already delivered: a defensible ranking and an explicit "what NOT to build" list that should reshape next quarter's roadmap.

Happy to scope the next step on our walkthrough call.

---

## How to use this example

- **Voice:** Note the specific numbers, the named risks, the explicit "don't build" calls. Resist softening any of these in your real engagements; sharpness is the product.
- **Length:** ~6 pages of dense content is the sweet spot. Less feels thin; more is padding. Aim for a deliverable a CEO could absorb in 15 minutes and a product team could work from for a quarter.
- **Personalization:** Every real audit will need genuine customization — the metrics, the user moments, the named opportunities. Don't copy the Beacon HR examples; use the structure.
- **The "What NOT to Do" section is the test of senior judgment.** Junior consultants leave it out (or hide it) because saying no is uncomfortable. It's the single highest-value section. Always include it; always make it specific.
