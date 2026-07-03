# scripturebook.org — Test Plan

A working set of testing documents covering functional/UX, performance, accessibility, link/SEO, and (non-intrusive) security testing for **scripturebook.org**.

---

## How to use this folder

1. Start with **`06-master-checklist.md`** — the single sheet you actually fill in during a test pass.
2. Each numbered doc is the deep dive for one testing dimension. Use them when you need detail, repro steps, or tool commands.
3. Record results in **`runs/`** as `YYYY-MM-DD-run.md` (one per pass) so you can diff sessions over time.

```
scripturebook-testing/
├── README.md                    ← you are here
├── 01-functional-ux.md          ← user-facing flows, browser/device matrix
├── 02-performance.md            ← Lighthouse, Core Web Vitals, load times
├── 03-accessibility.md          ← WCAG 2.2 AA, screen readers, keyboard
├── 04-link-seo.md               ← broken links, metadata, sitemap, structured data
├── 05-security.md               ← non-intrusive web hygiene checks
├── 06-master-checklist.md       ← the one-pager for a full pass
└── runs/                        ← dated test results (create as you go)
```

---

## Authorization & scope

- Tester: **Amanda Shelton** (site owner / authorized).
- Target: `https://scripturebook.org` and any subdomains owned by the same project.
- Security testing: **non-intrusive only** in these docs — no fuzzing, no exploit attempts, no automated brute force. Anything intrusive needs a separate engagement plan.

---

## Recommended toolbelt

Most of these are free. Install what you'll actually use.

| Need                  | Tool                                              | Notes                          |
| --------------------- | ------------------------------------------------- | ------------------------------ |
| Performance           | Chrome DevTools Lighthouse, PageSpeed Insights    | Built into Chrome              |
| Performance (deeper)  | WebPageTest (webpagetest.org)                     | Free tier, multiple locations  |
| Accessibility (auto)  | axe DevTools (browser extension), WAVE            | Free                           |
| Accessibility (manual)| VoiceOver (macOS built-in), NVDA (Windows)        | Screen readers                 |
| Link checking         | `lychee` or `linkchecker` CLI; W3C Link Checker   | `brew install lychee`          |
| SEO/metadata          | Google Search Console, Ahrefs/SE Ranking free     | Verify ownership in GSC        |
| Structured data       | Google Rich Results Test, Schema.org validator    | Web-based                      |
| Security headers      | securityheaders.com, Mozilla Observatory          | Web-based, read-only           |
| TLS                   | Qualys SSL Labs (ssllabs.com)                     | Web-based, read-only           |
| Cross-browser         | BrowserStack / LambdaTest (paid), or real devices | Or your own phone + tablet     |

---

## Test pass cadence

- **Smoke** (≤15 min): master checklist, "must work" rows only. Run after any deploy.
- **Standard** (~2 hr): full master checklist + Lighthouse on 3 key pages.
- **Deep** (½ day): every numbered doc, multi-browser, recorded run.

Aim for one deep pass per release, smoke after every deploy.
