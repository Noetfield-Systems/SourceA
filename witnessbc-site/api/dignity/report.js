import {normalize,newReceipt,digest} from '../../lib/dignity-domain.mjs';
import {assessPriority} from '../../lib/dignity-stream.mjs';
import {saveReport,readReport,rateCheck,recordRate,storeReady} from '../../lib/dignity-storage.mjs';
const reply=(res,status,payload)=>{res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');return res.status(status).json(payload)};
export default async function handler(req,res){
 if(req.method!=='POST'){res.setHeader('Allow','POST');return reply(res,405,{error:'Method not allowed'});}
 if(!storeReady())return reply(res,503,{error:'Private report storage is temporarily unavailable. Nothing has been saved.'});
 if(Number(req.headers['content-length']||0)>16000)return reply(res,413,{error:'Report is too large'});
 const origin=req.headers.origin;
 if(origin && !/^https:\/\/(witnessbc\.com|www\.witnessbc\.com|[a-z0-9-]+\.vercel\.app)$/i.test(origin))return reply(res,403,{error:'Origin not permitted'});
 let report;
 try{report=normalize(typeof req.body==='string'?JSON.parse(req.body):req.body);}catch(e){return reply(res,400,{error:e.message||'Invalid report'});}
 const ip=String(req.headers['x-vercel-forwarded-for']||'').split(',')[0].trim();
 let limiter;
 try{limiter=await rateCheck(ip);}catch(e){return reply(res,503,{error:'Reporting storage cannot be reached. Nothing was saved.'});}
 if(!limiter.allowed)return reply(res,429,{error:'Too many reports from this connection today. Try again tomorrow.'});
 const {id,code}=newReceipt();
 const saved={id,createdAt:new Date().toISOString(),status:'received',receiptHash:digest(code),...report,private:true,source:'community',version:3,triageAtReceipt:assessPriority(report)};
 try{
  await saveReport(saved);
  const check=await readReport(id);
  if(!check||check.id!==id)throw Error('Persistence verification failed');
  try{await recordRate(limiter.prefix)}catch{/* Rate telemetry must not obscure a saved report */}
  return reply(res,201,{saved:true,id,accessCode:code,status:'received',createdAt:saved.createdAt,trackingUrl:'https://witnessbc.com/dignity/track'});
 }catch(e){console.error('dignity-report-write-failed',e?.name);return reply(res,503,{error:'Storage confirmation failed. Please keep a copy of your report and retry or use the published Witness BC contact.'});}
}
