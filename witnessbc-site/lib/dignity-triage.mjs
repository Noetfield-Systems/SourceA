// Witness BC — non-legal, explainable intake triage and jurisdiction guide.
// Referrals are informational only. No external messages are sent by this module.
export const LEVELS=['standard','high','urgent'];
export const ROUTES={
 'Delivery / gig work':{
  system:'Franchise pickup policy, regional supervision and platform support',
  first:'Identify the exact branch and its franchise operator. Request written pickup rules and a documented, management-level response.',
  referrals:[
   {name:'Business / franchise management',url:null,when:'For repeated disrespect or inconsistent pickup rules',note:'Focus on procedures, training and oversight, not individual employees'},
   {name:'Delivery platform support',url:null,when:'For barriers encountered during app-based pickup work',note:'Record the event with the actual platform; no automatic platform contact here'},
   {name:'BC Human Rights Tribunal',url:'https://www.bchrt.bc.ca/human-rights-duties/services/',when:'Only if facts involve a protected ground and a covered service',note:'Ordinary discourtesy alone does not prove discrimination'}
  ]
 },
 'Retail / customer service':{
  system:'Merchant policy, store training and the customer escalation path',
  first:'Contact the business operator first for a written policy explanation and corrective response.',
  referrals:[
   {name:'Business management',url:null,when:'For customer interaction and store rules',note:'General courtesy complaints begin with the responsible business'},
   {name:'Consumer Protection BC',url:'https://www.consumerprotectionbc.ca/complaint-assistant/',when:'Only if the issue is governed by consumer-protection law',note:'General rude service alone is not necessarily regulated'},
   {name:'BC Human Rights Tribunal',url:'https://www.bchrt.bc.ca/human-rights-duties/services/',when:'Only for a potential protected-ground discrimination complaint',note:'Eligibility depends on specific evidence'}
  ]
 },
 'Employment / workplace':{
  system:'Employer responsibilities, working conditions and complaint protection',
  first:'Identify the actual employer, contract status, written policies and relevant legal regime.',
  referrals:[
   {name:'WorkSafeBC',url:'https://www.worksafebc.com/en/health-safety/hazards-exposures/bullying-harassment',when:'Where WorkSafeBC prevention duties or workplace bullying/harassment coverage apply',note:'Employment and incident coverage vary'},
   {name:'BC Employment Standards Branch',url:'https://services.labour.gov.bc.ca/Complaints/s/employer-summary',when:'Only for provincial employment-standards matters such as unpaid wages',note:'Not an all-purpose courtesy regulator'},
   {name:'BC Human Rights Tribunal',url:'https://www.bchrt.bc.ca/human-rights-duties/employment/',when:'When supported facts suggest protected-ground discrimination in employment',note:'Do not presume the legal test is met'}
  ]
 },
 'Community services':{
  system:'Service operator and accountable public-body or nonprofit procedures',
  first:'Identify the provider and its public service standards, caseworker and internal review mechanisms.',
  referrals:[
   {name:'BC Ombudsperson',url:'https://bcombudsperson.ca/complaints/what-we-do/',when:'For an eligible provincial or local public authority',note:'Private retailers are generally not in jurisdiction'},
   {name:'211 BC',url:'https://bc.211.ca/',when:'To locate appropriate community resources',note:'A referral directory, not a tribunal'}
  ]
 },
 'Housing / neighbourhood':{
  system:'Tenancy rights, landlord policy or local public service',
  first:'Distinguish tenancy agreements, municipal enforcement and protected-ground concerns before referral.',
  referrals:[
   {name:'BC Residential Tenancy Branch',url:'https://www2.gov.bc.ca/gov/content/housing-tenancy/residential-tenancies',when:'For matters covered by residential tenancy law',note:'Certain arrangements are excluded'},
   {name:'BC Human Rights Tribunal',url:'https://www.bchrt.bc.ca/human-rights-duties/housing/',when:'For potentially discriminatory housing practices',note:'Requires protected-area and protected-ground facts'}
  ]
 },
 'Accessibility':{
  system:'Access barriers, accommodation and service accessibility',
  first:'Document the concrete barrier, requested accommodation and the provider response.',
  referrals:[
   {name:'BC Human Rights Tribunal',url:'https://www.bchrt.bc.ca/human-rights-duties/services/',when:'For a supported disability-related protected-ground complaint',note:'Accessibility concerns are not all automatically tribunal cases'},
   {name:'BC Ombudsperson',url:'https://bcombudsperson.ca/complaints/what-we-do/',when:'For public-authority service fairness',note:'Jurisdiction should be checked'}
  ]
 },
 'Public administration':{
  system:'Administrative fairness, reasons and public-body review',
  first:'Identify the relevant government office, decision letter, internal review and appeal routes.',
  referrals:[
   {name:'BC Ombudsperson',url:'https://bcombudsperson.ca/complaints/how-to-make-a-complaint/',when:'For a covered public agency after ordinary review avenues',note:'Separate statutory filing limits may still run'}
  ]
 },
 'Other':{
  system:'Systemic treatment and the responsible service owner',
  first:'Clarify the organization, setting, pattern and what outcome is sought before choosing a channel.',
  referrals:[{name:'211 BC',url:'https://bc.211.ca/',when:'For community resource discovery',note:'Referrals are not a finding of wrongdoing'}]
 }
};
const validISO=value=>typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&!Number.isNaN(Date.parse(value+'T00:00:00Z'));
export function prioritySuggestion(report){
 const reasons=[];
 if(report?.safetyConcern===true)reasons.push('Immediate safety concern self-reported');
 if(report?.retaliationConcern===true)reasons.push('Retaliation concern self-reported');
 if(reasons.length)return {priority:'urgent',days:1,reasons,basis:'Internal triage recommendation, not an emergency service or legal conclusion'};
 if(report?.frequency==='Repeated')reasons.push('Repeated conduct self-reported');
 if(report?.category==='Accessibility')reasons.push('Accessibility barrier requires clarification');
 if(reasons.length)return {priority:'high',days:2,reasons,basis:'Internal triage recommendation, not a verified systemic finding'};
 return {priority:'standard',days:3,reasons:['No immediate priority signal identified'],basis:'Internal review target, not a statutory deadline'};
}
export function businessDayTarget(iso,days){
 const date=new Date(iso);if(!Number.isFinite(date.getTime()))return null;
 let n=0;date.setUTCHours(12,0,0,0);
 while(n<days){date.setUTCDate(date.getUTCDate()+1);const day=date.getUTCDay();if(day!==0&&day!==6)n++;}
 return date.toISOString().slice(0,10);
}
export function firstReview(report){
 const p=prioritySuggestion(report);
 return {priority:p.priority,reviewBy:businessDayTarget(report?.createdAt,p.days),reasons:p.reasons,basis:p.basis};
}
export function routeGuide(category){
 const r=ROUTES[category]||ROUTES.Other;
 return {category:category||'Other',...r,disclaimer:'Suggestions only; not legal advice, a transmitted complaint, or a finding against an organization'};
}
