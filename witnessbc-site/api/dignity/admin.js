import {constantEquals,validId,STATES} from '../../lib/dignity-domain.mjs';
import {nextActions,dueState,validateEventWorkflow} from '../../lib/dignity-workstream.mjs';
import {readReport,readEvents,listReports,saveEvent,storeReady} from '../../lib/dignity-storage.mjs';
const response=(res,status,data)=>{res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');return res.status(status).json(data)};
export default async function handler(req,res){
 const key=process.env.WITNESS_ADMIN_KEY;
 const auth=String(req.headers.authorization||'').replace(/^Bearer\s+/i,'');
 if(!key||key.length<32||!constantEquals(key,auth))return response(res,401,{error:'Operator credentials required'});
 if(!storeReady())return response(res,503,{error:'Private storage unavailable'});
 if(req.method==='GET'){
  try{
   const id=typeof req.query?.id==='string'?req.query.id:null;
   if(id){if(!validId(id))return response(res,400,{error:'Invalid id'});const report=await readReport(id);if(!report)return response(res,404,{error:'Not found'});const events=await readEvents(id);const {receiptHash,...privateReport}=report;return response(res,200,{report:privateReport,events,workstream:nextActions(report,events)});}
   const page=await listReports(req.query?.cursor);
   const reports=await Promise.all(page.paths.map(async p=>{const id=p.split('/').at(-1).replace('.json','');const r=await readReport(id);if(!r)return null;const e=await readEvents(id);const work=nextActions(r,e);return {id:r.id,createdAt:r.createdAt,category:r.category,place:r.place,organization:r.organization,frequency:r.frequency,sourceType:r.sourceType,...work,due:dueState(work.nextActionAt)};}));
   return response(res,200,{reports:reports.filter(Boolean),nextCursor:page.cursor});
  }catch(e){console.error('dignity-admin-read-error',e?.name);return response(res,503,{error:'Cannot read case records'});}
 }
 if(req.method==='POST'){
  const {id,status,internalNote,publicNote,evidenceUrl,owner,priority,nextActionAt,route,proofLevel,nextAction,channel,outcomeType}=req.body||{};
  if(!validId(id)||!STATES.includes(status))return response(res,400,{error:'Invalid case or status'});
  if(typeof internalNote!=='string'||internalNote.trim().length<5||internalNote.length>2000)return response(res,400,{error:'Record a factual internal reason (5–2000 characters)'});
  if(evidenceUrl && (typeof evidenceUrl!=='string'||!/^https:\/\//i.test(evidenceUrl)||evidenceUrl.length>600))return response(res,400,{error:'Evidence URL must be HTTPS'});
  if(['response_requested','corroborated','resolved','corrected'].includes(status)&&!evidenceUrl)return response(res,400,{error:'Documentary evidence URL required for this transition'});
  if(publicNote && (typeof publicNote!=='string'||publicNote.length>600))return response(res,400,{error:'Public note too long'});
  try{
   const report=await readReport(id);if(!report)return response(res,404,{error:'No such report'});
   const prior=await readEvents(id);
   const last=nextActions(report,prior);
   let work;
   try{work=validateEventWorkflow({status,evidenceUrl,owner:owner||last.owner,priority:priority||last.priority,nextActionAt:nextActionAt===undefined?last.nextActionAt:nextActionAt,route:route||last.route,proofLevel:proofLevel||last.proofLevel,nextAction:nextAction===undefined?last.nextAction:nextAction,channel:channel===undefined?last.channel:channel,outcomeType:outcomeType===undefined?last.outcomeType:outcomeType},last.status);}
   catch(e){return response(res,400,{error:e.message});}
   const event={id,status,at:new Date().toISOString(),internalNote:internalNote.trim(),publicNote:String(publicNote||'').trim(),evidenceUrl:String(evidenceUrl||'').trim(),...work,by:'Witness BC operator'};
   await saveEvent(id,event);
   return response(res,201,{recorded:true,id,status,at:event.at,workstream:work});
  }catch(e){console.error('dignity-admin-event-error',e?.name);return response(res,503,{error:'Event was not confirmed saved'});}
 }
 res.setHeader('Allow','GET, POST');return response(res,405,{error:'Method not allowed'});
}
