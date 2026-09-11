import { describe, it, expect } from "bun:test";
import { NextRequest } from "next/server";
import { proxy, config } from "@/proxy";

function requestFor(pathname: string, accessToken?: string) {
  const request = new NextRequest(`http://localhost:3000${pathname}`);
  // Not passed via the constructor's `headers` option: happy-dom's global
  // Headers polyfill (registered for the component tests elsewhere in this
  // suite) silently breaks NextRequest's own header parsing, so a `Cookie`
  // header set that way is never seen by request.cookies. Setting directly
  // on the request's cookie jar sidesteps that entirely.
  if (accessToken) {
    request.cookies.set("access_token", accessToken);
  }
  return request;
}

describe("proxy — route guard", () => {
  it("lets /login through with no cookie", () => {
    const response = proxy(requestFor("/login"));
    expect(response.status).toBe(200); // NextResponse.next() default status
    expect(response.headers.get("location")).toBeNull();
  });

  it("lets /register through with no cookie", () => {
    const response = proxy(requestFor("/register"));
    expect(response.headers.get("location")).toBeNull();
  });

  it("redirects a protected path to /login when no access_token cookie is present", () => {
    const response = proxy(requestFor("/dashboard"));
    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe("http://localhost:3000/login");
  });

  it("redirects nested protected paths too", () => {
    const response = proxy(requestFor("/tasks/abc-123/edit"));
    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe("http://localhost:3000/login");
  });

  it("lets a protected path through when access_token is present", () => {
    const response = proxy(requestFor("/dashboard", "access_token=some.jwt.value"));
    expect(response.headers.get("location")).toBeNull();
  });

  it("only checks cookie presence, not validity — an empty/garbage token still passes", () => {
    // Deliberate: the file's own comment documents this as a presence-only
    // check, with real validation left to the backend. A malformed or
    // expired cookie must still pass proxy and get rejected by the API's
    // own 401, not be silently "fixed" here.
    const response = proxy(requestFor("/dashboard", "access_token=garbage"));
    expect(response.headers.get("location")).toBeNull();
  });

  it("does not treat a path that merely starts with a public path as public", () => {
    // e.g. a hypothetical /login-history page must still require auth —
    // the check is an exact match, not a prefix match.
    const response = proxy(requestFor("/login-history"));
    expect(response.status).toBe(307);
  });

  it("redirects root path when unauthenticated (root itself redirects to /login client-side too)", () => {
    const response = proxy(requestFor("/"));
    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe("http://localhost:3000/login");
  });

  it("keeps /login public even with a query string (pathname excludes search params)", () => {
    const response = proxy(requestFor("/login?from=%2Fdashboard"));
    expect(response.headers.get("location")).toBeNull();
  });

  it("treats a trailing slash on a public path as a different, protected path", () => {
    // PUBLIC_PATHS does an exact string match — "/login/" !== "/login".
    // Next.js itself normalizes trailing slashes before most routes ever
    // see them, but this file doesn't rely on that: if trailing-slash
    // handling upstream ever changes, this documents what proxy.ts alone
    // would do with the literal pathname it was given.
    const response = proxy(requestFor("/login/"));
    expect(response.status).toBe(307);
  });

  it("treats path casing as significant — /Login is not the same as /login", () => {
    const response = proxy(requestFor("/Login"));
    expect(response.status).toBe(307);
  });

  it("redirects when a cookie jar has other cookies but none named access_token", () => {
    const request = requestFor("/dashboard");
    request.cookies.set("session_id", "unrelated-value");
    request.cookies.set("theme", "dark");
    const response = proxy(request);
    expect(response.status).toBe(307);
  });

  it("treats an access_token cookie with an empty string value as still present", () => {
    // .has() checks for the cookie's existence, not its truthiness — an
    // empty value is a real (if useless) cookie, and validity is the
    // backend's job either way, per the presence-only design.
    const response = proxy(requestFor("/dashboard", "access_token="));
    expect(response.headers.get("location")).toBeNull();
  });

  it("preserves the original request's host/port in the redirect Location", () => {
    const request = new NextRequest("http://example.com:4000/dashboard");
    const response = proxy(request);
    expect(response.headers.get("location")).toBe("http://example.com:4000/login");
  });
});

describe("proxy — matcher config", () => {
  it("excludes api, static assets, and the runtime env script from the matcher", () => {
    const [pattern] = config.matcher;
    expect(pattern).toContain("api");
    expect(pattern).toContain("_next/static");
    expect(pattern).toContain("_next/image");
    expect(pattern).toContain("favicon.ico");
    expect(pattern).toContain("env-config.js");
  });
});
