/** ExecutiveRun terminals — never ACTIVE_FOREVER. */

export const RUN_TERMINALS = [
  "ACCEPTED",
  "BOUNDED_FAILURE",
  "INCIDENT",
  "DEFERRED_BY_POLICY",
  "FOUNDER_DECISION_REQUIRED",
] as const;

export type RunTerminal = (typeof RUN_TERMINALS)[number];

export const RUN_TRANSITIONS: Record<string, string[]> = {
  RECEIVED: ["SNAPSHOT_LOCKED", "BOUNDED_FAILURE"],
  SNAPSHOT_LOCKED: ["ROLE_DELIBERATION", "BOUNDED_FAILURE"],
  ROLE_DELIBERATION: ["CONTEXT_READY", "DEFERRED_BY_POLICY", "BOUNDED_FAILURE"],
  CONTEXT_READY: ["COUNCIL_REVIEW", "BOUNDED_FAILURE"],
  COUNCIL_REVIEW: ["GOVERNOR_DECIDED", "BOUNDED_FAILURE", "INCIDENT"],
  GOVERNOR_DECIDED: ["ACTION_COMPILED", "INCIDENT", "FOUNDER_DECISION_REQUIRED"],
  ACTION_COMPILED: ["EXECUTING", "INCIDENT"],
  EXECUTING: ["VERIFYING", "INCIDENT", "BOUNDED_FAILURE"],
  VERIFYING: ["ACCEPTED", "INCIDENT"],
};

export function assertNotActiveForever(status: string): void {
  if (status === "ACTIVE_FOREVER" || status === "ACTIVE") {
    throw new Error("ACTIVE_FOREVER_FORBIDDEN");
  }
  if (!(RUN_TERMINALS as readonly string[]).includes(status) && status.endsWith("_FOREVER")) {
    throw new Error("ACTIVE_FOREVER_FORBIDDEN");
  }
}
