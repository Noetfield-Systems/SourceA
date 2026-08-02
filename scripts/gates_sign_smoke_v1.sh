#!/usr/bin/env bash
# Local gates signing smoke (no deploy required for crypto path).
set -euo pipefail
export SECRET
SECRET=$(openssl rand -hex 24)
node --input-type=module <<'NODE'
const secret = process.env.SECRET;
async function hmacHex(secret, body) {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
const packet = {
  v: 1,
  gate_id: "gate_test",
  action: "APPROVE",
  lane: "AMBER",
  exp: Math.floor(Date.now() / 1000) + 900,
  nonce: crypto.randomUUID(),
  idempotency_key: "idem_test",
};
const payload = JSON.stringify(packet);
const sig = await hmacHex(secret, payload);
const token = Buffer.from(JSON.stringify({ packet, sig })).toString("base64");
const parsed = JSON.parse(Buffer.from(token, "base64").toString("utf8"));
const expect = await hmacHex(secret, JSON.stringify(parsed.packet));
if (expect !== parsed.sig) throw new Error("sig mismatch");
if (parsed.packet.lane !== "AMBER") throw new Error("lane");
console.log(JSON.stringify({ ok: true, schema: "gates_sign_smoke_v1", gate_id: packet.gate_id }));
NODE
