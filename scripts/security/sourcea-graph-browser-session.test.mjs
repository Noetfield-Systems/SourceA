import test from "node:test";
import assert from "node:assert/strict";
import {
  authorizeGraphBrowserSession, mapGraphBrowserRoute, browserRequestAllowed,
} from "../../cloud/workers/sourcea-graph-studio-v1/src/browser-session.mjs";

const origin = "https://sourcea-graph-studio-v1.example.com";
const now = Math.floor(Date.now() / 1000);
const env = {
  SOURCEA_ACCESS_TEAM_DOMAIN: "sourcea-operators.cloudflareaccess.com",
  SOURCEA_GRAPH_ACCESS_AUD: "1234567890abcdef1234567890abcdef",
  SOURCEA_GRAPH_ACCESS_ALLOWED_EMAILS: "operator@example.com",
};
const bytes = new TextEncoder();
const b64 = data => Buffer.from(data).toString("base64url");

const keys = await crypto.subtle.generateKey({
  name: "RSASSA-PKCS1-v1_5", modulusLength: 2048,
  publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256",
}, true, ["sign", "verify"]);
const publicJwk = { ...await crypto.subtle.exportKey("jwk", keys.publicKey), kid: "test-rsa-kid", alg: "RS256" };

function payload(override = {}) {
  return {
    iss: "https://" + env.SOURCEA_ACCESS_TEAM_DOMAIN,
    aud: [env.SOURCEA_GRAPH_ACCESS_AUD],
    email: "operator@example.com", sub: "access-sub-100",
    iat: now - 30, exp: now + 3600, ...override,
  };
}

async function token(claims = payload(), overrideHeader = {}) {
  const head = b64(JSON.stringify({ typ: "JWT", alg: "RS256", kid: publicJwk.kid, ...overrideHeader }));
  const body = b64(JSON.stringify(claims));
  const signature = await crypto.subtle.sign(
    "RSASSA-PKCS1-v1_5", keys.privateKey, bytes.encode(head + "." + body),
  );
  return head + "." + body + "." + b64(signature);
}

function sessionReq(jwt, path = "/api/studio/registry", opts = {}) {
  return new Request(origin + path, {
    ...opts,
    headers: { Cookie: "CF_Authorization=" + jwt, ...(opts.headers || {}) },
  });
}

let fetchCalls = 0;
const fetchImpl = async (url, options) => {
  fetchCalls++;
  assert.equal(url, "https://sourcea-operators.cloudflareaccess.com/cdn-cgi/access/certs");
  assert.equal(options.redirect, "error");
  return new Response(JSON.stringify({ keys: [publicJwk] }), {
    status: 200, headers: { "content-type": "application/json" },
  });
};

test("pinned Cloudflare Access session enables read-only BFF without service key", async () => {
  const jwt = await token();
  const decision = await authorizeGraphBrowserSession(sessionReq(jwt), env, {
    fetchImpl, nowSeconds: now, cache: false,
  });
  assert.equal(decision.ok, true);
  assert.equal(decision.subject, "access-sub-100");
  assert.equal(mapGraphBrowserRoute(sessionReq(jwt)).mapped, "/v1/registry");
  assert.equal(mapGraphBrowserRoute(sessionReq(jwt, "/api/studio/blueprints/golden")).mapped,
    "/v1/blueprints/golden");
  assert.equal(mapGraphBrowserRoute(sessionReq(jwt, "/api/studio/runs/grun_safe-id")).mapped,
    "/v1/runs/grun_safe-id");
});

