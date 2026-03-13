import { describe, expect, it } from "vitest";

import {
  canDependOn,
  listAllowedDependencies
} from "../../../src/architecture/module-boundaries.js";

describe("module boundaries", () => {
  it("allows the agent runtime to depend on memory, tools and knowledge", () => {
    expect(listAllowedDependencies("agent-runtime")).toEqual([
      "memory-layer",
      "tool-layer",
      "knowledge-system"
    ]);
  });

  it("disallows reverse dependencies into the agent runtime", () => {
    expect(canDependOn("memory-layer", "agent-runtime")).toBe(false);
    expect(canDependOn("tool-layer", "agent-runtime")).toBe(false);
    expect(canDependOn("knowledge-system", "agent-runtime")).toBe(false);
  });
});
