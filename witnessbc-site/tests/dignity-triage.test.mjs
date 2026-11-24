import test from 'node:test';import assert from 'node:assert/strict';
import {ROUTES,routeGuide,prioritySuggestion,businessDayTarget,firstReview} from '../lib/dignity-triage.mjs';
test('all eight official categories have routing with a no-claim caveat',()=>{assert.equal(Object.keys(ROUTES).length,8);for(const r of Object.values(ROUTES))assert.ok(r.referrals.length>=1);assert.match(routeGuide('Retail / customer service').referrals[1].when,/Only/);});
test('repeated experiences imply high internal review, not proven wrongdoing',()=>{const a=prioritySuggestion({frequency:'Repeated'});assert.equal(a.priority,'high');assert.match(a.basis,/not a verified/);});
test('urgent self-reported protection concerns remain explicit',()=>{assert.equal(prioritySuggestion({retaliationConcern:true}).priority,'urgent');assert.equal(prioritySuggestion({safetyConcern:true}).days,1);});
test('calendar does not count weekends as business days',()=>{assert.equal(businessDayTarget('2026-11-27T12:00:00Z',1),'2026-11-30');assert.equal(businessDayTarget('2026-11-23T12:00:00Z',2),'2026-11-25');});
test('default target is a suggestion not a statutory deadline',()=>{const p=firstReview({createdAt:'2026-11-23T12:00:00Z',frequency:'Repeated'});assert.equal(p.reviewBy,'2026-11-25');assert.match(p.basis,/Internal/);});
