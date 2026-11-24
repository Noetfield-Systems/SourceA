import {firstReview} from './dignity-triage.mjs';
// Witness BC / Systemic Stream v3 — manual, evidence-led case management.
// This module never determines wrongdoing, discrimination, or legal liability.
export const PRIORITIES=['standard','high','urgent'];
export const PROOF_LEVELS=['reported','documents_received','independently_corroborated','disputed'];
export const ROUTES={
 'Delivery / gig work':{lane:'Delivery-platform or franchise policy',primary:'Business owner or platform escalation',ref:'https://www.mcdonalds.com/ca/en-ca/contact-us/talk-to-us.html',why:'Verify the exact franchise, its pickup rules, and the delivery platform relationship; legal workplace rules depend on actual employment status.'},
 'Community services':{lane:'Services accessibility',primary:'Service operator / relevant ombudsperson',ref:'https://bcombudsperson.ca/complaints/what-we-do/',why:'A provincial Ombudsperson remit is generally public bodies, not privately operated restaurants.'},
 'Housing / neighbourhood':{lane:'Housing and local services',primary:'Relevant landlord, tenancy agency or municipality',ref:'https://www2.gov.bc.ca/gov/content/housing-tenancy/residential-tenancies',why:'Housing and tenancy routes depend on whether the matter concerns a tenancy, property rules or public services.'},
 'Accessibility':{lane:'Accessible service & reasonable accommodation',primary:'Service operator / possible human rights pathway',ref:'https://www.bchrt.bc.ca/human-rights-duties/services/',why:'A potential human-rights issue requires connection to a protected ground and protected area; do not infer discrimination.'},
 'Employment / workplace':{lane:'Workplace standards & safety',primary:'Employer / WorkSafeBC or Employment Standards',ref:'https://www.worksafebc.com/en/health-safety/hazards-exposures/bullying-harassment',why:'Different rules apply to employees, contractors, platform workers and workplace hazards.'},
 'Retail / customer service':{lane:'Consumer & customer-service treatment',primary:'Store owner / company escalation',ref:'https://www.consumerprotectionbc.ca/complaint-assistant/',why:'Poor manners do not automatically create a statutory consumer-protection claim.'},
 'Public administration':{lane:'Administrative process fairness',primary:'Responsible government service / BC Ombudsperson',ref:'https://bcombudsperson.ca/complaints/what-we-do/',why:'Identify the actual decision-maker and review or complaint process before escalation.'},
 'Other':{lane:'Community dignity review',primary:'Relevant organization or specialized service',ref:'https://bc.211.ca/',why:'Classify specific concerns first; avoid automated accusations or unsuitable regulatory referrals.'}
};
export const STAGES=[
 {key:'receive',label:'Receive & acknowledge',owner:'Intake',objective:'Issue a real private case receipt',output:'Stored report receipt'},
 {key:'screen',label:'Screen for safety and scope',owner:'Intake reviewer',objective:'Separate immediate danger, retaliation risk and legal deadlines from ordinary service concerns',output:'Triage note'},
 {key:'verify',label:'Verify facts & patterns',owner:'Case reviewer',objective:'Confirm branch, dates, independent sources and policy; preserve competing explanations',output:'Evidence matrix'},
 {key:'route',label:'Identify accountable system',owner:'Case lead',objective:'Find franchise operator, corporate contact, regulator or service owner appropriate to the facts',output:'Routing memo'},
 {key:'engage',label:'Request documented response',owner:'Case lead',objective:'Send factual questions and preserve a dated communication receipt',output:'Outbound receipt + response target'},
 {key:'followup',label:'Track corrective action',owner:'Case lead',objective:'Assess verifiable policy, training or service changes and reply fairly',output:'Evidence-linked action log'},
 {key:'publish',label:'Publish approved record',owner:'Editor',objective:'Publish only minimal, sourced, anonymized facts with right of reply and corrections',output:'Public editorial update'}
];
export const INTERNAL_TARGETS={urgent:1,high:2,standard:3};
const datePattern=/^\d{4}-\d{2}-\d{2}$/;
export function validDate(s){
 if(typeof s!=='string'||!datePattern.test(s))return false;
 const d=new Date(s+'T00:00:00.000Z');
 return Number.isFinite(d.valueOf())&&d.toISOString().slice(0,10)===s;
}
export function routeFor(category){return ROUTES[category]||ROUTES.Other;}
export function nextActions(report,events=[]){
 const current=events.at(-1)||{};
 const initial=firstReview(report);
 const status=current.status||report.status||'received';
 const route=routeFor(report.category);
 return {status,owner:current.owner||'Unassigned',priority:PRIORITIES.includes(current.priority)?current.priority:initial.priority,
  nextActionAt:current.nextActionAt||initial.reviewBy,route:current.route||route.lane,proofLevel:current.proofLevel||'reported',
  nextAction:current.nextAction||'Identify accountable policy, facts and case owner',channel:current.channel||null,outcomeType:current.outcomeType||null,
  priorityReason:current.priority?'Operator-selected priority':initial.reasons.join('; '),
  lastActionAt:current.at||report.createdAt,sourceType:report.sourceType,category:report.category,
  suggestedChannel:route.primary,suggestedUrl:route.ref,suggestedWhy:route.why,
  evidenceCount:events.filter(e=>e.evidenceUrl).length,actionsRecorded:events.length};
}
export function dueState(nextActionAt,now=new Date()){
 if(!nextActionAt||!validDate(nextActionAt))return 'not_scheduled';
 const today=new Date(now).toISOString().slice(0,10);
 return nextActionAt<today?'overdue':nextActionAt===today?'due_today':'scheduled';
}
export function validateEventWorkflow(data,previous='received'){
 const priority=String(data.priority||'standard');
 const proofLevel=String(data.proofLevel||'reported');
 const owner=String(data.owner||'').trim();
 const nextActionAt=String(data.nextActionAt||'').trim();
 const route=String(data.route||'').trim();
 const nextAction=String(data.nextAction||'').trim();
 const channel=String(data.channel||'').trim();
 const outcomeType=String(data.outcomeType||'').trim();
 const allowedOutcomes=['Policy clarified','Staff training','Procedure changed','Accessibility improved','Written response','Referred externally','Unresolved','Withdrawn','Other'];
 if(nextAction.length>600||channel.length>80)throw new Error('Next action or channel label too long');
 if(outcomeType&&!allowedOutcomes.includes(outcomeType))throw new Error('Unsupported outcome type');
 if(!PRIORITIES.includes(priority))throw new Error('Unknown priority');
 if(!PROOF_LEVELS.includes(proofLevel))throw new Error('Unknown evidence classification');
 if(owner.length>100||route.length>130)throw new Error('Owner or routing note is too long');
 if(nextActionAt&&!validDate(nextActionAt))throw new Error('Use a valid ISO date for the next action');
 if(['corroborated','resolved'].includes(data.status)&&!['independently_corroborated','documents_received'].includes(proofLevel))throw new Error('Document the actual evidence level before declaring corroboration or resolution');
 if(data.status==='response_requested'&&!/https:\/\//.test(data.evidenceUrl||''))throw new Error('A dated outbound correspondence receipt is required');
 // Repeated status events are legitimate evidence or follow-up updates. Operators cannot silently alter old events.
 const terminal=previous==='closed'&&data.status!=='corrected'&&data.status!=='closed';
 if(terminal)throw new Error('A closed case must be reopened by an explicit correction, not silently changed');
 return {priority,proofLevel,owner:owner||'Unassigned',nextActionAt:nextActionAt||null,route:route||null,nextAction:nextAction||null,channel:channel||null,outcomeType:outcomeType||null};
}
export function publicEligible({permission=false,redacted=false,editorApproval=false,sourceCheck=false,rightOfReply=false}={}){
 return Boolean(permission&&redacted&&editorApproval&&sourceCheck&&rightOfReply);
}
