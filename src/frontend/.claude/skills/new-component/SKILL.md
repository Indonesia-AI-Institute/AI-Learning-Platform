---
name: new-component
description: Scaffold a new component under src/components/, following this frontend's conventions — shadcn/ui primitives for building blocks, the right client/server boundary, react-hook-form + zod for forms. Use when asked to add a new component, not a full page (see new-page for that).
---

# New frontend component

Adds a new component under `src/components/<domain>/`, matching the
patterns already established by existing ones.

## Steps

1. **Place it in the right domain folder** — `auth/`, `chat/`,
   `dashboard/`, `layout/`, or a new domain folder if this is genuinely
   the first component for a new feature area. Don't add a new component
   directly under `src/components/` (only `providers.tsx` lives there,
   for a specific reason — everything else is grouped).

2. **Decide presentational vs. stateful.** Check `CLAUDE.md`'s directory
   map / the explored component list for examples of each: a pure
   presentational component (`StatCard`, `ChatMessage`) takes props and
   renders — no `useState`/`useEffect`/hooks beyond maybe `"use client"`
   for an event handler. A stateful one (`ChatInput`, `Sidebar`) owns
   local state or calls a data-fetching hook. Don't add `"use client"` to
   a component that doesn't need it — most of `src/components/ui/`'s
   primitives that need it (Radix-based) already have it; plain
   presentational wrappers often don't.

3. **Build from `src/components/ui/` primitives** (shadcn/ui, Radix-based)
   rather than raw HTML elements where an equivalent exists — `Button`,
   `Input`, `Card`, `Select`, etc. Check `src/components/ui/` before
   reaching for a bare `<button>`/`<input>`.

4. **If the component fetches data**, use an existing hook from
   `src/hooks/` or `useQuery` directly for a single use — don't call a
   `src/services/*.ts` method directly from the component (see the
   `new-hook` skill for when to extract vs. inline).

5. **If the component is or contains a form**, follow the
   `react-hook-form` + `zod` + `components/ui/form.tsx` pattern
   (`LoginForm.tsx`/`RegisterForm.tsx`). **Read `CLAUDE.md` Critical Rule
   5 before adding any input with a sibling icon/button** (a
   password-visibility toggle, a clear button, a unit suffix) —
   `FormControl` must wrap the actual input directly; a wrapping `<div>`
   around `FormControl` breaks the label's accessible association. If the
   input needs a positioned sibling element, wrap *outside* `FormControl`:
   ```tsx
   <div className="relative">
     <FormControl><Input className="pr-10" {...field} /></FormControl>
     <button className="absolute ...">...</button>
   </div>
   ```

6. **Use `cn()` (`src/lib/utils.ts`)** for merging a caller-provided
   `className` prop with the component's own base classes, not manual
   string concatenation — it resolves Tailwind conflicts correctly (a
   caller's override wins over a same-property base class; see
   `tests/unit/utils.test.ts` for exactly which patterns do and don't
   fully conflict).

7. **Write tests** under `tests/integration/` (any test using `render()`
   from React Testing Library belongs there by this codebase's
   convention) — cover the component's actual branches (loading/empty/
   error/populated states if it fetches data; each interactive path if
   it's a form or has click/keyboard handlers). Follow `ChatInput.test.tsx`
   for a pure-interaction component or `StudentDashboard.test.tsx` for one
   that fetches data via MSW-mocked network calls.

## Notes

- Don't duplicate an existing `src/components/ui/` primitive with a
  slightly different variant — extend the existing one via its `variant`/
  `size` props (see `button.tsx`'s `cva`-based variants) or a `className`
  override, rather than creating a near-identical second component.
- A component that's only ever used in one page doesn't need to live in
  `src/components/` at all — see whether the existing pages colocate
  small page-specific pieces (check the target page's directory) before
  assuming everything needs to be a shared component.
