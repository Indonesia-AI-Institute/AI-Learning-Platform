import { GlobalRegistrator } from "@happy-dom/global-registrator";

// Must be its own preload file, listed before tests/setup.ts in
// bunfig.toml, and must import nothing else. ES imports are hoisted
// above a module's own top-level code, so if @testing-library/react
// were imported from this same file, its transitive import of
// @testing-library/dom would create the `screen` singleton (bound to
// `document` at that moment) before this register() call ever ran,
// leaving `screen` permanently pointed at a nonexistent document.
GlobalRegistrator.register();
