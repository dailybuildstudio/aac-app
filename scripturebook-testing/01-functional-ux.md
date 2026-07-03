# 01 — Functional & UX Testing

Goal: verify every user-facing path works correctly and feels right on the devices/browsers your audience actually uses.

---

## 1. Browser & device matrix

Test the **top 3 browsers** on the **top 3 viewports** for your audience. Defaults below — adjust based on real analytics once you have them.

| Browser            | Desktop (1440×900) | Tablet (768×1024) | Mobile (390×844) |
| ------------------ | :----------------: | :---------------: | :--------------: |
| Chrome (latest)    | ✅                  | ✅                 | ✅                |
| Safari (latest)    | ✅                  | ✅                 | ✅                |
| Firefox (latest)   | ✅                  | —                 | —                |
| Edge (latest)      | ✅                  | —                 | —                |
| Chrome (prev. ver) | spot-check         | —                 | —                |

Also test: real iPhone (Safari), real Android (Chrome). Emulators miss touch quirks.

---

## 2. Core flows to verify

Fill in flows specific to scripturebook.org. Generic starter list:

### Public / unauthenticated

- [ ] Landing page renders, hero CTA visible above the fold
- [ ] Primary nav links go to correct pages
- [ ] Footer links (about, contact, privacy, terms) resolve
- [ ] Search (if present) — empty query, common word, gibberish, special chars
- [ ] Sign up / register flow (if applicable)
- [ ] Login flow — happy path, wrong password, password reset
- [ ] Logout returns to a sensible landing page

### Content / reading

- [ ] Scripture/book content loads completely (no truncation)
- [ ] Navigation between chapters/sections (next/prev, jump-to)
- [ ] Bookmarks / highlights / notes (if features exist) persist across reload
- [ ] Sharing (copy link, social share) produces a valid URL
- [ ] Print view (Cmd+P) is legible and not broken

### Forms

For every form: contact, signup, feedback, etc.

- [ ] Empty submit → clear validation messages, no silent failure
- [ ] Invalid email format → caught client-side
- [ ] Successful submit → confirmation + (if applicable) email arrives
- [ ] Double-click submit doesn't double-post
- [ ] Browser back after submit doesn't resubmit

### Edge cases

- [ ] Very long input (paste 10kb of text into a field)
- [ ] Unicode/emoji in inputs (names with accents, RTL text, 😀)
- [ ] Slow connection (DevTools → Network → "Slow 3G") — does the UI degrade gracefully?
- [ ] Offline → reconnect — does it recover?
- [ ] Refresh mid-flow — state recovery sensible?

---

## 3. UX heuristics (Nielsen-style spot check)

1. **Visibility of system status** — loading spinners, progress indicators present?
2. **Match real world** — language is reader-friendly, not jargon
3. **User control** — undo, back, cancel always available
4. **Consistency** — buttons styled the same way across pages
5. **Error prevention** — destructive actions confirm
6. **Recognition over recall** — primary actions visible, not hidden
7. **Flexibility** — keyboard shortcuts for power users (where it matters)
8. **Aesthetic & minimalist** — no clutter, hierarchy obvious
9. **Recover from errors** — error messages explain *what* and *how to fix*
10. **Help & docs** — findable when needed

Rate each 1–5; anything ≤3 becomes a follow-up issue.

---

## 4. Recording results

For each browser/viewport cell in the matrix, record:
- Pass / fail / partial
- Screenshot of any failures (drag into the run doc)
- Repro steps if not obvious

Save in `runs/YYYY-MM-DD-run.md` under a `## Functional / UX` heading.
