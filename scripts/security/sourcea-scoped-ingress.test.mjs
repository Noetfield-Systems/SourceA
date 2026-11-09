import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import {
  authorizeScopedIngress,
  signServiceRequest,
} from "../../cloud/workers/shared/scoped-ingress.mjs";

const require = createRequire(import.meta.url);
const { callGovernor } = require("../../packages/n8n-nodes-sourcea/src/shared.cjs");

const GRAPH_SECRET = "g".repeat(64);
const N8N_SECRET = "n".repeat(64);
const env = {
  SOURCEA_GRAPH_CALLER_KEY: GRAPH_SECRET,
  SOURCEA_N8N_CALLER_KEY: N8N_SECRET,
  SOURCEA_FOUNDER_CALLER_KEY: "f".repeat(64),
  SOURCEA_GRAPH_ALLOWED_ORGS: "sourcea",
  SOURCEA_N8N_ALLOWED_ORGS: "sourcea",
  SOURCEA_FOUNDER_ALLOWED_ORGS: "sourcea",
};
const url = "https://executive-mesh/v1/executive/runs?org=sourcea";
const body = JSON.stringify({
  event_id: "evt_real_audited_001",
  event_type: "webpage.repair.requested",
  idempotency_key: "idem_audited_001",
  payload: { task_type: "webpage_repair", target_url: "https://example.com/" },
});

async function signed(method = "POST", bodyText = body, address = url, caller = "graph-studio", token = GRAPH_SECRET) {
  const headers = await signServiceRequest(method, address, bodyText, {
    audience: "governor",
    caller,
    org: "sourcea",
    secret: token,
  });
  return new Request(address, { method, headers, ...method === "POST" ? { body: bodyText } : {} });
}

test("signed internal Graph Studio call is verified for its exact action", async () => {
  const request = await signed();
  const res = await authorizeScopedIngress(request, env, "governor");
  assert.equal(res.ok, true);
  assert.equal(res.claims.scope, "governor.run.create");
  assert.equal(res.claims.aud, "governor");
  assert.equal(res.claims.org, "sourcea");
  assert.ok(res.claims.expires_at_ms > Date.now());
});

test("unsigned, wrong signature, wrong body, wrong tenant and wrong audience fail closed", async () => {
  assert.equal((await authorizeScopedIngress(new Request(url,{method:"POST",body}),env,"governor")).status,401);
  const good=await signed();
  const wrongHeaders=new Headers(good.headers);
  wrongHeaders.set("X-SourceA-Signature","a".repeat(43));
  assert.equal((await authorizeScopedIngress(new Request(url,{method:"POST",headers:wrongHeaders,body}),env,"governor")).status,403);
  assert.equal((await authorizeScopedIngress(new Request(url,{method:"POST",headers:good.headers,body:body+" "}),env,"governor")).reason,"body_binding_mismatch");
  assert.equal((await authorizeScopedIngress(new Request(url+"&org=elsewhere",{method:"POST",headers:good.headers,body}),env,"governor")).status,403);
  assert.equal((await authorizeScopedIngress(good,env,"graph")).status,404);
});

test("expired and future-issued identities are rejected independently of valid signature", async () => {
  const req=await signed();
  const ok=await authorizeScopedIngress(req,env,"governor");
  const now=Date.now();
  assert.equal((await authorizeScopedIngress(req,env,"governor",now+120000)).reason,"identity_scope_or_freshness_invalid");
  assert.equal((await authorizeScopedIngress(req,env,"governor",now-20000)).reason,"identity_scope_or_freshness_invalid");
  assert.equal(ok.ok,true);
});

test("unknown caller, missing server secret, and unsupported action are denied",async()=>{
  const valid=await signed();
  assert.equal((await authorizeScopedIngress(valid,{},"governor")).status,503);
  await assert.rejects(()=>signed("POST",body,url,"random-caller",GRAPH_SECRET),/caller_scope_denied/);
  assert.equal((await authorizeScopedIngress(new Request("https://executive-mesh/v1/admin",{method:"POST"}),env,"governor")).status,404);
});

test("GET run-read scope cannot be substituted for POST write scope",async()=>{
  const readUrl="https://executive-mesh/v1/executive/runs/run_123";
  const get=await signed("GET","",readUrl);
  assert.equal((await authorizeScopedIngress(get,env,"governor")).ok,true);
  assert.equal((await authorizeScopedIngress(new Request(url,{method:"POST",headers:get.headers,body}),env,"governor")).status,403);
});

