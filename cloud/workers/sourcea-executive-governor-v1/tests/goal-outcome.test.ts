import assert from "node:assert/strict";
import { test } from "node:test";
import { classifyGoalOutcome } from "../src/goal-outcome.ts";

const passingGoal = {
  goal_id: "goal_123",
  status: "PASSED",
  work_packet_terminal: "ACCEPTED_ARTIFACT",
  receipt_id: "receipt_123",
  receipt_hash: "a".repeat(64),
  acceptance_criteria: [
    { id: "artifact_available", required: true },
    { id: "receipt_verified", required: true },
    { id: "optional_polish", required: false },
  ],
  acceptance_results: [
    { id: "artifact_available", status: "PASS" },
    { id: "receipt_verified", status: "PASS" },
    { id: "optional_polish", status: "WAITING" },
  ],
};

test("READY is pending, never accepted or closed", () => {
  const result = classifyGoalOutcome(
    { ...passingGoal, status: "READY", work_packet_terminal: null, receipt_id: null, receipt_hash: null },
    "goal_123",
  );
  assert.equal(result.kind, "PENDING");
});

test("RUNNING and WAITING_FOR_APPROVAL remain pending", () => {
  for (const status of ["RUNNING", "WAITING_FOR_APPROVAL", "WAITING_FOR_EXTERNAL_EVENT", "SLEEPING"]) {
    assert.equal(classifyGoalOutcome({ ...passingGoal, status }, "goal_123").kind, "PENDING");
  }
});

test("PASSED with a valid accepted-artifact terminal and all required predicates passes", () => {
  const result = classifyGoalOutcome(passingGoal, "goal_123");
  assert.equal(result.kind, "ACCEPTED_ARTIFACT");
  if (result.kind === "ACCEPTED_ARTIFACT") {
    assert.equal(result.receipt_id, "receipt_123");
    assert.deepEqual(result.passed_criteria.sort(), ["artifact_available", "receipt_verified"]);
  }
});

test("PASSED without receipt identity or hash is an incident", () => {
  assert.equal(
    classifyGoalOutcome({ ...passingGoal, receipt_hash: null }, "goal_123").kind,
    "INCIDENT",
  );
});

test("PASSED without the accepted-artifact terminal is an incident", () => {
  assert.equal(
    classifyGoalOutcome({ ...passingGoal, work_packet_terminal: null }, "goal_123").kind,
    "INCIDENT",
  );
});

test("PASSED with a required predicate not PASS is an incident", () => {
  const result = classifyGoalOutcome({
    ...passingGoal,
    acceptance_results: [{ id: "artifact_available", status: "PASS" }],
  }, "goal_123");
  assert.equal(result.kind, "INCIDENT");
});

test("PARTIAL_PASS requires a founder decision", () => {
  assert.equal(classifyGoalOutcome({ ...passingGoal, status: "PARTIAL_PASS" }, "goal_123").kind, "FOUNDER_DECISION_REQUIRED");
});

test("Runway terminal failures are bounded failures", () => {
  for (const status of ["FAILED", "BUDGET_EXHAUSTED", "TIME_EXHAUSTED", "CANCELLED"]) {
    assert.equal(classifyGoalOutcome({ ...passingGoal, status }, "goal_123").kind, "BOUNDED_FAILURE");
  }
});

test("a different goal id is rejected", () => {
  const result = classifyGoalOutcome(passingGoal, "goal_other");
  assert.equal(result.kind, "INCIDENT");
  if (result.kind === "INCIDENT") assert.equal(result.reason, "goal_identity_mismatch");
});

test("unknown states stay pending instead of being promoted to success", () => {
  assert.equal(classifyGoalOutcome({ ...passingGoal, status: "FUTURE_STATE" }, "goal_123").kind, "PENDING");
});

test("missing criteria cannot produce a false PASS", () => {
  assert.equal(classifyGoalOutcome({
    ...passingGoal,
    acceptance_criteria: [],
  }, "goal_123").kind, "INCIDENT");
});
