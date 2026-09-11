import { describe, it, expect, beforeEach, mock } from "bun:test";
import { act, renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { server } from "../mocks/server";
import { withQueryClient } from "./testUtils";

const push = mock<(href: string) => void>();
const refresh = mock<() => void>();

mock.module("next/navigation", () => ({
  useRouter: () => ({ push, refresh }),
}));

const { useAuth } = await import("@/hooks/useAuth");

const LOGIN_URL = "http://localhost:8000/api/v1/auth/login";
const REGISTER_URL = "http://localhost:8000/api/v1/auth/register";

describe("useAuth", () => {
  beforeEach(() => {
    push.mockClear();
    refresh.mockClear();
  });

  it("login: on success, navigates to /dashboard and refreshes", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper: withQueryClient() });

    act(() => {
      result.current.login({ email: "a@example.com", password: "password123" });
    });

    await waitFor(() => expect(result.current.isLoginLoading).toBe(false));

    expect(push).toHaveBeenCalledWith("/dashboard");
    expect(refresh).toHaveBeenCalled();
    expect(result.current.loginError).toBeNull();
  });

  it("login: on failure, exposes the error and does not navigate", async () => {
    server.use(
      http.post(LOGIN_URL, () =>
        HttpResponse.json({ detail: "Invalid credentials" }, { status: 401 })
      )
    );

    const { result } = renderHook(() => useAuth(), { wrapper: withQueryClient() });

    act(() => {
      result.current.login({ email: "a@example.com", password: "wrong" });
    });

    await waitFor(() => expect(result.current.isLoginLoading).toBe(false));

    expect(push).not.toHaveBeenCalled();
    expect(result.current.loginError).toBeTruthy();
  });

  it("register: on success, navigates to /dashboard", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper: withQueryClient() });

    act(() => {
      result.current.register({
        full_name: "New User",
        email: "new@example.com",
        password: "password123",
        role: "student",
      });
    });

    await waitFor(() => expect(result.current.isRegisterLoading).toBe(false));

    expect(push).toHaveBeenCalledWith("/dashboard");
    expect(result.current.registerError).toBeNull();
  });

  it("register: on failure (e.g. duplicate email), exposes the error", async () => {
    server.use(
      http.post(REGISTER_URL, () =>
        HttpResponse.json({ detail: "Email already registered" }, { status: 400 })
      )
    );

    const { result } = renderHook(() => useAuth(), { wrapper: withQueryClient() });

    act(() => {
      result.current.register({
        full_name: "New User",
        email: "dupe@example.com",
        password: "password123",
        role: "student",
      });
    });

    await waitFor(() => expect(result.current.isRegisterLoading).toBe(false));

    expect(push).not.toHaveBeenCalled();
    expect(result.current.registerError).toBeTruthy();
  });

  it("logout: navigates to /login and refreshes on success", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper: withQueryClient() });

    act(() => {
      result.current.logout();
    });

    await waitFor(() => expect(result.current.isLogoutLoading).toBe(false));

    expect(push).toHaveBeenCalledWith("/login");
    expect(refresh).toHaveBeenCalled();
  });
});
