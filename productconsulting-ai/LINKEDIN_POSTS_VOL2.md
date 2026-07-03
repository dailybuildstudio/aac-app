# LinkedIn Post Pack — Volume 2 (Posts 7–14)

*Extends `LINKEDIN_POSTS.md` with 8 more drafts in varied angles. Mix and match with Vol 1 for ~14 weeks of weekly content. Each one is built to stand on its own — no required reading order.*

**Voice guardrails (same as Vol 1):**
- Lead with the contrarian/surprising claim
- Concrete numbers > vague claims
- At least one "what NOT to do" beat per post
- Short paragraphs, no jargon, no hedging
- Soft CTA — never beg

---

## Post 7 — Personal-story angle

> Spent years in product roles where the AI question was getting louder and the answers were getting worse.
>
> Every quarter, more "AI strategy" decks. Every quarter, the same broken loop: a feature ships, doesn't move the metric, gets quietly retired six months later.
>
> The teams that broke the loop had two things in common, and neither was a better model.
>
> **One: an explicit "what NOT to build" list.** Most roadmaps don't have one. The list of "no" — written down, defended in a room — was always upstream of the teams that shipped well.
>
> **Two: someone senior willing to be unpopular about scope.** AI features have a built-in incentive to grow. Someone has to push the other direction. That role almost never lives in the title that should own it.
>
> That's the gap productconsulting.ai exists to fill. Senior product judgment in the work, not in the kickoff.
>
> If you're in the loop I described, you already know what to do. The hard part isn't seeing it.

---

## Post 8 — Contrarian / "AI consultant grift" critique

> The going rate for "AI strategy" consulting in 2026 is somewhere between $50k and $500k.
>
> What you typically get for that money:
>
> ▸ A 60-page deck.
> ▸ A "maturity model" with your company plotted on it.
> ▸ A roadmap that names 8–14 AI features.
> ▸ Zero working software.
>
> Six months later, your team is still shipping the same product. The deck is in a drive nobody opens.
>
> Here's what would actually move the needle for that money, in order of leverage:
>
> 1. A 2-week, fixed-scope audit that scores your AI candidate features and explicitly tells you what NOT to build. Outcome: 1 quarter of reclaimed engineering.
> 2. A senior product practitioner embedded 2–3 days/week, owning the AI feature work end-to-end. Outcome: shipped features.
> 3. Almost anything else.
>
> The decks aren't useless because the consultants aren't smart. They're useless because the senior smart people are in the kickoff; the delivery is junior.
>
> Buy delivery, not advice.

---

## Post 9 — Public teardown (anonymized)

> A recent AI feature launch I've been studying:
>
> Big-name product. Launched a "smart [thing]" with a polished demo video. Trade press wrote it up. The CEO posted about it.
>
> Three months in:
>
> ▸ Active users of the feature: **<5%** of eligible accounts.
> ▸ Of those, **<30%** used it more than once.
> ▸ Removed quietly from the navigation last week.
>
> What went wrong, in order of how much each mattered:
>
> **1. Wrong user moment.** The feature improved a part of the user's workflow they didn't think of as broken. So the demo was impressive, but the muscle memory of the workflow stayed unchanged.
>
> **2. No success metric defined pre-launch.** I asked. There wasn't one. So nobody could tell if "5% adoption" was disaster or expected.
>
> **3. The build was scoped on the team's capacity, not the user's need.** Six months of engineering went into a feature that, in hindsight, should have been a 6-week test.
>
> The model worked great. The product didn't.

---

## Post 10 — What I'd look for hiring an AI PM

> If you're hiring a Product Manager whose first quarter includes "ship the first AI feature," here's what would move me to "yes" in an interview.
>
> **What I'd test for:**
>
> ▸ Can they name a specific user moment your AI should improve, after 30 minutes with your product? Not a generic improvement — a moment.
>
> ▸ Can they articulate what they would explicitly **NOT** build, and why? If everything sounds like a good idea, that's a no-hire.
>
> ▸ When asked "how would you measure if it worked," do they pick a real metric and a target — or hedge?
>
> ▸ Have they ever pulled a feature back after launch? (The right answer is yes; this signals maturity.)
>
> ▸ Do they treat "the model" as the easy part of the problem? They should.
>
> **What I'd ignore in resumes:**
>
> ▸ "Led AI strategy at [BigCo]." Strategy without shipping is debate club.
> ▸ Specific framework certifications. The framework matters less than the judgment using it.
> ▸ Prompt engineering as a primary skill. It's table stakes now, not a differentiator.
>
> The AI part of an AI PM is increasingly commodity. The product part is the whole job.

