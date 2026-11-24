import {ROUTES} from '../../lib/dignity-triage.mjs';
export default function handler(req,res){
 res.setHeader('Cache-Control','public, max-age=300, s-maxage=900');
 res.setHeader('X-Content-Type-Options','nosniff');
 res.setHeader('X-Robots-Tag','noindex');
 if(req.method!=='GET'){res.setHeader('Allow','GET');return res.status(405).json({error:'Method not allowed'});}
 return res.status(200).json({routes:ROUTES,disclaimer:'Suggestions only; no agency or company has been contacted automatically.'});
}
