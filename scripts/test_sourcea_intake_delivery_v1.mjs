#!/usr/bin/env node
/* SourceA lead-intake truth test — simulated KV/Resend only; no external sends. */
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {webcrypto} from "node:crypto";
if (!globalThis.crypto) globalThis.crypto=webcrypto;
const load=async file=>import("data:text/javascript;base64,"+Buffer.from(readFileSync(file,"utf8")).toString("base64"));
const pages=await load("cloud/pages-functions/_middleware.js");
const worker=(await load("cloud/workers/sourcea-mvp-intake-v1/src/index.js")).default;
const url="https://sourcea.app/api/commercial/mvp-intake/v1";
function request(){return new Request(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({building:"Consumer app prototype",deadline:"Next quarter",budget:"Discuss",email:"lead@example.org"})});}
const posts=[
 ["pages",(env)=>pages.onRequest({request:request(),env,next:async()=>new Response("404",{status:404})})],
 ["worker",(env)=>worker.fetch(request(),env)]
];
const savedFetch=globalThis.fetch;
let assertions=0;
try {
 for (const [name,post] of posts) {
  let response=await post({});
  assert.equal(response.status,503,name+" must fail without a durable delivery path");assert.equal((await response.json()).ok,false);assertions+=2;
  let entries=[];
  response=await post({INTAKE_KV:{put:async(k,v)=>{entries.push({k,v});}}});
  let data=await response.json();
  assert.equal(response.status,200);assert.equal(data.storage.ok,true);assert.equal(entries.length,1);assert.ok(entries[0].k.startsWith("intake:mvp-"));assert.ok(JSON.parse(entries[0].v).intake.email==="lead@example.org");assertions+=5;
  response=await post({INTAKE_KV:{put:async()=>{throw Error("simulated KV failure");}}});
  assert.equal(response.status,503,name+" must not claim persisted after write failure");assertions++;
  globalThis.fetch=async endpoint=>{assert.equal(endpoint,"https://api.resend.com/emails");return new Response(JSON.stringify({id:"test-email-id"}),{status:200,headers:{"Content-Type":"application/json"}});};
  response=await post({RESEND_API_KEY:"test-only"});
  data=await response.json();
  assert.equal(response.status,200);assert.equal(data.notify.ok,true);assertions+=2;
  globalThis.fetch=async()=>new Response(JSON.stringify({error:"down"}),{status:503});
  response=await post({RESEND_API_KEY:"test-only"});
  assert.equal(response.status,503,name+" must reject when delivery provider fails");assertions++;
  globalThis.fetch=async()=>{throw Error("simulated network outage");};
  response=await post({RESEND_API_KEY:"test-only"});
  assert.equal(response.status,503,name+" must handle provider network exceptions");assertions++;
  globalThis.fetch=savedFetch;
 }
}finally{globalThis.fetch=savedFetch;}
console.log("SOURCEA_INTAKE_TRUTH_QA_PASS "+JSON.stringify({cases:posts.length,assertions}));
