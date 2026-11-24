/**
 * Witness BC Dignity Stream v3.
 * Explainable routing and operator workload planning. This is neither a legal
 * determination nor an automated complaint to an outside institution.
 */
export const STAGES=[
 {key:'received',label:'Received',action:'Acknowledge receipt and protect source identity'},
 {key:'triage',label:'Triage',action:'Check location, dates, jurisdiction and immediate safety'},
 {key:'more_information',label:'Information requested',action:'Ask the reporter for missing first-hand facts'},
 {key:'under_review',label:'Evidence review',action:'Review documents, corroboration and repeated-pattern claims'},
 {key:'response_requested',label:'Response requested',action:'Follow up with the responsible organization after actual correspondence'},
 {key:'corroborated',label:'Corroborated',action:'Agree a verifiable systemic corrective action or escalation'},
 {key:'resolved',label:'Resolved',action:'Record the actual outcome and close remaining follow-ups'},
 {key:'corrected',label:'Corrected',action:'Publish or record the documented correction with context'},
 {key:'closed',label:'Closed',action:'Archive the verified final record and any unresolved limitations'}
];
const route=(name,url,condition,description)=>({name,url,condition,description});
export const ROUTING={
 'Delivery / gig work':{
  system:'Restaurant/operator policy + delivery-platform relationship',
  primary:'Identify the exact branch, franchise operator and delivery platform; request their written pickup policy and supervisory response',
  referrals:[
   route('Restaurant or franchise management',null,'Where the report concerns repeated courtesy or pickup rules','Request a documented, systems-level response rather than targeting one staff member'),
   route('Delivery platform support',null,'If the reporter works through an app','Log pickup barriers or respectful-treatment concerns within the platform'),
   route('BC Human Rights Tribunal','https://www.bchrt.bc.ca/human-rights-duties/services/','Only when supported facts indicate a protected ground and covered service','Rudeness alone is not necessarily discrimination')
  ]
 },
 'Retail / customer service':{
  system:'Merchant policy, training and customer interaction',
  primary:'Request the merchant’s formal procedure, escalation path and written corrective response',
  referrals:[
   route('Business owner / service management',null,'Where service conduct or store rules are the issue','First direct point of accountability'),
   route('Consumer Protection BC','https://www.consumerprotectionbc.ca/complaint-assistant/','Only for issues under regulated consumer law','General rude service alone may be outside its mandate'),
   route('BC Human Rights Tribunal','https://www.bchrt.bc.ca/human-rights-duties/services/','Only when protected-ground discrimination is indicated','Review the legal criteria before filing')
  ]
 },
 'Employment / workplace':{
  system:'Employer policy, workforce conditions and safeguards',
  primary:'Clarify actual employer/contractor relationship, employment terms and the employer’s internal complaint procedure',
  referrals:[
   route('WorkSafeBC','https://www.worksafebc.com/en/health-safety/hazards-exposures/bullying-harassment','Where workplace bullying/harassment prevention duties may apply','Coverage and remedies depend on working relationship and facts'),
   route('BC Employment Standards Branch','https://www2.gov.bc.ca/gov/content/employment-business/employment-standards-advice/employment-standards/complaint-process','Only for provincial employment standards such as wages/hours','Not a general rude-treatment complaint channel'),
   route('BC Human Rights Tribunal','https://www.bchrt.bc.ca/human-rights-duties/employment/','Only if protected-ground discrimination is alleged in covered employment','Do not infer discrimination from conduct alone')
  ]
 },
 'Community services':{
  system:'Public-facing service standards and accessibility',
  primary:'Identify the service operator, eligibility rules, published service standards and appeal or complaint process',
  referrals:[
   route('BC Ombudsperson','https://bcombudsperson.ca/complaints/what-we-do/','For public bodies within its jurisdiction','Usually requires attempts to resolve with the agency first'),
   route('211 BC','https://bc.211.ca/','For discovering local social supports','Referral information rather than formal enforcement')
  ]
 },
 'Housing / neighbourhood':{
  system:'Housing provider, tenancy rules and neighbourhood services',
  primary:'Distinguish tenancy from municipal service and safety concerns before selecting an authority',
  referrals:[
   route('BC Residential Tenancy Branch','https://www2.gov.bc.ca/gov/content/housing-tenancy/residential-tenancies','For covered landlord–tenant disputes','Different rules may apply to non-residential or excluded arrangements'),
   route('BC Human Rights Tribunal','https://www.bchrt.bc.ca/human-rights-duties/housing/','Only for housing discrimination linked to a protected ground','Protected-ground complaint process is separate from tenancy resolution')
  ]
 },
 'Accessibility':{
  system:'Barrier identification, accommodation and accessible service design',
  primary:'Document the concrete barrier, service involved, accommodation requested and operator response',
  referrals:[
   route('BC Human Rights Tribunal','https://www.bchrt.bc.ca/human-rights-duties/services/','For possible disability-based discrimination in covered services','Legal eligibility depends on particular facts'),
   route('BC Ombudsperson','https://bcombudsperson.ca/complaints/what-we-do/','For fairness of public authority administration','Not generally for private retail businesses')
  ]
 },
 'Public administration':{
  system:'Government service fairness and administrative process',
  primary:'Record the public body, policy, decision notice, internal review taken and a specific desired remedy',
  referrals:[
   route('BC Ombudsperson','https://bcombudsperson.ca/complaints/how-to-make-a-complaint/','For a covered public body after normal complaint attempts','Does not investigate all private companies'),
   route('Official government service channel','https://www2.gov.bc.ca/','For the direct responsible ministry or public body','Use the body’s published review and appeal procedure')
  ]
 },
 'Other':{
  system:'General community dignity and fair treatment',
  primary:'Clarify the sector, responsible operator, first-hand facts and proper review channel',
  referrals:[route('211 BC','https://bc.211.ca/','To locate relevant community services','Referral rather than an enforcement decision')]
 }
};
export const OUTCOME_TYPES=['Policy clarified','Staff training','Procedure changed','Accessibility improved','Written response','Referred externally','Unresolved','Withdrawn','Other'];
const plusDays=(iso,days)=>new Date(Date.parse(iso)+days*86400000).toISOString();
export function assessPriority(report){
 const reasons=[];
 let points=0;
 if(report?.frequency==='Repeated'){points+=2;reasons.push('Reporter describes recurrence');}
 if(report?.retaliationConcern===true){points+=2;reasons.push('Reporter indicates possible retaliation risk');}
 if(report?.safetyConcern===true){points+=3;reasons.push('Reporter indicated an urgent safety concern');}
 if(report?.category==='Accessibility'){points+=2;reasons.push('Potential access barrier requiring specific review');}
 const level=points>=3?'P1':points>=2?'P2':'P3';
 const targetHours=level==='P1'?24:level==='P2'?48:96;
 return {level,targetHours,reasons:reasons.length?reasons:['Standard community report — no urgent signals declared'],basis:'Operational triage only, not an evidence or legal finding'};
}
export function suggestedRoute(report){
 const item=ROUTING[report?.category]??ROUTING.Other;
 return {category:report?.category||'Other',...item,disclaimer:'Informational jurisdiction suggestions, not referrals sent, legal advice or findings of discrimination'};
}
export function buildStream(report,events=[],now=new Date().toISOString()){
 const sorted=[...events].sort((a,b)=>String(a.at||'').localeCompare(String(b.at||'')));
 const latest=sorted.at(-1);
 const stage=STAGES.find(s=>s.key===latest?.status)||STAGES[0];
 const priority=assessPriority(report);
 const assigned=[...sorted].reverse().find(x=>typeof x.owner==='string'&&x.owner.trim());
 const next=[...sorted].reverse().find(x=>typeof x.nextAction==='string'&&x.nextAction.trim());
 const explicit=[...sorted].reverse().find(x=>x.dueAt);
 const closed=['resolved','corrected','closed'].includes(stage.key);
 const dueAt=closed?null:(explicit?.dueAt||plusDays(latest?.at||report.createdAt||now,priority.targetHours/24));
 const overdue=Boolean(dueAt&&Date.parse(dueAt)<Date.parse(now));
 const elapsedHours=Math.max(0,Math.floor((Date.parse(now)-Date.parse(report.createdAt||now))/3600000));
 return {
  id:report.id,status:stage.key,stageLabel:stage.label,priority:priority.level,priorityReasons:priority.reasons,
  owner:assigned?.owner||'Unassigned',nextAction:next?.nextAction||stage.action,dueAt,overdue,elapsedHours,
  route:suggestedRoute(report),eventCount:sorted.length,updatedAt:latest?.at||report.createdAt||now,
  outcomeType:[...sorted].reverse().find(x=>x.outcomeType)?.outcomeType??null,
  open:!closed,targetsAreInternal:true
 };
}
export function streamSummary(cases){
 return {total:cases.length,open:cases.filter(x=>x.open).length,overdue:cases.filter(x=>x.overdue).length,
  unassigned:cases.filter(x=>x.open&&x.owner==='Unassigned').length,
  priority1:cases.filter(x=>x.open&&x.priority==='P1').length,
  statusCounts:Object.fromEntries(STAGES.map(s=>[s.key,cases.filter(x=>x.status===s.key).length])),
  explanation:'Counts reflect only the fetched page of private reports, not all Witness BC cases'};
}
export function validateStreamUpdate(input){
 const status=String(input?.status||'');
 if(!STAGES.some(x=>x.key===status)||status==='received')throw Error('Choose a supported workflow stage');
 const note=String(input?.internalNote||'').trim();
 if(note.length<5||note.length>2000)throw Error('Document an internal reason in 5–2000 characters');
 const owner=String(input?.owner||'').trim();
 if(owner.length>120)throw Error('Owner label too long');
 const nextAction=String(input?.nextAction||'').trim();
 if(nextAction.length>600)throw Error('Next action too long');
 const channel=String(input?.channel||'').trim();
 if(channel.length>80)throw Error('Channel label too long');
 const evidenceUrl=String(input?.evidenceUrl||'').trim();
 if(evidenceUrl&&(!/^https:\/\/[^\s]+$/i.test(evidenceUrl)||evidenceUrl.length>600))throw Error('Use an HTTPS evidence URL');
 if(['response_requested','corroborated','resolved','corrected'].includes(status)&&!evidenceUrl)throw Error('A real correspondence or evidence URL is required for this recorded status');
 const outcomeType=String(input?.outcomeType||'').trim();
 if(outcomeType&&!OUTCOME_TYPES.includes(outcomeType))throw Error('Choose a supported outcome type');
 const dueAt=String(input?.dueAt||'').trim();
 if(dueAt&&(!/^\d{4}-\d{2}-\d{2}$/.test(dueAt)||!Number.isFinite(Date.parse(dueAt))))throw Error('Choose a valid target date');
 const publicNote=String(input?.publicNote||'').trim();
 if(publicNote.length>600)throw Error('Public reporter note is too long');
 return {status,internalNote:note,owner,nextAction,channel,evidenceUrl,publicNote,
   dueAt:dueAt?new Date(dueAt+'T23:59:00Z').toISOString():null,
   outcomeType:outcomeType||null};
}
