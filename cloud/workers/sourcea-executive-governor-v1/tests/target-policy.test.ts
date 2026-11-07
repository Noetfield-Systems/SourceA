import assert from "node:assert/strict";
import { test } from "node:test";
import { validateExecutiveTargetUrl } from "../src/target-policy.ts";

test("allows exact HTTPS host", () => {
  const result = validateExecutiveTargetUrl("https://sourcea.app/page", "sourcea.app,www.sourcea.app");
  assert.equal(result.ok, true);
  if (result.ok) assert.equal(result.hostname, "sourcea.app");
});

test("blocks an absent allowlist", () => {
  assert.deepEqual(
    validateExecutiveTargetUrl("https://sourcea.app/page", ""),
    { ok: false, reason: "target_allowlist_missing" },
  );
});

test("blocks host suffix tricks and lookalikes", () => {
  assert.equal(validateExecutiveTargetUrl("https://sourcea.app.attacker.test/", "sourcea.app").ok, false);
  assert.equal(validateExecutiveTargetUrl("https://evilsourcea.app/", "sourcea.app").ok, false);
});

test("blocks non-HTTPS URLs and embedded credentials", () => {
  assert.equal(validateExecutiveTargetUrl("http://sourcea.app/", "sourcea.app").ok, false);
  assert.equal(validateExecutiveTargetUrl("https://user:pass@sourcea.app/", "sourcea.app").ok, false);
});

test("blocks nonstandard ports and IP addresses", () => {
  assert.equal(validateExecutiveTargetUrl("https://sourcea.app:8443/", "sourcea.app").ok, false);
  assert.equal(validateExecutiveTargetUrl("https://127.0.0.1/", "sourcea.app").ok, false);
});
