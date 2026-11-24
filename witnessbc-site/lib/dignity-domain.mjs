import {createHash, randomBytes, timingSafeEqual} from 'node:crypto';
export const CATEGORIES=['Delivery / gig work','Community services','Housing / neighbourhood','Accessibility','Employment / workplace','Retail / customer service','Public administration','Other'];
export const ROLES=['Worker','Delivery partner','Customer','Resident','Witness','Other'];
export const STATES=['received','triage','more_information','under_review','response_requested','corroborated','resolved','corrected','closed'];
const trim=(x,max=6000)=>typeof x==='string'?x.trim().slice(0,max):'';
const mail=/^[^\s@]+@[^\s@]+\.[^\s@]+$/;
export const validId=id=>/^WBC-[0-9]{8}-[a-f0-9]{20}$/.test(String(id||''));
export const digest=x=>createHash('sha256').update(String(x)).digest('hex');
export const constantEquals=(a,b)=>{const aa=Buffer.from(String(a||''));const bb=Buffer.from(String(b||''));return aa.length===bb.length&&timingSafeEqual(aa,bb)};
export function normalize(input){
 if(!input || typeof input!=='object'||Array.isArray(input))throw new Error('A JSON report is required');
 if(trim(input.website,100))throw new Error('Submission rejected');
 const category=trim(input.category,90),role=trim(input.role,40)||'Other';
 const place=trim(input.place,160),when=trim(input.when,150),account=trim(input.account,6000);
 const evidence=trim(input.evidence,750),reply=trim(input.reply,160),organization=trim(input.organization,160);
 const desiredOutcome=trim(input.desiredOutcome,1000),frequency=trim(input.frequency,40)||'Unknown';
 if(!CATEGORIES.includes(category))throw new Error('Choose a valid issue category');
 if(!ROLES.includes(role))throw new Error('Choose a valid reporting role');
 if(place.length<3||when.length<3)throw new Error('Add a location and approximate date');
 if(account.length<30||account.length>6000)throw new Error('Describe the concern in 30 to 6000 characters');
 if(reply&&!mail.test(reply))throw new Error('Use a valid reply email');
 if(evidence && !/^https:\/\//i.test(evidence))throw new Error('Evidence link must begin with https://');
 if(!['Once','Repeated','Unknown'].includes(frequency))throw new Error('Choose how often the issue occurred');
 if(input.consent!==true)throw new Error('Acknowledgement is required');
 return {category,role,place,when,account,evidence,reply,organization,desiredOutcome,frequency,sourceType:trim(input.sourceType,25)==='other'?'Second-hand account':'First-hand account',publicConsent:input.publicConsent===true,retaliationConcern:input.retaliationConcern===true,safetyConcern:input.safetyConcern===true};
}
export function newReceipt(){
 const id='WBC-'+new Date().toISOString().slice(0,10).replaceAll('-','')+'-'+randomBytes(10).toString('hex');
 return {id,code:randomBytes(24).toString('base64url')};
}
export function safeStatus(status){return STATES.includes(status)?status:'received'}
