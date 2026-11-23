import assert from 'node:assert/strict';
import {del} from '@vercel/blob';
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
 }finally{
  if(id){await del('dignity/v1/reports/'+id+'.json');console.log('DIGNITY_TEST_RECORD_CLEANUP=CONFIRMED');}
 }
}
