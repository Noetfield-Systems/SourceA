import {list} from '@vercel/blob';
import {storeReady} from '../../lib/dignity-storage.mjs';
export default async function handler(req,res){
 res.setHeader('Cache-Control','no-store');res.setHeader('X-Robots-Tag','noindex');
 if(req.method!=='GET'){res.setHeader('Allow','GET');return res.status(405).json({error:'Method not allowed'});}
 if(!storeReady())return res.status(503).json({healthy:false,storage:'not_configured'});
 try{
  await list({prefix:'dignity/v1/health-check/',limit:1});
  return res.status(200).json({healthy:true,storage:'private_store_accessible',reporting:'enabled'});
 }catch(e){console.error('dignity-storage-health',e?.name);return res.status(503).json({healthy:false,storage:'unavailable'});}
}
