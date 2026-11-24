import {constantEquals,validId} from '../../lib/dignity-domain.mjs';
import {readReport,readEvents,listReports,saveEvent,storeReady} from '../../lib/dignity-storage.mjs';
import {buildStream,streamSummary,validateStreamUpdate} from '../../lib/dignity-stream.mjs';
const response=(res,status,data)=>{res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('X-Robots-Tag','noindex');return res.status(status).json(data)};
export default async function handler(req,res){
 const key=process.env.WITNESS_ADMIN_KEY;
 const auth=String(req.headers.authorization||'').replace(/^Bearer\s+/i,'');
 if(!key||key.length<32||!constantEquals(key,auth))return response(res,401,{error:'Operator credentials required'});
 if(!storeReady())return response(res,503,{error:'Private storage unavailable'});
 if(req.method==='GET'){
  try{
   const id=typeof req.query?.id==='string'?req.query.id:null;
   if(id){
    if(!validId(id))return response(res,400,{error:'Invalid id'});
    const report=await readReport(id);if(!report)return response(res,404,{error:'Not found'});
    const events=await readEvents(id);const {receiptHash,...privateReport}=report;
    return response(res,200,{report:privateReport,events,stream:buildStream(report,events)});
   }
   const page=await listReports(req.query?.cursor);
   const cases=(await Promise.all(page.paths.map(async p=>{
    const id=p.split('/').at(-1).replace('.json','');
    const r=await readReport(id);if(!r)return null;
    const e=await readEvents(id);const stream=buildStream(r,e);
    return {id:r.id,createdAt:r.createdAt,category:r.category,place:r.place,organization:r.organization,frequency:r.frequency,sourceType:r.sourceType,...stream};
   }))).filter(Boolean);
   cases.sort((a,b)=>Number(b.overdue)-Number(a.overdue)||['P1','P2','P3'].indexOf(a.priority)-['P1','P2','P3'].indexOf(b.priority)||String(a.dueAt||'').localeCompare(String(b.dueAt||'')));
   return response(res,200,{reports:cases,nextCursor:page.cursor,summary:streamSummary(cases),partial:!!page.cursor});
  }catch(e){console.error('dignity-admin-read-error',e?.name);return response(res,503,{error:'Cannot read case records'});}
 }
 if(req.method==='POST'){
  const id=req.body?.id;
  if(!validId(id))return response(res,400,{error:'Invalid case identifier'});
  let update;
  try{update=validateStreamUpdate(req.body);}catch(e){return response(res,400,{error:e.message||'Invalid workflow update'});}
  try{
   const report=await readReport(id);if(!report)return response(res,404,{error:'No such report'});
   const event={id,...update,at:new Date().toISOString(),by:'Witness BC operator',kind:'case_workflow_update',version:3};
   const saved=await saveEvent(id,event);
   if(!saved?.url)return response(res,503,{error:'Event storage receipt not confirmed'});
   return response(res,201,{recorded:true,id,status:event.status,at:event.at,owner:event.owner,nextAction:event.nextAction,dueAt:event.dueAt});
  }catch(e){console.error('dignity-admin-event-error',e?.name);return response(res,503,{error:'Event was not confirmed saved'});}
 }
 res.setHeader('Allow','GET, POST');return response(res,405,{error:'Method not allowed'});
}
