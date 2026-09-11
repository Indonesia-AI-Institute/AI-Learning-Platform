import { afterEach } from "bun:test";
import { cleanup } from "@testing-library/react";
import "@testing-library/jest-dom";

// RTL doesn't auto-cleanup under bun:test the way it does under Jest's
// global afterEach hook, so leftover DOM from one test would otherwise
// leak into the next and produce false "found 2 elements" failures.
afterEach(() => {
  cleanup();
});
