import {ROUTING,STAGES} from '../../lib/dignity-stream.mjs';
export default function handler(req,res){
 res.setHeader('Cache-Control','public, max-age=300, s-maxage=900');
 res.setHeader('X-Content-Type-Options','nosniff');
 if(req.method!=='GET'){res.setHeader('Allow','GET');return res.status(405).json({error:'Method not allowed'});}
 return res.status(200).json({routes:ROUTING,stages:STAGES,disclaimer:'Independent guidance only. No complaint is automatically filed with a business, regulator or tribunal.'});
}
