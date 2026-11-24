import test from 'node:test';
import assert from 'node:assert/strict';
import {assessPriority,suggestedRoute,buildStream,streamSummary,validateStreamUpdate,STAGES} from '../lib/dignity-stream.mjs';
const base={id:'WBC-20261123-aaaaaaaaaaaaaaaaaaaa',createdAt:'2026-11-23T10:00:00.000Z',category:'Delivery / gig work',frequency:'Repeated'};
test('recurring report is P2 not legal finding',()=>{const p=assessPriority(base);assert.equal(p.level,'P2');assert.match(p.basis,/not an evidence/);});
test('optional retaliation signal triggers P1 without automatic accusation',()=>assert.equal(assessPriority({...base,retaliationConcern:true}).level,'P1'));
test('retail complaints route to business first, not automatically consumer regulator',()=>{
 const r=suggestedRoute({...base,category:'Retail / customer service'});
 assert.match(r.primary,/merchant/i);assert.match(r.referrals[1].condition,/Only/);
});
test('receipt stream derives due date and operator assignment from immutable events',()=>{
 const ev=[{status:'triage',at:'2026-11-23T11:00:00Z',owner:'Community Desk',nextAction:'Request documented dates',dueAt:'2026-11-26T23:59:00Z'}];
 const s=buildStream(base,ev,'2026-11-25T00:00:00Z');
 assert.equal(s.owner,'Community Desk');assert.equal(s.nextAction,'Request documented dates');assert.equal(s.overdue,false);assert.equal(s.status,'triage');
 assert.equal(buildStream(base,ev,'2026-11-27T00:00:00Z').overdue,true);
});
test('closed status is not overdue',()=>{const s=buildStream(base,[{status:'resolved',at:'2026-11-24T11:00:00Z',outcomeType:'Procedure changed'}],'2026-12-01T00:00:00Z');assert.equal(s.dueAt,null);assert.equal(s.outcomeType,'Procedure changed');});
test('operator status requires actual evidence for outward contact or resolution',()=>{
 assert.throws(()=>validateStreamUpdate({status:'response_requested',internalNote:'Sent a letter'}),/evidence/i);
 assert.equal(validateStreamUpdate({status:'response_requested',internalNote:'Sent actual written request',evidenceUrl:'https://example.org/receipt',owner:'Team A'}).status,'response_requested');
});
test('targets are internal and summaries do not pretend to cover all records',()=>{
 const s=buildStream(base,[],'2026-11-27T12:00:00Z');const m=streamSummary([s]);
 assert.equal(s.overdue,true);assert.equal(m.unassigned,1);assert.match(m.explanation,/only the fetched page/);
});
test('no unlisted stages or arbitrary outcomes',()=>{
 assert.equal(STAGES.length,9);assert.throws(()=>validateStreamUpdate({status:'convicted',internalNote:'Some reason'}),/supported/);
 assert.throws(()=>validateStreamUpdate({status:'triage',internalNote:'Some reason',outcomeType:'Guaranteed win'}),/outcome/);
});
