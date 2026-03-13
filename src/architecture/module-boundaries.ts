export const systemModules = [
  "agent-runtime",
  "memory-layer",
  "tool-layer",
  "knowledge-system"
] as const;

export type SystemModule = (typeof systemModules)[number];

const allowedDependencies: Record<SystemModule, readonly SystemModule[]> = {
  "agent-runtime": ["memory-layer", "tool-layer", "knowledge-system"],
  "memory-layer": [],
  "tool-layer": [],
  "knowledge-system": []
};

export function listAllowedDependencies(
  moduleName: SystemModule
): readonly SystemModule[] {
  return allowedDependencies[moduleName];
}

export function canDependOn(
  source: SystemModule,
  target: SystemModule
): boolean {
  return allowedDependencies[source].includes(target);
}