---

## Post 11 — Data + product = a rare combo

> Most AI features fail at the seam where data meets product.
>
> Engineers can call the API. Data scientists can build the model. Product can define the JTBD. But the seam — where you turn raw model outputs into something a user trusts and uses — is where most teams have a blind spot.
>
> A few signs your team has the seam covered:
>
> ▸ Every AI output has a **confidence signal** the user can see.
>
> ▸ Every AI output has a **recovery path** — edit, undo, override.
>
> ▸ The team has an **eval set** that runs before every shipped change.
>
> ▸ "Better model" is treated as one input, not the whole roadmap.
>
> Signs your team doesn't:
>
> ▸ The product roadmap reads like "improve the model" without saying what the user gets.
>
> ▸ Nobody can tell you the model's accuracy on a known test set this week.
>
> ▸ The feature ships, accuracy degrades silently, nobody notices until support tickets spike.
>
> Data depth + product judgment is rare on the same person — and it's exactly what the seam needs.

---

## Post 12 — Founder-specific (early-stage AI pitfalls)

> Three AI pitfalls I keep seeing at seed and Series A:
>
> **1. Building the AI feature your VC asked about.**
>
> The board mentioned LLMs. You added LLMs. Now you have an AI feature optimizing for nobody's actual job.
>
> Fix: have one written sentence about the user moment the feature improves. If you can't write it, don't build it.
>
> **2. Treating "ship AI" as a milestone, not a metric.**
>
> The feature shipping is not the win. The feature moving a number is the win. Most founders I talk to celebrate launch day, then go quiet about adoption six weeks later.
>
> Fix: write the success metric and target *before* the feature gets a code branch. If you won't name a number you're committing to, the feature isn't ready.
>
> **3. Hiring an "AI engineer" instead of a senior product thinker.**
>
> Engineers who can call APIs are everywhere. Product leaders who can decide which AI feature is worth building are the rare role.
>
> Fix: pay for the judgment. The build is the easier hire.
>
> If your AI roadmap is generating quarterly board excitement and no measurable customer behavior change, two of these three are probably true.

---

## Post 13 — Reframe of a familiar idea

> Andy Grove's "OUTPUT = NEW PRODUCT / TIME" feels like it was written for AI features.
>
> Most AI work fails the numerator — the team ships features, but nothing the user perceives as a "new product."
>
> Most AI work fails the denominator — what should be a 6-week test becomes a 6-month project.
>
> A useful question to ask of any AI feature on your roadmap:
>
> ▸ Is this a **new product** in the user's eyes? Or is it the same product with a different button?
>
> ▸ Could it ship in **6 weeks**? If no, what would the 6-week version look like?
>
> The AI features that compound — that customers describe to other customers, that show up in renewal conversations — are the ones that pass both tests.
>
> Most don't.

---

## Post 14 — A short story about saying "no"

> A founder asked me what they should build first with AI.
>
> I asked what was on their list.
>
> They named six features. We scored each one. Three were strong, three were weak.
>
> "Okay," I said. "Don't build these three."
>
> Long pause.
>
> "But the team's already excited about the chatbot."
>
> That moment is where every AI roadmap I've ever seen quietly goes wrong.
>
> "Excited about the chatbot" is a signal — but it's a signal about team dynamics, not user value. The chatbot scored a 14 because it's the wrong build. Excitement doesn't change the math.
>
> The senior move isn't picking the build-first. It's holding the line on the build-never.
>
> If you can't kill the wrong AI feature when the team is excited about it, you don't have a roadmap. You have a wishlist.
>
> The hardest part of the job is the "no" you can defend on a Monday morning. The framework is for that conversation.

---

## Cross-Vol notes
- **Avoid double-posting** similar angles in adjacent weeks (e.g., don't follow Vol 1 Post 2 — "what NOT to build" — with Vol 2 Post 14 — also a "no" story). Space them at least 3 weeks apart.
- **Recycle winners.** Whichever post lands best becomes the first ad creative in `LINKEDIN_ADS.md`.
- **Test cadence.** Some weeks 2 posts (Tue + Thu) tests well. Don't exceed 3/week — drops engagement.