test("unsigned, unconfigured, expired, wrong issuer/audience/email and wrong key deny", async () => {
  const fake = new Request(origin + "/api/studio/registry");
  assert.equal((await authorizeGraphBrowserSession(fake, env)).status, 401);
  assert.equal((await authorizeGraphBrowserSession(fake, {}, { fetchImpl })).status, 503);
  for (const bad of [
    { exp: now - 1 },
    { iss: "https://evil.cloudflareaccess.com" },
    { aud: ["unknown-aud"] },
    { email: "outsider@example.com" },
    { iat: now + 900 },
  ]) {
    const response = await authorizeGraphBrowserSession(
      sessionReq(await token(payload(bad))), env, { fetchImpl, nowSeconds: now, cache: false },
    );
    assert.equal(response.status, 403);
  }
  const kid = await token(payload(), {kid:"unknown-key"});
  assert.equal((await authorizeGraphBrowserSession(sessionReq(kid), env,
    {fetchImpl, nowSeconds: now, cache:false})).status,403);
});

test("cryptographic tampering, duplicate cookie, mismatched assertion and network outage deny", async () => {
  const jwt = await token();
  const bad = jwt.slice(0, -3) + "aaa";
  assert.equal((await authorizeGraphBrowserSession(sessionReq(bad), env,
    { fetchImpl, nowSeconds: now, cache:false })).reason, "access_signature_invalid");
  const req = sessionReq(jwt, "/api/studio/registry", {
    headers: {"Cf-Access-Jwt-Assertion": jwt + ".invalid"},
  });
  assert.equal((await authorizeGraphBrowserSession(req, env)).status,401);
  const repeated = sessionReq(jwt, "/api/studio/registry", {
    headers: {Cookie: "CF_Authorization=" + jwt + "; CF_Authorization=" + jwt},
  });
  assert.equal((await authorizeGraphBrowserSession(repeated, env)).status,401);
  assert.equal((await authorizeGraphBrowserSession(sessionReq(jwt), env, {
    fetchImpl:async () => {throw new Error("network unavailable")},
    nowSeconds:now,cache:false,
  })).status,503);
});

test("body-bound browser validation needs same-origin + JSON + anti-CSRF header", async () => {
  const path = "/api/studio/blueprints/validate";
  const json = JSON.stringify({graph:{blueprint_id:"golden"}});
  const req = (headers = {}, body = json) => new Request(origin+path, {
    method:"POST",body,headers:{
      "Origin":origin,"content-type":"application/json",
      "X-SourceA-Studio-Request":"1", ...headers,
    },
  });
  const valid = await browserRequestAllowed(req(), mapGraphBrowserRoute(req()));
  assert.equal(valid.ok,true);
  assert.equal(valid.mapped,"/v1/blueprints/validate");
  for (const headers of [
    {Origin:"https://evil.example.com"},
    {"X-SourceA-Studio-Request":"0"},
    {"Sec-Fetch-Site":"cross-site"},
    {"content-type":"text/plain"},
  ]) {
    const r=req(headers);
    assert.equal((await browserRequestAllowed(r,mapGraphBrowserRoute(r))).status,403);
  }
  const badJson=req({}, "not-json");
  assert.equal((await browserRequestAllowed(badJson,mapGraphBrowserRoute(badJson))).status,400);
  const oversized=req({},JSON.stringify({x:"a".repeat(65536)}));
  assert.equal((await browserRequestAllowed(oversized,mapGraphBrowserRoute(oversized))).status,413);
});

test("a browser session cannot publish/run or route to Governor even with valid Access JWT", async () => {
  for(const path of ["/api/studio/blueprints/publish","/api/studio/runs"]){
    const r=new Request(origin+path,{method:"POST",body:"{}"});
    assert.equal(mapGraphBrowserRoute(r).reason,"independent_governor_permit_required");
  }
  const wrong=new Request(origin+"/api/studio/../../v1/executive/runs",{method:"POST",body:"{}"});
  assert.equal(mapGraphBrowserRoute(wrong).ok,false);
  const query=new Request(origin+"/api/studio/registry?org=elsewhere");
  assert.equal(mapGraphBrowserRoute(query).status,403);
  const deleteRequest=new Request(origin+"/api/studio/blueprints/validate",{method:"DELETE"});
  assert.equal(mapGraphBrowserRoute(deleteRequest).ok,false);
  assert.ok(fetchCalls > 0);
});
