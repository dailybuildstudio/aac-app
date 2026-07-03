# 02 — Performance Testing

Goal: confirm scripturebook.org loads fast, stays responsive, and clears Core Web Vitals thresholds on real-world hardware/network conditions.

---

## 1. Targets (Core Web Vitals — Google's "good" thresholds)

| Metric                              | Good       | Needs work | Poor    |
| ----------------------------------- | ---------- | ---------- | ------- |
| **LCP** (Largest Contentful Paint) | ≤ 2.5 s    | ≤ 4.0 s    | > 4.0 s |
| **INP** (Interaction to Next Paint)| ≤ 200 ms   | ≤ 500 ms   | > 500 ms|
| **CLS** (Cumulative Layout Shift)  | ≤ 0.1      | ≤ 0.25     | > 0.25  |
| **TTFB** (Time to First Byte)      | ≤ 0.8 s    | ≤ 1.8 s    | > 1.8 s |
| **FCP** (First Contentful Paint)   | ≤ 1.8 s    | ≤ 3.0 s    | > 3.0 s |

Aim for **green on mobile** — that's the bar Google ranks against.

---

## 2. Pages to measure (every run)

Pick representative pages:
- [ ] **Home** — `/`
- [ ] **Book/reading page** (a long content page)
- [ ] **Search results** (if present)
- [ ] **Account page** (if logged in)
- [ ] **One slow page from last run** (regression check)

---

## 3. Tools & steps

### 3a. Lighthouse (Chrome DevTools)

1. Open page in incognito (no extensions skewing results).
2. DevTools → Lighthouse tab.
3. Categories: **Performance, Accessibility, Best Practices, SEO**.
4. Device: **Mobile** (most important) then **Desktop**.
5. Run 3 times; record the **median** score (single runs are noisy).

Record: score, LCP, INP, CLS, TBT, FCP, screenshot of the report.

### 3b. PageSpeed Insights (field + lab data)

URL: `https://pagespeed.web.dev/`

- Field data = real Chrome users (28-day rolling). Authoritative.
- Lab data = synthetic, like Lighthouse.
- Look at the **Origin Summary** to see CWV across the whole site.

### 3c. WebPageTest (deeper diagnostics)

URL: `https://www.webpagetest.org/`

- Run from at least 2 locations (closest to your audience + one far).
- Connection: "4G" mobile profile.
- Inspect the **waterfall** — anything blocking? Render-blocking JS/CSS?
- Note the **Speed Index** and **Time to Interactive**.

### 3d. Real device test (very important)

A mid-range Android on a coffee-shop Wi-Fi tells you more than any synthetic test. At minimum:
- [ ] Load home page on real phone, time it with stopwatch (rough proxy).
- [ ] Scroll the long reading page — any jank? Jumpy scrolling?
- [ ] Tap a button — does it respond within 100 ms visually?

---

## 4. Common wins to look for

If scores are low, these usually account for it:

- **Images:** wrong format (use AVIF/WebP), wrong size (serve responsive `srcset`), missing `loading="lazy"` below the fold.
- **Fonts:** too many weights, no `font-display: swap`, no preloading the LCP font.
- **JavaScript:** large bundles, no code splitting, third-party scripts (analytics, chat widgets) blocking main thread.
- **CSS:** unused styles, large blocking stylesheet — consider critical CSS inlining.
- **No caching:** missing `Cache-Control` headers on static assets.
- **No CDN:** if origin is single-region, audiences abroad eat full RTT.
- **CLS culprits:** images without `width`/`height`, ad slots that pop in, web fonts swapping.

---

## 5. Stress / load (optional)

If traffic spikes are expected (e.g. featured by a podcast):

- `k6` or `Artillery` script — ramp from 1 → 100 RPS over 5 min on the home page.
- Watch server response time and error rate.
- **Only run against staging or with explicit approval** — load testing prod can look like an attack to your host/CDN.

---

## 6. Record in run doc

```
## Performance — YYYY-MM-DD

Page: /
- Lighthouse mobile: Perf 87 / A11y 98 / BP 92 / SEO 100
- LCP 2.1s | INP 140ms | CLS 0.03 | TTFB 0.6s
- Issues: hero image is 1.2MB JPEG, recommend WebP @ ~180KB
```
