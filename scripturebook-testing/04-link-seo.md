# 04 — Link Checking & SEO

Goal: no broken links, clean metadata, valid structured data, indexable by search engines, share previews look right.

---

## 1. Broken link sweep

### Quick (CLI)

```bash
# install once
brew install lychee

# sweep the live site, depth 2
lychee --max-depth 2 https://scripturebook.org

# include external links and write a report
lychee --max-depth 2 --include-fragments --output report.md https://scripturebook.org
```

Alternatives: `linkchecker https://scripturebook.org`, or web-based `https://www.deadlinkchecker.com/`.

### What to check

- [ ] 0 internal links broken (4xx/5xx).
- [ ] External links checked — note any third-party rot.
- [ ] Anchor/fragment links resolve (`#section-name` actually exists in DOM).
- [ ] No redirect chains > 1 hop (each hop costs latency).
- [ ] HTTPS only — no `http://` links sneaking in.

---

## 2. On-page SEO

For each key page (home, top reading page, about, contact):

- [ ] **`<title>`** — unique, ≤ 60 chars, primary keyword near front.
- [ ] **`<meta name="description">`** — unique, 120–160 chars, compelling.
- [ ] **Exactly one `<h1>`** per page, matches user intent.
- [ ] **Heading hierarchy** — H1 → H2 → H3, no skipping levels.
- [ ] **`<meta name="viewport">`** present (`width=device-width, initial-scale=1`).
- [ ] **Canonical URL** — `<link rel="canonical">` set, points to the preferred version.
- [ ] **`<html lang="en">`** set correctly.
- [ ] No `<meta name="robots" content="noindex">` on pages you want indexed.
- [ ] **URLs**: lowercase, hyphenated, descriptive, no session IDs.

---

## 3. Sitemap & robots

- [ ] `https://scripturebook.org/robots.txt` exists and is sensible.
  - Allows search engines on indexable content.
  - Blocks admin / login pages (`/admin`, `/login`).
  - References sitemap: `Sitemap: https://scripturebook.org/sitemap.xml`.
- [ ] `https://scripturebook.org/sitemap.xml` exists.
  - Valid XML (paste into `https://www.xml-sitemaps.com/validate-xml-sitemap.html`).
  - Includes all canonical URLs you want indexed.
  - `<lastmod>` dates are accurate (helps crawl prioritization).
  - Under 50,000 URLs / 50MB; split into sitemap index if larger.

---

## 4. Google Search Console

- [ ] Property verified (DNS or HTML file).
- [ ] Sitemap submitted.
- [ ] **Coverage report**: review excluded/error pages monthly.
- [ ] **Core Web Vitals report**: cross-check with field data.
- [ ] **Manual Actions** tab — should be empty.
- [ ] **Mobile Usability** tab — should be empty or trivial.

Same for **Bing Webmaster Tools** if your audience is meaningfully on Bing/DuckDuckGo (DDG uses Bing's index).

---

## 5. Social / share previews

Test each on every shareable page type (home, reading page, article):

| Platform   | Validator                                              |
| ---------- | ------------------------------------------------------ |
| Facebook   | `https://developers.facebook.com/tools/debug/`         |
| X (Twitter)| `https://cards-dev.twitter.com/validator` (legacy) — or just paste into draft tweet |
| LinkedIn   | `https://www.linkedin.com/post-inspector/`             |
| iMessage   | Paste the link to yourself — preview should look right |

Check:
- [ ] `og:title`, `og:description`, `og:image` (≥ 1200×630), `og:url`, `og:type`.
- [ ] `twitter:card` (`summary_large_image`), `twitter:title`, `twitter:description`, `twitter:image`.
- [ ] Image actually loads (absolute URL, HTTPS).
- [ ] Preview text isn't truncated awkwardly.

---

## 6. Structured data (schema.org)

Scripture/book content has good structured data options. Worth investing in.

Candidates:
- `Book` / `Chapter` / `Article` for reading content.
- `Organization` and `WebSite` on the home page (enables sitelinks search box).
- `BreadcrumbList` on nested pages.
- `FAQPage` on FAQ-style content.

Validate with:
- `https://search.google.com/test/rich-results` (Google's Rich Results Test)
- `https://validator.schema.org/` (general schema validation)

- [ ] No errors in Rich Results Test.
- [ ] Warnings reviewed and addressed if applicable.
- [ ] Live URL eligible for the relevant rich result type.

---

## 7. Misc SEO hygiene

- [ ] **HTTPS** everywhere, no mixed content warnings.
- [ ] **Redirects**: `http→https` and `www↔non-www` both consistent.
- [ ] **404 page** is helpful (links to home, search) and returns actual 404 status (not 200).
- [ ] **Soft 404s** absent in GSC.
- [ ] **Page speed** (covered in 02-performance.md) — ranking factor.
- [ ] **No duplicate content** — canonicals correct, no `?utm_…` versions getting indexed.

---

## 8. Record in run doc

```
## Link / SEO — YYYY-MM-DD

- lychee scan: 0 broken internal, 3 broken external (see report.md)
- Sitemap: ✅ valid, 412 URLs
- Robots: ✅
- GSC coverage: 408 indexed, 4 excluded (intentional)
- Share preview (Facebook debugger): ✅ home, ❌ /read/genesis — og:image returns 404
- Schema: Book schema valid, eligible for rich result
```
