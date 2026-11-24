import assert from 'node:assert/strict';
import {del,list} from '@vercel/blob';
import admin from '../api/dignity/admin.js';
import postReport from '../api/dignity/report.js';
import checkStatus from '../api/dignity/status.js';
import {storeReady} from '../lib/dignity-storage.mjs';
if(!storeReady()){
 console.log('DIGNITY_STORAGE_SMOKE=SKIPPED_NO_CREDENTIALS (local/CI only; not a proof of persistence)');
}else{
 let id=null;
 function response(){return {code:200,setHeader(){},status(code){this.code=code;return this;},json(value){this.data=value;return value;}};}
 try{
  const payload={category:'Delivery / gig work',role:'Witness',place:'Synthetic test only, BC',when:'2026-11-23',account:'AUTOMATED STORAGE TEST ONLY. This is not a real person, company complaint or accepted community case.',frequency:'Once',consent:true,organization:'INTERNAL TEST DO NOT PUBLISH'};
  const saved=response();
  await postReport({method:'POST',headers:{},body:payload},saved);
  assert.equal(saved.code,201,JSON.stringify(saved.data));
  assert.equal(saved.data?.saved,true);
  id=saved.data.id;
  const check=response();
  await checkStatus({method:'POST',body:{id,accessCode:saved.data.accessCode}},check);
  assert.equal(check.code,200,JSON.stringify(check.data));
  assert.equal(check.data.status,'received');
  console.log('DIGNITY_PRIVATE_STORAGE_E2E=VERIFIED (test record stored, read back, reporter status confirmed)');
  if(process.env.WITNESS_ADMIN_KEY){
   const event=response();
   await admin({method:'POST',headers:{authorization:'Bearer '+process.env.WITNESS_ADMIN_KEY},body:{id,status:'triage',owner:'Witness BC automated QA',nextAction:'Automated synthetic verification, no outreach',internalNote:'Controlled synthetic test of append-only event persistence',publicNote:'Automated test only; no real community case'}},event);
   assert.equal(event.code,201,JSON.stringify(event.data));
   assert.equal(event.data?.recorded,true);
   const statusAfter=response();
   await checkStatus({method:'POST',body:{id,accessCode:saved.data.accessCode}},statusAfter);
   assert.equal(statusAfter.code,200,JSON.stringify(statusAfter.data));
   assert.equal(statusAfter.data.status,'triage');
   assert.equal(statusAfter.data.history.length,1);
   console.log('DIGNITY_STREAM_EVENT_E2E=VERIFIED (operator event appended, reporter progress read back)');
  }
 }finally{
  if(id){const events=await list({prefix:'dignity/v1/events/'+id+'/',limit:100});if(events.blobs?.length)await del(events.blobs.map(b=>b.url));await del('dignity/v1/reports/'+id+'.json');console.log('DIGNITY_TEST_RECORD_CLEANUP=CONFIRMED');}
 }
}
