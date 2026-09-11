import { beforeAll, afterEach, afterAll } from "bun:test";
import { server } from "./mocks/server";

// Global — registered once for the whole test run via bunfig.toml's
// preload, not per test file. Each integration test file previously did
// its own beforeAll(listen)/afterAll(close) on this same shared server
// singleton; running the full suite (as opposed to one file at a time)
// interleaved those lifecycles — one file's afterAll could close the
// server out from under another file's still-running tests, producing
// ECONNREFUSED failures that never showed up running a file in isolation.
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
