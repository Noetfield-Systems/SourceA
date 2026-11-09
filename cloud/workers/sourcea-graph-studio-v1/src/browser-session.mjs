/**
 * Graph Studio browser BFF — one existing Worker, no browser workload secrets.
 *
 * A Cloudflare Access JWT proves the human's session. It is NOT an ActionPermit.
 * Only read/compile operations may reach the existing Graph Studio DO.
 * Publish and Run stay blocked until a separate scoped Governor permit exists.
 */
const encoder = new TextEncoder();
const SESSION_PREFIX = "/api/studio/";
const MAX_JWT_BYTES = 8192;
const MAX_POST_BYTES = 65536;
const MAX_JWKS_BYTES = 32768;
const JWKS_CACHE_MS = 180000;
const jwksCache = new Map();

function failure(status, reason) {
  return { ok: false, status, reason };
}

function decodedB64Url(value, maxBytes) {
  if (typeof value !== "string" || !/^[A-Za-z0-9_-]+$/.test(value) ||
      value.length > Math.ceil(maxBytes * 4 / 3) + 5) {
    throw new Error("encoding_invalid");
  }
  const b64 = value.replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(b64 + "=".repeat((4 - b64.length % 4) % 4));
  if (raw.length > maxBytes) throw new Error("payload_oversized");
  return Uint8Array.from(raw, char => char.charCodeAt(0));
}

function jsonPart(encoded, maxBytes) {
  return JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(
    decodedB64Url(encoded, maxBytes),
  ));
}

function jwtFromRequest(request) {
  const assertion = request.headers.get("Cf-Access-Jwt-Assertion") || "";
  const cookie = request.headers.get("Cookie") || "";
  const matches = [...cookie.matchAll(/(?:^|;\s*)CF_Authorization=([^;]+)/g)];
  if (matches.length > 1) return null;
  const cookieJwt = matches.length ? matches[0][1] : "";
  if (assertion && cookieJwt && assertion !== cookieJwt) return null;
  return assertion || cookieJwt || null;
}

function configured(env) {
  const team = env.SOURCEA_ACCESS_TEAM_DOMAIN || "";
  const aud = env.SOURCEA_GRAPH_ACCESS_AUD || "";
  const allow = env.SOURCEA_GRAPH_ACCESS_ALLOWED_EMAILS || "";
  if (!/^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.cloudflareaccess\.com$/.test(team) ||
      !/^[A-Za-z0-9_-]{20,128}$/.test(aud) || !allow.trim() || allow.length > 3000) {
    return null;
  }
  const emails = allow.split(",").map(s => s.trim());
  if (emails.length > 25 || emails.some(s =>
      !/^[A-Za-z0-9.!#$%&'*+\/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(s) ||
      s !== s.toLowerCase()) || new Set(emails).size !== emails.length) return null;
  return { team, aud, emails, issuer: `https://${team}` };
}

async function keysFor(team, fetchImpl, nowMs, useCache) {
  const cached = jwksCache.get(team);
  if (useCache && cached && cached.expires > nowMs) return cached.keys;
  const url = `https://${team}/cdn-cgi/access/certs`;
  const response = await fetchImpl(url, {
    method: "GET", redirect: "error", headers: { accept: "application/json" },
    signal: AbortSignal.timeout(5000),
  });
  if (!response.ok || response.status !== 200) throw new Error("jwks_http_error");
  const raw = await response.text();
  if (raw.length > MAX_JWKS_BYTES) throw new Error("jwks_oversized");
  const data = JSON.parse(raw);
  if (!Array.isArray(data.keys) || data.keys.length < 1 || data.keys.length > 20) {
    throw new Error("jwks_invalid");
  }
  const keys = data.keys.filter(key =>
    key && key.kty === "RSA" && (key.alg === "RS256" || !key.alg) &&
    typeof key.kid === "string" && key.kid.length <= 128 &&
    typeof key.n === "string" && typeof key.e === "string");
  if (!keys.length) throw new Error("jwks_no_rsa_key");
  if (useCache) jwksCache.set(team, { keys, expires: nowMs + JWKS_CACHE_MS });
  return keys;
}

/**
 * Cryptographically verify Access JWT using pinned issuer, application AUD,
 * explicit email allowlist and current time. No Access config means deny.
 * fetchImpl is injectable only for offline regression tests.
 */
export async function authorizeGraphBrowserSession(request, env, options = {}) {
  const cfg = configured(env);
  if (!cfg) return failure(503, "browser_access_not_commissioned");
  const token = jwtFromRequest(request);
  if (!token || token.length > MAX_JWT_BYTES) return failure(401, "access_session_required");
  const parts = token.split(".");
  if (parts.length !== 3) return failure(401, "access_jwt_invalid");
  const now = options.nowSeconds ?? Math.floor(Date.now() / 1000);
  let header, payload, signature;
  try {
    header = jsonPart(parts[0], 1500);
    payload = jsonPart(parts[1], 3500);
    signature = decodedB64Url(parts[2], 1024);
  } catch {
    return failure(401, "access_jwt_invalid");
  }
  if (!header || typeof header !== "object" || header.alg !== "RS256" ||
      typeof header.kid !== "string" || header.kid.length > 128 ||
      !payload || typeof payload !== "object" ||
      payload.iss !== cfg.issuer ||
      !((Array.isArray(payload.aud) && payload.aud.includes(cfg.aud)) ||
        payload.aud === cfg.aud) ||
      !Number.isSafeInteger(payload.exp) || payload.exp <= now ||
      !Number.isSafeInteger(payload.iat) || payload.iat > now + 60 ||
      (payload.nbf !== undefined &&
        (!Number.isSafeInteger(payload.nbf) || payload.nbf > now + 60)) ||
      typeof payload.sub !== "string" || !payload.sub ||
      typeof payload.email !== "string" || !cfg.emails.includes(payload.email.toLowerCase())) {
    return failure(403, "access_claims_denied");
  }
  try {
    const keyset = await keysFor(cfg.team, options.fetchImpl || fetch, now * 1000,
      options.cache !== false);
    const jwk = keyset.find(k => k.kid === header.kid);
    if (!jwk) return failure(403, "access_signing_key_unknown");
    const key = await crypto.subtle.importKey(
      "jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"],
    );
    const passed = await crypto.subtle.verify(
      "RSASSA-PKCS1-v1_5", key, signature, encoder.encode(parts[0] + "." + parts[1]),
    );
    if (!passed) return failure(403, "access_signature_invalid");
  } catch {
    return failure(503, "access_verifier_unavailable");
  }
  return { ok: true, subject: payload.sub };
}

