import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import { getApiUrl } from "@/lib/env";

const ORIGINAL_ENV_VAR = process.env.NEXT_PUBLIC_API_URL;

describe("getApiUrl", () => {
  beforeEach(() => {
    delete window.__ENV__;
    delete process.env.NEXT_PUBLIC_API_URL;
  });

  afterEach(() => {
    delete window.__ENV__;
    if (ORIGINAL_ENV_VAR === undefined) {
      delete process.env.NEXT_PUBLIC_API_URL;
    } else {
      process.env.NEXT_PUBLIC_API_URL = ORIGINAL_ENV_VAR;
    }
  });

  it("reads window.__ENV__ first — the value entrypoint.sh injects at container runtime", () => {
    window.__ENV__ = { NEXT_PUBLIC_API_URL: "https://runtime.example.com/api/v1" };
    expect(getApiUrl()).toBe("https://runtime.example.com/api/v1");
  });

  it("prefers window.__ENV__ over process.env when both are set", () => {
    window.__ENV__ = { NEXT_PUBLIC_API_URL: "https://runtime.example.com/api/v1" };
    process.env.NEXT_PUBLIC_API_URL = "https://buildtime.example.com/api/v1";
    expect(getApiUrl()).toBe("https://runtime.example.com/api/v1");
  });

  it("falls back to process.env when window.__ENV__ is absent (server-side rendering)", () => {
    process.env.NEXT_PUBLIC_API_URL = "https://ssr.example.com/api/v1";
    expect(getApiUrl()).toBe("https://ssr.example.com/api/v1");
  });

  it("falls back to process.env when window.__ENV__ exists but has no NEXT_PUBLIC_API_URL", () => {
    window.__ENV__ = {};
    process.env.NEXT_PUBLIC_API_URL = "https://ssr.example.com/api/v1";
    expect(getApiUrl()).toBe("https://ssr.example.com/api/v1");
  });

  it("falls back to process.env when window.__ENV__.NEXT_PUBLIC_API_URL is an empty string", () => {
    // entrypoint.sh's `${NEXT_PUBLIC_API_URL:-}` writes an empty string, not
    // an absent key, when the env var is unset — the `?.` check alone
    // wouldn't catch this; the code also needs the truthiness check.
    window.__ENV__ = { NEXT_PUBLIC_API_URL: "" };
    process.env.NEXT_PUBLIC_API_URL = "https://ssr.example.com/api/v1";
    expect(getApiUrl()).toBe("https://ssr.example.com/api/v1");
  });

  it("falls back to the localhost default when nothing is set at all", () => {
    expect(getApiUrl()).toBe("http://localhost:8000/api/v1");
  });
});
