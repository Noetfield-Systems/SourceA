import {put,get,list} from '@vercel/blob';
import {createHmac,randomUUID} from 'node:crypto';
import {validId,safeStatus} from './dignity-domain.mjs';
const options={access:'private'};
const pathFor=id=>{if(!validId(id))throw Error('Invalid case identifier');return 'dignity/v1/reports/'+id+'.json'};
export const storeReady=()=>Boolean(process.env.BLOB_READ_WRITE_TOKEN||(process.env.VERCEL_OIDC_TOKEN&&process.env.BLOB_STORE_ID));
const save=async(path,obj,ttlDays)=>put(path,JSON.stringify(obj),{...options,contentType:'application/json',addRandomSuffix:false,allowOverwrite:false,...(ttlDays?{ttlDays}:{})});
const load=async path=>{
 const result=await get(path,options);
 if(!result||!result.stream)return null;
 const text=await new Response(result.stream).text();
 return JSON.parse(text);
};
export const saveReport=report=>save(pathFor(report.id),report);
export const readReport=id=>load(pathFor(id));
export async function saveEvent(id,event){
 if(!validId(id))throw Error('Invalid case identifier');
 return save('dignity/v1/events/'+id+'/'+new Date().toISOString().replace(/[:.]/g,'-')+'-'+randomUUID()+'.json',event);
}
export async function readEvents(id){
 if(!validId(id))throw Error('Invalid case identifier');
 const prefix='dignity/v1/events/'+id+'/';
 let cursor,more=true,events=[],pages=0;
 while(more && pages++<10){
  const data=await list({prefix,cursor,limit:200});
  for(const b of data.blobs||[]){const e=await load(b.pathname);if(e)events.push(e);}
  more=Boolean(data.hasMore);cursor=data.cursor;
 }
 return events.sort((a,b)=>String(a.at).localeCompare(String(b.at)));
}
export async function listReports(cursor){
 const result=await list({prefix:'dignity/v1/reports/',limit:40,...(cursor?{cursor}:{})});
 return {paths:(result.blobs||[]).map(x=>x.pathname),cursor:result.hasMore?result.cursor:null};
}
export async function rateCheck(ip){
 const secret=process.env.WITNESS_ADMIN_KEY;
 if(!ip||!secret)return {allowed:true,prefix:null};
 const day=new Date().toISOString().slice(0,10);
 const hash=createHmac('sha256',secret).update(day+':'+ip).digest('hex').slice(0,32);
 const prefix='dignity/v1/rate/'+day+'/'+hash+'/';
 const {blobs}=await list({prefix,limit:13});
 return {allowed:(blobs||[]).length<12,prefix};
}
export async function recordRate(prefix){if(prefix)await save(prefix+randomUUID()+'.json',{at:new Date().toISOString()},2);}
export async function caseStatus(id){
 const events=await readEvents(id);
 return {status:safeStatus(events.at(-1)?.status),updatedAt:events.at(-1)?.at??null,eventCount:events.length,events};
}
