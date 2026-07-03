# 03 — Accessibility Testing

Goal: scripturebook.org meets **WCAG 2.2 Level AA** and is usable with keyboard, screen reader, and at 200% zoom.

Accessibility for a reading-focused site matters more than usual: readers with vision, motor, or cognitive needs are part of your core audience.

---

## 1. Automated scan (catches ~30% of issues)

### axe DevTools

1. Install axe DevTools browser extension (free).
2. Open each key page → DevTools → axe → "Scan all of my page".
3. Triage:
   - **Critical / Serious** → fix before next release.
   - **Moderate** → ticket for the backlog.
   - **Minor** → judgment call.

### WAVE

URL: `https://wave.webaim.org/` — paste each key URL, review errors & contrast issues.

### Lighthouse → Accessibility tab

Aim for ≥ 95. Sub-95 usually means missing alt text, low contrast, or unlabeled inputs.

---

## 2. Manual checks (catches the other ~70%)

### Keyboard only — unplug your mouse

- [ ] **Tab** through every interactive element on each key page.
- [ ] Visible **focus ring** on every focusable element (not removed by CSS).
- [ ] Tab order matches visual order — no random jumps.
- [ ] **Enter / Space** activates buttons and links.
- [ ] **Esc** closes modals/dropdowns.
- [ ] No **keyboard traps** (can't tab out of a widget).
- [ ] **Skip to content** link present at top (helpful for screen reader users).

### Screen reader

Pick one:
- **VoiceOver** (macOS): Cmd+F5 to toggle. Cheat sheet: ctrl+option+arrows to navigate.
- **NVDA** (Windows, free).

Test:
- [ ] Headings announce in logical order (H1 → H2 → H3, no skipping).
- [ ] Images have meaningful **alt text** (or `alt=""` if decorative — don't omit `alt`).
- [ ] Form fields have labels (announced when focused).
- [ ] Buttons announce their purpose ("Search", not just "Button").
- [ ] Links make sense out of context ("Read Genesis 1", not "click here").
- [ ] Dynamic content (e.g. "loading...", search results updating) uses **ARIA live regions** so SR users hear it.

### Zoom & reflow

- [ ] **200% browser zoom** — no content cut off, no horizontal scrolling on mobile widths.
- [ ] **400% zoom** at desktop width (WCAG 2.2 SC 1.4.10) — content reflows to single column without losing functionality.
- [ ] **Text spacing** override (use the WCAG bookmarklet) — nothing overlaps or clips.

### Color & contrast

- [ ] Text vs. background ≥ **4.5:1** (normal text) or **3:1** (large text ≥18pt or 14pt bold).
- [ ] UI components and graphical objects ≥ **3:1** against adjacent colors.
- [ ] Information not conveyed by **color alone** (e.g. error fields need an icon or text, not just red border).
- [ ] **Dark mode** (if supported) meets the same ratios.

Tool: Chrome DevTools → inspect element → color picker shows contrast ratio.

### Motion & cognition

- [ ] No **flashing content** > 3 times/sec (seizure risk).
- [ ] **Auto-play video/audio** is disabled or has clear stop control.
- [ ] **Reduced motion** preference respected (`prefers-reduced-motion: reduce` disables non-essential animation).
- [ ] Sessions don't time out without warning + extension option.

### Forms

- [ ] Labels are **programmatically associated** (`<label for="">` or wrap).
- [ ] Errors identified by text, not just color, and linked to the field with `aria-describedby`.
- [ ] Required fields marked in text (`required` attr + visible "required" or `*`).

---

## 3. Specific to a reading site

- [ ] **Reader mode** works (try Safari Reader, Firefox Reader View).
- [ ] **Font size controls** (if you provide them) actually persist across pages.
- [ ] **Dyslexia-friendly options** considered (line spacing, font choice — bonus, not required).
- [ ] **Language attribute** set on `<html lang="en">` — and `lang` overrides on quoted passages in other languages (Hebrew, Greek, Latin).
- [ ] **Reading order in DOM** matches visual order (CSS shouldn't rearrange semantics).

---

## 4. Record in run doc

```
## Accessibility — YYYY-MM-DD

- axe automated: 0 critical, 2 serious (alt text, color contrast on footer link)
- Keyboard: ✅ except no visible focus on hero CTA
- VoiceOver: ✅ headings logical, alt text good
- Zoom 200%: ✅
- Contrast: ❌ footer link #888 on #fff = 3.5:1, needs ≥4.5
```
