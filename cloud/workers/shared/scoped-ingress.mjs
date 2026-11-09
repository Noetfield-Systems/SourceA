/**
 * SourceA ingress v1 — signed short-lived service identity, exact method, path,
 * tenant and body binding. A signed identity is NOT a Governor action permit.
 *
 * Caller signing keys live only in workload-secret stores. No browser receives one.
 * Requests fail closed until every intended caller and upstream is provisioned.
 */
const ENCODER = new TextEncoder();
const MAX_BODY_BYTES = 64 * 1024;
const MAX_TTL_MS = 90_000;
const SKEW_MS = 15_000;
const SIGNING_KEYS = Object.freeze({
  "graph-studio": "SOURCEA_GRAPH_CALLER_KEY",
  "n8n": "SOURCEA_N8N_CALLER_KEY",
  "founder-os": "SOURCEA_FOUNDER_CALLER_KEY",
});
const ALLOWED = Object.freeze({
  governor: Object.freeze({
    "POST /v1/executive/runs": "governor.run.create",
    "GET /v1/executive/runs/": "governor.run.read",
  }),
  graph: Object.freeze({
    "GET /v1/registry": "graph.registry.read",
    "GET /v1/blueprints/golden": "graph.blueprint.read",
    "POST /v1/blueprints/validate": "graph.blueprint.validate",
    "POST /v1/blueprints/publish": "graph.blueprint.publish",
    "POST /v1/runs": "graph.run.create",
    "GET /v1/runs/": "graph.run.read",
  }),
});

const error = (status, reason) => ({ ok: false, status, reason });

function keyName(caller) {
  return Object.prototype.hasOwnProperty.call(SIGNING_KEYS, caller)
    ? SIGNING_KEYS[caller] : null;
}

function scopeFor(audience, method, path) {
  const policies = ALLOWED[audience];
  if (!policies) return null;
  const exact = policies[method + " " + path];
  if (exact) return exact;
  if (method === "GET") {
    for (const [key, scope] of Object.entries(policies)) {
      if (key.endsWith("/") && (method + " " + path).startsWith(key) &&
          path.length > key.slice(method.length + 1).length) {
        return scope;
      }
    }
  }
  return null;
}

function toB64url(bytes) {
  let encoded = "";
  for (const b of bytes) encoded += String.fromCharCode(b);
  return btoa(encoded).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromB64url(input) {
  if (typeof input !== "string" || !/^[A-Za-z0-9_-]{30,1500}$/.test(input)) {
    throw new Error("invalid_claims_encoding");
  }
  const base = input.replace(/-/g, "+").replace(/_/g, "/");
  const binary = atob(base + "=".repeat((4 - base.length % 4) % 4));
  return Uint8Array.from(binary, c => c.charCodeAt(0));
}

async function digestBytes(bytes) {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map(c => c.toString(16).padStart(2, "0")).join("");
}

async function signer(secret, ops) {
  return crypto.subtle.importKey(
    "raw", ENCODER.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ops,
  );
}

async function bodyDigest(request) {
  const raw = new Uint8Array(await request.clone().arrayBuffer());
  if (raw.byteLength > MAX_BODY_BYTES) throw new Error("body_too_large");
  return digestBytes(raw);
}

function claimFieldsAreExact(claims) {
  if (!claims || typeof claims !== "object" || Array.isArray(claims)) return false;
  const expected = [
    "schema", "aud", "caller", "org", "scope", "method", "path",
    "body_sha256", "issued_at_ms", "expires_at_ms", "nonce",
  ].sort();
  return JSON.stringify(Object.keys(claims).sort()) === JSON.stringify(expected);
}

export async function authorizeScopedIngress(request, env, audience, now = Date.now()) {
  const url = new URL(request.url);
  const scope = scopeFor(audience, request.method, url.pathname);
  if (!scope) return error(404, "scope_not_supported");
  const rawClaims = request.headers.get("X-SourceA-Claims");
  const rawSignature = request.headers.get("X-SourceA-Signature");
  if (!rawClaims || !rawSignature) return error(401, "service_signature_required");
  if (!/^[A-Za-z0-9_-]{40,90}$/.test(rawSignature)) return error(401, "signature_format_invalid");
  let claims;
  try {
    claims = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(fromB64url(rawClaims)));
  } catch {
    return error(401, "claims_invalid");
  }
  if (!claimFieldsAreExact(claims) || claims.schema !== "sourcea.signed-workload.v1" ||
      claims.aud !== audience || claims.scope !== scope ||
      claims.method !== request.method || claims.path !== url.pathname ||
      !/^[a-z0-9][a-z0-9_-]{1,62}$/.test(claims.org) ||
      claims.org !== (url.searchParams.get("org") || "sourcea") ||
      !/^[A-Za-z0-9_-]{16,96}$/.test(claims.nonce) ||
      !/^[a-f0-9]{64}$/.test(claims.body_sha256) ||
      !Number.isSafeInteger(claims.issued_at_ms) ||
      !Number.isSafeInteger(claims.expires_at_ms) ||
      claims.issued_at_ms > now + SKEW_MS ||
      claims.expires_at_ms <= now ||
      claims.expires_at_ms - claims.issued_at_ms > MAX_TTL_MS ||
      claims.expires_at_ms <= claims.issued_at_ms) {
    return error(403, "identity_scope_or_freshness_invalid");
  }
  const keyVar = keyName(claims.caller);
  if (!keyVar) return error(403, "caller_untrusted");
  if (audience === "governor" && claims.caller === "graph-studio" &&
      !["governor.run.create", "governor.run.read"].includes(scope)) {
    return error(403, "caller_scope_denied");
  }
  if (audience === "graph" && claims.caller === "graph-studio") {
    return error(403, "graph_self_call_denied");
  }
  const key = env[keyVar];
  if (typeof key !== "string" || key.length < 48) return error(503, "service_identity_unconfigured");
  try {
    if (claims.body_sha256 !== await bodyDigest(request)) return error(403, "body_binding_mismatch");
    const cryptoKey = await signer(key, ["verify"]);
    if (!await crypto.subtle.verify(
      "HMAC", cryptoKey, fromB64url(rawSignature), ENCODER.encode(rawClaims)
    )) return error(403, "signature_invalid");
  } catch {
    return error(403, "signature_or_body_invalid");
  }
  return { ok: true, claims };
}

/** For trusted Cloudflare service-binding callers only. Never expose this in UI. */
export async function signServiceRequest(method, url, body, { audience, caller, org = "sourcea", secret, nonce }) {
  if (typeof secret !== "string" || secret.length < 48) throw new Error("missing_workload_secret");
  const parsed = new URL(url);
  const scope = scopeFor(audience, method, parsed.pathname);
  if (!scope) throw new Error("scope_not_supported");
  const now = Date.now();
  const bodyBytes = ENCODER.encode(body || "");
  if (bodyBytes.byteLength > MAX_BODY_BYTES) throw new Error("body_too_large");
  const claims = {
    schema: "sourcea.signed-workload.v1", aud: audience, caller, org,
    scope, method, path: parsed.pathname,
    body_sha256: await digestBytes(bodyBytes),
    issued_at_ms: now, expires_at_ms: now + 60_000,
    nonce: nonce || crypto.randomUUID().replace(/-/g, ""),
  };
  const encoded = toB64url(ENCODER.encode(JSON.stringify(claims)));
  const signature = new Uint8Array(await crypto.subtle.sign(
    "HMAC", await signer(secret, ["sign"]), ENCODER.encode(encoded),
  ));
  return {
    "X-SourceA-Claims": encoded,
    "X-SourceA-Signature": toB64url(signature),
  };
}
