import test from 'node:test';import assert from 'node:assert/strict';
import {normalize,newReceipt,digest,validId,constantEquals,CATEGORIES} from '../lib/dignity-domain.mjs';
const good={category:CATEGORIES[0],role:'Delivery partner',place:'Richmond, BC',when:'2026-11',account:'I personally experienced repeated disrespectful delivery pickup treatment on several visits.',frequency:'Repeated',consent:true};
test('firsthand report validates and excludes unknown keys',()=>{const r=normalize({...good,unexpected:'secret'});assert.equal(r.place,'Richmond, BC');assert.equal('unexpected' in r,false);assert.equal(r.publicConsent,false)});
test('consent and valid category mandatory',()=>{assert.throws(()=>normalize({...good,consent:false}),/Acknowledgement/);assert.throws(()=>normalize({...good,category:'invented'}),/valid/);});
test('invalid email and URL refused',()=>{assert.throws(()=>normalize({...good,reply:'not-an-email'}),/email/);assert.throws(()=>normalize({...good,evidence:'http://example.com'}),/https/);});
test('spam honeypot is rejected',()=>assert.throws(()=>normalize({...good,website:'spam'}),/rejected/));
test('receipt is unique, unguessable and checks with constant comparison',()=>{const a=newReceipt(),b=newReceipt();assert.ok(validId(a.id));assert.notEqual(a.id,b.id);assert.notEqual(a.code,b.code);assert.equal(constantEquals(digest(a.code),digest(a.code)),true);assert.equal(constantEquals(digest(a.code),digest(b.code)),false);});

test('optional protection flags are boolean only',()=>{const a=normalize({...good,retaliationConcern:true,safetyConcern:false});assert.equal(a.retaliationConcern,true);assert.equal(a.safetyConcern,false);});
