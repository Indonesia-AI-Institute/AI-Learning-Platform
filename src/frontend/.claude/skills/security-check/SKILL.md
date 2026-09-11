---
name: security-check
description: Review a frontend diff or the current frontend codebase against this project's specific security checklist — auth/token handling, route protection, XSS surface, CSP, dependency hygiene, Docker image config. Use when asked to review frontend changes for security issues, or to audit the frontend's current security posture.
---

# Frontend security check

Checks specific to *this* codebase's actual history — every item here
maps to something that was either found and fixed, or deliberately
evaluated and left as a documented gap. Not a generic OWASP checklist;
read `CLAUDE.md`'s Critical Rules and "Known, deliberately deferred gaps"
sections first, since a review should distinguish a new problem from an
already-accepted one.

## Checklist

**Token/session handling**
- [ ] No token, session id, or credential is written to `localStorage`,
      `sessionStorage`, or a client-side store (Zustand, Redux, etc.).
      Auth state is the httpOnly cookie only (Critical Rule 4) — grep for
      new `localStorage`/`sessionStorage` usage in any diff touching auth.
- [ ] No `Authorization` header is manually constructed from a token the
      frontend holds — this app doesn't do bearer-token auth at all: cookie
      only, via `withCredentials: true` on the shared `api` instance.

**Route protection**
- [ ] A new protected page lands under `src/app/(dashboard)/` (covered by
      `src/proxy.ts`'s default-protect matcher) rather than requiring a
      matcher/`PUBLIC_PATHS` change. If `PUBLIC_PATHS` *is* being changed,
      confirm the new public route genuinely has no sensitive data to
      protect — the guard is presence-only and structurally cannot
      validate the cookie itself (Critical Rule 2's "known gaps" note).
- [ ] `src/proxy.ts` still lives at `src/proxy.ts` (not `middleware.ts`,
      not moved to the package root) — verify with
      `find src/frontend -iname "middleware.ts" -o -iname "proxy.ts"`
      and confirm only the correct file exists. This exact misplacement
      silently disabled all route protection for a full session before
      (Critical Rule 2) — don't assume a file named "middleware" or
      "proxy" existing anywhere means the guard is active.

**XSS / injection surface**
- [ ] No new `dangerouslySetInnerHTML` or `rehype-raw` usage. This app
      renders all markdown (chat messages, task descriptions) through
      `react-markdown` without raw-HTML passthrough — that's the primary
      XSS defense; a new raw-HTML render path would bypass it.
- [ ] Any new use of `eval`, `new Function(...)`, or dynamically
      constructed `<script>` tags — should be zero; flag any occurrence.
- [ ] User-controlled text rendered outside React's own escaping (e.g.
      into a `title` attribute built via string concatenation, a `style`
      attribute, or an injected CSS custom property) — check for
      reflected-content risk even without `dangerouslySetInnerHTML`.

**CSP / headers**
- [ ] `next.config.ts`'s CSP wasn't loosened further than the documented
      `'unsafe-inline'` on `script-src`/`style-src` (Critical Rule 8) —
      a new external script/style source needs an explicit, reviewed
      addition to the relevant `-src` directive, not a switch to `*`.
- [ ] `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and the
      `Permissions-Policy` block are all still present.

**Dependency hygiene**
- [ ] Run `bun audit` — zero known vulnerabilities is the baseline this
      codebase has maintained; investigate anything new.
- [ ] `package.json`'s `trustedDependencies` only lists packages actually
      present in `bun.lock` (Critical Rule 6) — `grep <name> bun.lock`
      each entry.
- [ ] No `pnpm`/`npm`/`yarn` lockfiles or config resurfaced (Critical
      Rule 7) — `find src/frontend -iname "*pnpm*" -o -iname "*.npmrc" -o -iname "package-lock.json" -o -iname "yarn.lock"`.

**Docker / deployment**
- [ ] No secret or environment-specific value baked into the Dockerfile
      via `ENV` or a build `ARG` default — `NEXT_PUBLIC_API_URL`, `PORT`
      must stay runtime-only (Critical Rules 1 and 3).
- [ ] The image still runs as the non-root `nextjs` user (check the
      Dockerfile hasn't dropped the `USER nextjs` line).

## Reporting

For each finding: file, line, what's wrong, and the concrete exploit
scenario (not just "this is bad practice") — matching the standard this
project's earlier backend security review used. If nothing is found in a
section, say so explicitly rather than omitting it, so the report reads
as a completed checklist, not a partial scan.