/** Browser API is a read-only BFF: it cannot mint or imply a governor permit. */
export function mapGraphBrowserRoute(request) {
  const url = new URL(request.url);
  const path = url.pathname;
  if (!path.startsWith(SESSION_PREFIX)) return failure(404, "not_found");
  if (url.search) return failure(403, "browser_query_not_supported");
  const routes = {
    "GET /api/studio/registry": "/v1/registry",
    "GET /api/studio/blueprints/golden": "/v1/blueprints/golden",
    "POST /api/studio/blueprints/validate": "/v1/blueprints/validate",
  };
  const mapped = routes[request.method + " " + path];
  if (mapped) return { ok: true, mapped };
  if (/^GET \/api\/studio\/runs\/grun_[A-Za-z0-9_-]{1,120}$/.test(request.method + " " + path)) {
    return { ok: true, mapped: path.replace(SESSION_PREFIX, "/v1/") };
  }
  if (/^POST \/api\/studio\/(?:blueprints\/publish|runs)$/.test(request.method + " " + path)) {
    return failure(403, "independent_governor_permit_required");
  }
  return failure(404, "browser_route_not_found");
}

export async function browserRequestAllowed(request, route) {
  if (!route.ok) return route;
  const url = new URL(request.url);
  if (request.method === "POST") {
    const origin = request.headers.get("Origin");
    if (origin !== url.origin || request.headers.get("X-SourceA-Studio-Request") !== "1" ||
        (request.headers.get("Sec-Fetch-Site") &&
         request.headers.get("Sec-Fetch-Site") !== "same-origin") ||
        !/^application\/json(?:\s*;|$)/i.test(request.headers.get("content-type") || "")) {
      return failure(403, "browser_csrf_denied");
    }
    const raw = new Uint8Array(await request.clone().arrayBuffer());
    if (raw.length > MAX_POST_BYTES) return failure(413, "browser_body_oversized");
    try {
      if (!JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(raw))) {
        return failure(400, "browser_json_invalid");
      }
    } catch {
      return failure(400, "browser_json_invalid");
    }
  } else if (request.method !== "GET") {
    return failure(405, "method_denied");
  }
  return { ok: true, mapped: route.mapped };
}
