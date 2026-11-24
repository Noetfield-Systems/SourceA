import test from 'node:test';import assert from 'node:assert/strict';
import {PRIORITIES,ROUTES,STAGES,routeFor,dueState,validateEventWorkflow,publicEligible} from '../lib/dignity-workstream.mjs';
test('all issue categories have a documented, non-automatic referral route',()=>{
 const cats=['Delivery / gig work','Community services','Housing / neighbourhood','Accessibility','Employment / workplace','Retail / customer service','Public administration','Other'];
 for(const c of cats){assert.ok(ROUTES[c]);assert.match(routeFor(c).ref,/^https:\/\//);}
 assert.equal(STAGES.length,7);assert.deepEqual(PRIORITIES,['standard','high','urgent']);
});
test('deadlines are deterministic and explicitly optional',()=>{
 const now=new Date('2026-11-23T12:00:00Z');
 assert.equal(dueState('',now),'not_scheduled');assert.equal(dueState('2026-11-22',now),'overdue');
 assert.equal(dueState('2026-11-23',now),'due_today');assert.equal(dueState('2026-11-25',now),'scheduled');
 assert.equal(dueState('2026-02-30',now),'not_scheduled');
});
test('events reject invented evidence statuses and bad routing metadata',()=>{
 assert.throws(()=>validateEventWorkflow({status:'corroborated',proofLevel:'reported'}),/evidence/);
 assert.throws(()=>validateEventWorkflow({status:'response_requested',evidenceUrl:''}),/receipt/);
 assert.throws(()=>validateEventWorkflow({status:'under_review',nextActionAt:'2026-02-30'}),/valid ISO date/);
 assert.throws(()=>validateEventWorkflow({status:'under_review',priority:'top-secret'}),/priority/);
 const ok=validateEventWorkflow({status:'response_requested',evidenceUrl:'https://example.org/sent-receipt',priority:'high',proofLevel:'documents_received',owner:'Case lead',nextActionAt:'2026-11-25'});
 assert.equal(ok.owner,'Case lead');assert.equal(ok.priority,'high');
});
test('closed records cannot be silently reclassified',()=>{
 assert.throws(()=>validateEventWorkflow({status:'under_review'},'closed'),/explicit correction/);
 assert.equal(validateEventWorkflow({status:'corrected',proofLevel:'documents_received'},'closed').priority,'standard');
});
test('public release requires five independent editorial predicates',()=>{
 assert.equal(publicEligible({permission:true,redacted:true,editorApproval:true,sourceCheck:true,rightOfReply:true}),true);
 for(const k of ['permission','redacted','editorApproval','sourceCheck','rightOfReply']){
  const state={permission:true,redacted:true,editorApproval:true,sourceCheck:true,rightOfReply:true};state[k]=false;assert.equal(publicEligible(state),false);
 }
});
