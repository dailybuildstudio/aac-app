# 05 — Security Testing (non-intrusive)

Goal: verify web security hygiene without doing anything that looks like an attack.

**Scope:** read-only checks against publicly reachable surface. No fuzzing, no brute force, no exploit attempts, no automated scanners that hammer the origin. If you need penetration testing later, hire a firm with a scoped engagement letter.

---

## 1. TLS / HTTPS

### Qualys SSL Labs

URL: `https://www.ssllabs.com/ssltest/analyze.html?d=scripturebook.org`

- [ ] Overall grade **A or higher**.
- [ ] TLS 1.2 + 1.3 enabled; TLS 1.0/1.1 disabled.
- [ ] No weak ciphers (RC4, 3DES, CBC-mode SHA1).
- [ ] Certificate valid, ≥ 30 days to expiry, correct hostnames (including `www`).
- [ ] HSTS enabled with reasonable `max-age` (≥ 6 months) and `includeSubDomains` if appropriate.

### Manual checks

- [ ] `http://` redirects to `https://` for every URL (not just root).
- [ ] No **mixed content** warnings in DevTools console on any page.
- [ ] Certificate chain complete (no "intermediate missing" warnings on mobile).

---

## 2. Security headers

### securityheaders.com

URL: `https://securityheaders.com/?q=https%3A%2F%2Fscripturebook.org`

Aim for **A or higher**. The big ones:

| Header                          | Why                                              | Good default                                         |
| ------------------------------- | ------------------------------------------------ | ---------------------------------------------------- |
| `Strict-Transport-Security`     | Forces HTTPS                                     | `max-age=31536000; includeSubDomains`                |
| `Content-Security-Policy`       | XSS mitigation                                   | Start strict, loosen as needed                       |
| `X-Content-Type-Options`        | Stops MIME sniffing                              | `nosniff`                                            |
| `X-Frame-Options`               | Clickjacking (older sites; CSP `frame-ancestors` supersedes) | `DENY` or `SAMEORIGIN`               |
| `Referrer-Policy`               | Limits referrer leak                             | `strict-origin-when-cross-origin`                    |
| `Permissions-Policy`            | Disables unused powerful features                | `camera=(), microphone=(), geolocation=()`           |
| `Cross-Origin-Opener-Policy`    | Process isolation                                | `same-origin`                                        |

CSP is the hardest one — start in **report-only** mode, watch the violations endpoint, then enforce.

---

## 3. Cookies

In DevTools → Application → Cookies, for every cookie set:

- [ ] `Secure` flag set (HTTPS-only).
- [ ] `HttpOnly` set on session cookies (not readable from JS).
- [ ] `SameSite=Lax` (or `Strict` for auth) — at minimum not `None` without `Secure`.
- [ ] No PII in cookie values (use opaque session IDs).
- [ ] Reasonable expiry (don't set 10-year cookies for session data).

---

## 4. Information leakage

- [ ] **Server header** doesn't reveal exact version (`Server: nginx` OK; `Server: nginx/1.18.0 (Ubuntu)` is a leak).
- [ ] **`X-Powered-By`** header removed if present.
- [ ] **Stack traces** never shown on error pages — generic 500 message only.
- [ ] **`.git/`, `.env`, `.DS_Store`, `backup.zip`** not reachable at root. Check:
  - `curl -I https://scripturebook.org/.git/config`
  - `curl -I https://scripturebook.org/.env`
  - Expect 404, not 200.
- [ ] **Source maps** (`.js.map`) — fine to ship, but be aware they expose original source. Decide intentionally.
- [ ] **Admin paths** (`/admin`, `/wp-admin`, `/phpmyadmin`) — either don't exist, or behind auth + IP allowlist.

---

## 5. Authentication (if applicable)

- [ ] **Password policy**: no max length below 64, allow all printable chars (no banning special chars).
- [ ] **Password storage**: bcrypt/argon2/scrypt with sane work factor (not MD5/SHA1, not plaintext).
- [ ] **Rate limiting** on login + password reset (verify with a few manual attempts — don't script it).
- [ ] **MFA option** available for accounts (TOTP minimum).
- [ ] **Password reset** uses single-use, time-limited tokens.
- [ ] **Session invalidation** on logout, password change, and email change.
- [ ] **Account enumeration** avoided — "if this email exists, we sent a link" on reset.

---

## 6. Common web vulns — spot check (light, manual, on your own data)

Do NOT do these on production user data or accounts you don't own.

- [ ] **Reflected XSS** — paste `<script>alert(1)</script>` and `"><svg onload=alert(1)>` into your own search/forms. Expect literal text, no popup.
- [ ] **CSRF** — sensitive POSTs (account changes, payment) have anti-CSRF tokens or `SameSite` cookies.
- [ ] **Open redirect** — try `https://scripturebook.org/?redirect=https://evil.example.com` style params; should reject or only allow same-origin.
- [ ] **CORS** — `Access-Control-Allow-Origin: *` should NOT appear on endpoints that return user data.
- [ ] **Clickjacking** — try embedding the site in an `<iframe>` from a local HTML file; expect it to be blocked by CSP/X-Frame-Options.

---

## 7. Dependencies & supply chain

If you control the repo:

- [ ] `npm audit` / `pip-audit` / equivalent — no high/critical unpatched.
- [ ] **Dependabot / Renovate** enabled.
- [ ] No abandoned packages (last commit > 2 years) in critical paths.
- [ ] Lockfile committed (`package-lock.json`, `poetry.lock`).
- [ ] CI doesn't run untrusted code from PRs with secrets exposed.

---

## 8. Privacy / compliance touchpoints

- [ ] **Privacy policy** linked from footer, describes what's collected.
- [ ] **Cookie banner** if you serve EU users + use non-essential cookies.
- [ ] **Analytics** anonymized (or use a privacy-respecting provider — Plausible, Fathom).
- [ ] **Third-party scripts** minimized; each one reviewed for what it can see.
- [ ] **Contact / data deletion request** path exists (helps with GDPR/CCPA).

---

## 9. Mozilla Observatory (one more scan)

URL: `https://observatory.mozilla.org/`

Aim for **B+ or better**. It pulls together headers + cookies + redirects into one view.

---

## 10. Record in run doc

```
## Security — YYYY-MM-DD

- SSL Labs: A+
- securityheaders.com: A (missing Permissions-Policy)
- Observatory: B+
- Cookies: ✅
- Info leak scan: ✅ .git/.env not reachable
- Manual XSS spot check: ✅ payloads escaped
- Notable: Server header reveals "nginx/1.24.0 (Ubuntu)" — recommend stripping version
```

---

## When to escalate

If any of these show up, fix before next deploy:

- TLS grade below A
- Any header below "A" rating on securityheaders.com that you control
- Any sensitive cookie missing Secure/HttpOnly
- Reachable `.env`, `.git/config`, backup files
- Stack traces leaking from error pages
- Any reflected XSS that survives

For deeper testing (authenticated, application-logic, business-logic flaws), hire a pentest firm with a written scope and rules of engagement.
