import assert from 'node:assert/strict';
import {del,list} from '@vercel/blob';
import adminHandler from '../api/dignity/admin.js';
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
   const headers={authorization:'Bearer '+process.env.WITNESS_ADMIN_KEY};
   const updated=response();
   await adminHandler({method:'POST',headers,body:{
    id,status:'triage',internalNote:'Synthetic case management test — not an actual community investigation',
    publicNote:'',evidenceUrl:'',owner:'Internal test only',priority:'high',nextActionAt:'2026-11-25',
    route:'Synthetic test route',proofLevel:'reported'
   }},updated);
   assert.equal(updated.code,201,'Private case event not persisted');
   const fetched=response();
   await adminHandler({method:'GET',headers,query:{id}},fetched);
   assert.equal(fetched.code,200,'Private operator case lookup failed');
   assert.ok(fetched.data?.events?.some(e=>e.status==='triage'&&e.owner==='Internal test only'),'Stored workstream metadata absent');
   const reporter=response();
   await checkStatus({method:'POST',body:{id,accessCode:saved.data.accessCode}},reporter);
   assert.equal(reporter.data?.status,'triage','Reporter status did not reflect real operator event');
   assert.ok(!JSON.stringify(reporter.data).includes('Internal test only'),'Private operator metadata leaked to reporter');
   console.log('DIGNITY_OPERATOR_STREAM_E2E=VERIFIED (assignment, event and reporter status)');
  }else console.log('DIGNITY_OPERATOR_STREAM_E2E=SKIPPED_NO_KEY');

 }finally{
  if(id){
   const prefix='dignity/v1/events/'+id+'/';
   const page=await list({prefix,limit:100});
   for(const b of page.blobs||[])await del(b.pathname);
   await del('dignity/v1/reports/'+id+'.json');
   console.log('DIGNITY_TEST_RECORD_CLEANUP=CONFIRMED');
  }
 }
}
