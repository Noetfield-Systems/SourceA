import {validId,digest,constantEquals} from '../../lib/dignity-domain.mjs';
import {readReport,caseStatus,storeReady} from '../../lib/dignity-storage.mjs';
import {buildStream} from '../../lib/dignity-stream.mjs';
const reply=(res,status,data)=>{res.setHeader('Cache-Control','no-store');return res.status(status).json(data)};
export default async function handler(req,res){
 if(req.method!=='POST'){res.setHeader('Allow','POST');return reply(res,405,{error:'Method not allowed'});}
 if(!storeReady())return reply(res,503,{error:'Tracking is temporarily unavailable'});
 const {id,accessCode}=req.body||{};
 if(!validId(id)||typeof accessCode!=='string'||accessCode.length>100)return reply(res,400,{error:'Invalid receipt'});
 try{
  const report=await readReport(id);
  if(!report||!constantEquals(report.receiptHash,digest(accessCode)))return reply(res,404,{error:'No matching receipt'});
  const state=await caseStatus(id);
  const workflow=buildStream(report,state.events);
  return reply(res,200,{id,status:state.status,receivedAt:report.createdAt,updatedAt:state.updatedAt||report.createdAt,category:report.category,nextStep:workflow.stageLabel,history:state.events.filter(e=>e.publicNote).map(e=>({at:e.at,status:e.status,note:e.publicNote})).slice(-20)});
 }catch(e){console.error('dignity-status-error',e?.name);return reply(res,503,{error:'Unable to read the private case status'});}
}