test("n8n migrated caller signs the exact request using its distinct workload key",async()=>{
  let observed=false;
  const result=await callGovernor({event_id:"evt_123",target_url:"https://example.com",idempotency_key:"idem_123"},
    async (url,options)=>{
      const request=new Request(url,{method:options.method,headers:options.headers,body:options.body});
      const result=await authorizeScopedIngress(request,env,"governor");
      assert.equal(result.ok,true);
      assert.equal(result.claims.caller,"n8n");
      observed=true;
      return new Response(JSON.stringify({run_id:"run_123",terminal:"ACCEPTED"}),{status:200});
    },
    {SOURCEA_N8N_CALLER_KEY:N8N_SECRET}
  );
  assert.equal(observed,true);
  assert.equal(result.summary.terminal,"ACCEPTED");
  await assert.rejects(()=>callGovernor({event_id:"no_token"},async()=>{throw Error("must not fetch")},{}),/SOURCEA_N8N_CALLER_KEY/);
});

test("a valid HMAC cannot expand a caller's tenant or bypass absent org configuration", async () => {
  const crossTenantUrl = "https://executive-mesh/v1/executive/runs?org=othercompany";
  const otherTenant = await signed("POST", body, crossTenantUrl, "graph-studio", GRAPH_SECRET);
  // The signer can sign arbitrary org strings, but the workload policy refuses
  // to grant an uncommissioned tenant from the same HMAC key.
  const denied = await authorizeScopedIngress(otherTenant, env, "governor");
  assert.equal(denied.status, 403);
  assert.equal(denied.reason, "caller_tenant_denied");

  const valid = await signed();
  const noTenantScope = { ...env };
  delete noTenantScope.SOURCEA_GRAPH_ALLOWED_ORGS;
  assert.equal((await authorizeScopedIngress(valid, noTenantScope, "governor")).status, 503);
  assert.equal((await authorizeScopedIngress(valid, {
    ...env, SOURCEA_GRAPH_ALLOWED_ORGS: "sourcea,othercompany",
  }, "governor")).reason, "caller_tenant_scope_invalid");

  await assert.rejects(
    () => signServiceRequest("POST", crossTenantUrl, body, {
      audience: "governor", caller: "graph-studio", org: "sourcea", secret: GRAPH_SECRET,
    }), /query_tenant_mismatch/,
  );
});

test("signed body org and nested organization ID cannot select another tenant", async () => {
  const wrongTop = await signed("POST", JSON.stringify({
    event_id: "evt_test_cross_tenant", org: "othercompany",
  }));
  assert.equal((await authorizeScopedIngress(wrongTop, env, "governor")).reason,
    "signed_body_tenant_mismatch");
  const wrongNested = await signed("POST", JSON.stringify({
    event_id: "evt_nested_cross_tenant",
    payload: { organization_id: "othercompany" },
  }));
  assert.equal((await authorizeScopedIngress(wrongNested, env, "governor")).reason,
    "signed_body_tenant_mismatch");
  const correct = await signed("POST", JSON.stringify({
    event_id: "evt_consistent", organization_id: "sourcea",
  }));
  assert.equal((await authorizeScopedIngress(correct, env, "governor")).ok, true);
});

test("a valid caller HMAC does not authorize Graph Studio mutation", async () => {
  await assert.rejects(() => signServiceRequest(
    "POST", "https://graph-studio/v1/blueprints/publish?org=sourcea", JSON.stringify({}),
    { audience: "graph", caller: "founder-os", secret: "f".repeat(64) },
  ), /caller_scope_denied/);
  await assert.rejects(() => signServiceRequest(
    "POST", "https://graph-studio/v1/runs?org=sourcea", JSON.stringify({}),
    { audience: "graph", caller: "n8n", secret: N8N_SECRET },
  ), /caller_scope_denied/);
  const signedRead = await signServiceRequest(
    "GET", "https://graph-studio/v1/registry?org=sourcea", "",
    { audience: "graph", caller: "founder-os", secret: "f".repeat(64) },
  );
  const read = await authorizeScopedIngress(
    new Request("https://graph-studio/v1/registry?org=sourcea", { headers: signedRead }),
    env, "graph",
  );
  assert.equal(read.ok, true);
  assert.equal(read.claims.scope, "graph.registry.read");
});
