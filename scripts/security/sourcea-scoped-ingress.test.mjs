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
  const unknown=await signed("POST",body,url,"random-caller",GRAPH_SECRET);
  assert.equal((await authorizeScopedIngress(unknown,env,"governor")).status,403);
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
