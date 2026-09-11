import { describe, it, expect } from "bun:test";
import { act, renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse, delay } from "msw";
import { server } from "../mocks/server";
import { useChat } from "@/hooks/useChat";
import { withQueryClient } from "./testUtils";

const STREAM_URL = "http://localhost:8000/api/v1/chat/sessions/:sessionId/stream";
const AUTO_END_URL = "http://localhost:8000/api/v1/chat/sessions/:sessionId/auto-end";

function sseStream(chunks: string[]) {
  return new ReadableStream({
    async start(controller) {
      const encoder = new TextEncoder();
      for (const chunk of chunks) {
        controller.enqueue(encoder.encode(`data: ${chunk}\n`));
      }
      controller.enqueue(encoder.encode("data: [DONE]\n"));
      controller.close();
    },
  });
}

describe("useChat — sendMessage streaming", () => {
  it("appends the user message immediately, then streams and finalizes the assistant reply", async () => {
    // Each chunk becomes its own "data: " line, and the hook .trim()s every
    // line individually — a chunk that's pure whitespace (e.g. a lone " ")
    // would have it stripped, so avoid whitespace-only chunks here just
    // like a real token stream would.
    server.use(
      http.post(STREAM_URL, () =>
        new HttpResponse(sseStream(["Hello,", "world", "!"]), {
          headers: { "Content-Type": "text/event-stream" },
        })
      )
    );

    const { result } = renderHook(
      () => useChat({ sessionId: "session-1" }),
      { wrapper: withQueryClient() }
    );

    act(() => {
      result.current.sendMessage("Hi there");
    });

    // User message appears synchronously with the send call.
    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0]).toMatchObject({ role: "user", content: "Hi there" });
    expect(result.current.isStreaming).toBe(true);

    await waitFor(() => expect(result.current.isStreaming).toBe(false));

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[1]).toMatchObject({
      role: "assistant",
      content: "Hello,world!",
    });
    expect(result.current.streamingContent).toBe("");
    expect(result.current.error).toBeNull();
  });

  it("ignores empty or whitespace-only input", async () => {
    const { result } = renderHook(
      () => useChat({ sessionId: "session-1" }),
      { wrapper: withQueryClient() }
    );

    act(() => {
      result.current.sendMessage("   ");
    });

    expect(result.current.messages).toHaveLength(0);
    expect(result.current.isStreaming).toBe(false);
  });

  it("ignores a second send while already streaming", async () => {
    server.use(
      http.post(STREAM_URL, async () => {
        await delay(50);
        return new HttpResponse(sseStream(["done"]), {
          headers: { "Content-Type": "text/event-stream" },
        });
      })
    );

    const { result } = renderHook(
      () => useChat({ sessionId: "session-1" }),
      { wrapper: withQueryClient() }
    );

    act(() => {
      result.current.sendMessage("first");
    });
    act(() => {
      result.current.sendMessage("second");
    });

    // Only the first user message should have been appended — the guard
    // at the top of sendMessage bails out while isStreaming is already true.
    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0].content).toBe("first");

    await waitFor(() => expect(result.current.isStreaming).toBe(false));
  });

  it("sets a generic error and stops streaming when the response is not ok", async () => {
    server.use(http.post(STREAM_URL, () => new HttpResponse(null, { status: 500 })));

    const { result } = renderHook(
      () => useChat({ sessionId: "session-1" }),
      { wrapper: withQueryClient() }
    );

    act(() => {
      result.current.sendMessage("Hi");
    });

    await waitFor(() => expect(result.current.isStreaming).toBe(false));

    expect(result.current.error).toBe("Failed to send message. Please try again.");
  });

  it("stopStream aborts the in-flight request without setting an error", async () => {
    server.use(
      http.post(STREAM_URL, async () => {
        await delay(200);
        return new HttpResponse(sseStream(["late"]), {
          headers: { "Content-Type": "text/event-stream" },
        });
      })
    );

    const { result } = renderHook(
      () => useChat({ sessionId: "session-1" }),
      { wrapper: withQueryClient() }
    );

    act(() => {
      result.current.sendMessage("Hi");
    });
    expect(result.current.isStreaming).toBe(true);

    act(() => {
      result.current.stopStream();
    });

    expect(result.current.isStreaming).toBe(false);
    expect(result.current.streamingContent).toBe("");
    expect(result.current.error).toBeNull();
  });
});

describe("useChat — resetMessages", () => {
  it("replaces the message list wholesale (used to sync in fetched history)", () => {
    const { result } = renderHook(
      () => useChat({ sessionId: "session-1" }),
      { wrapper: withQueryClient() }
    );

    act(() => {
      result.current.resetMessages([
        { role: "user", content: "old", created_at: new Date().toISOString() },
      ]);
    });

    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0].content).toBe("old");
  });
});

describe("useChat — auto-end on unmount", () => {
  it("fires auto-end when unmounting an active session", async () => {
    let autoEndCalled = false;
    server.use(
      http.post(AUTO_END_URL, () => {
        autoEndCalled = true;
        return new HttpResponse(null, { status: 204 });
      })
    );

    const { unmount } = renderHook(
      () => useChat({ sessionId: "session-1", isSessionActive: true }),
      { wrapper: withQueryClient() }
    );

    unmount();

    await waitFor(() => expect(autoEndCalled).toBe(true));
  });

  it("does not fire auto-end when the session was already inactive", async () => {
    let autoEndCalled = false;
    server.use(
      http.post(AUTO_END_URL, () => {
        autoEndCalled = true;
        return new HttpResponse(null, { status: 204 });
      })
    );

    const { unmount } = renderHook(
      () => useChat({ sessionId: "session-1", isSessionActive: false }),
      { wrapper: withQueryClient() }
    );

    unmount();

    // Give any accidental fetch a moment to land before asserting it didn't.
    await new Promise((r) => setTimeout(r, 50));
    expect(autoEndCalled).toBe(false);
  });
});
