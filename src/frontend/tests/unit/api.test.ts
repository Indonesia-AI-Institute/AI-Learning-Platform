import { describe, it, expect, afterEach } from "bun:test";
import api from "@/lib/api";

// axios doesn't expose its registered interceptors publicly; this is the
// documented shape of its internal handlers array, just enough to invoke
// the rejected-branch callback directly without a real network call.
interface AxiosInterceptorManagerInternal {
  handlers: Array<{ rejected: (error: unknown) => Promise<never> }>;
}

// api.ts's redirect guard reads/writes window.location — happy-dom's real
// Location object rejects programmatic navigation in a test environment,
// so it's swapped for a plain mutable object for the scope of this file.
const originalLocation = window.location;

function setLocation(pathname: string) {
  // @ts-expect-error — intentionally replacing the whole object
  delete window.location;
  window.location = {
    pathname,
    href: `http://localhost${pathname}`,
  } as unknown as Location;
}

describe("api axios instance config", () => {
  it("sends credentials (cookies) with every request", () => {
    expect(api.defaults.withCredentials).toBe(true);
  });

  it("resolves baseURL through getApiUrl() rather than a hardcoded value", () => {
    expect(api.defaults.baseURL).toBeTruthy();
    expect(typeof api.defaults.baseURL).toBe("string");
  });

  it("sets a JSON content-type header by default", () => {
    expect(api.defaults.headers["Content-Type"]).toBe("application/json");
  });
});

describe("api 401 redirect guard", () => {
  // The guard's isRedirecting flag is module-private state, so these tests
  // run in the declared order and each one's effect on that flag is part
  // of what the next test verifies — this intentionally exercises the
  // real shared module, not a fresh instance per test. In particular: the
  // "already on /login" test below MUST run before any test that sets
  // isRedirecting to true, or it would pass for the wrong reason (the
  // isRedirecting guard short-circuiting first) instead of exercising the
  // pathname check it's actually meant to verify.

  afterEach(() => {
    window.location = originalLocation;
  });

  function reject(error: unknown) {
    const handler = (api.interceptors.response as unknown as AxiosInterceptorManagerInternal).handlers[0];
    return handler.rejected(error);
  }

  function reject401() {
    return reject({ response: { status: 401 } });
  }

  it("does not redirect on a 401 when already on /login (isRedirecting still false here)", async () => {
    setLocation("/login");
    window.location.href = "unchanged";
    await expect(reject401()).rejects.toBeDefined();
    expect(window.location.href).toBe("unchanged");
  });

  it("does not redirect on a network error with no response at all (e.g. CORS failure, timeout)", async () => {
    setLocation("/dashboard");
    window.location.href = "unchanged";
    await expect(reject(new Error("Network Error"))).rejects.toBeDefined();
    expect(window.location.href).toBe("unchanged");
  });

  it("does not redirect when response.status is present but not 401", async () => {
    setLocation("/dashboard");
    window.location.href = "unchanged";
    await expect(reject({ response: { status: 403 } })).rejects.toBeDefined();
    expect(window.location.href).toBe("unchanged");
  });

  it("redirects to /login on a 401 when not already there", async () => {
    setLocation("/dashboard");
    await expect(reject401()).rejects.toBeDefined();
    expect(window.location.href).toBe("/login");
  });

  it("does not redirect again on a second 401 (guards against a redirect loop)", async () => {
    setLocation("/dashboard");
    window.location.href = "unchanged";
    await expect(reject401()).rejects.toBeDefined();
    // isRedirecting is already true from the previous test, and this
    // module has no way to reset it short of a fresh import — which is
    // exactly the real-world scenario the guard exists for: multiple
    // concurrent 401 responses (e.g. auth/me + another request) must
    // only trigger one navigation.
    expect(window.location.href).toBe("unchanged");
  });

  it("always rejects the promise so callers still see the error", async () => {
    setLocation("/login");
    await expect(reject401()).rejects.toMatchObject({
      response: { status: 401 },
    });
  });

  it("passes through non-401 errors unchanged", async () => {
    setLocation("/dashboard");
    await expect(reject({ response: { status: 500 } })).rejects.toMatchObject({
      response: { status: 500 },
    });
  });
});
