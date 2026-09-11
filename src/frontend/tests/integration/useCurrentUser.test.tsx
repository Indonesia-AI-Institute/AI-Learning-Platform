import { describe, it, expect } from "bun:test";
import { renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { server } from "../mocks/server";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { withQueryClient } from "./testUtils";

const ME_URL = "http://localhost:8000/api/v1/auth/me";

describe("useCurrentUser", () => {
  it("starts loading, then resolves with the user from GET /users/me", async () => {
    const { result } = renderHook(() => useCurrentUser(), { wrapper: withQueryClient() });

    expect(result.current.isLoading).toBe(true);
    expect(result.current.user).toBeUndefined();

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.isError).toBe(false);
    expect(result.current.user).toMatchObject({
      id: "user-1",
      role: "student",
    });
  });

  it("surfaces isError without retrying on a 401 (avoids hammering the API while logged out)", async () => {
    server.use(http.get(ME_URL, () => new HttpResponse(null, { status: 401 })));

    const { result } = renderHook(() => useCurrentUser(), { wrapper: withQueryClient() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.isError).toBe(true);
    expect(result.current.user).toBeUndefined();
  });

  it("reflects a teacher role the same way as a student role", async () => {
    server.use(
      http.get(ME_URL, () =>
        HttpResponse.json({
          id: "user-2",
          email: "teacher@example.com",
          full_name: "Test Teacher",
          role: "teacher",
        })
      )
    );

    const { result } = renderHook(() => useCurrentUser(), { wrapper: withQueryClient() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.user?.role).toBe("teacher");
  });
});
