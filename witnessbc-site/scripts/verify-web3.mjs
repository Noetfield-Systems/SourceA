import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'dist','deploy');
const contract=JSON.parse(fs.readFileSync(path.join(root,'config','VENTURE_IDENTITY.json'),'utf8'));
const pages=contract.allowlisted_pages;
assert.equal(contract.venture,'Witness BC');
assert.match(contract.canonical_thesis,/Web3-native/i);
assert.equal(pages.length,10);
const htmlFiles=fs.readdirSync(out).filter(x=>x.endsWith('.html')).sort();
assert.deepEqual(htmlFiles,pages.map(p=>p+'.html').sort(),'Deploy artifact contains EXACTLY ten Web3 pages');
const forbidden=[/stripe/i,/noetfield/i,/mailto:/i,/institutional alignment/i,/CISO/i,/corporate consulting/i,/book a demo/i,/shadow cohort/i,/buy\.stripe\.com/i,/government outreach/i,/paid toolkit/i];
for(const name of htmlFiles){
 const html=fs.readFileSync(path.join(out,name),'utf8');
 assert.ok(html.startsWith('<!doctype html>'),'HTML5 document '+name);
 assert.match(html,/WEB3 BUILDER SOCIETY/);
 assert.match(html,/href="\/genesis"/);
 assert.match(html,/assets\/app.css/);
 assert.match(html,/assets\/app.js/);
 for(const pattern of forbidden)assert.doesNotMatch(html,pattern,'Forbidden legacy copy on '+name);
 for(const href of html.matchAll(/href="(\/[a-z][a-z-]*)"/g)){
  const dest=href[1].slice(1);
  if(dest==='')continue;
  assert.ok(fs.existsSync(path.join(out,dest+'.html')),'Unresolved internal route '+href[1]+' on '+name);
 }
}
for(const old of ['proof.html','pricing.html','toolkits.html','contact.html','sources.html','platform.html','learn.html','faq.html','guild.css']){
 assert.ok(!fs.existsSync(path.join(out,old)),'Retired corporate page not public: '+old);
}
const quest=fs.readFileSync(path.join(out,'quests.html'),'utf8');
for(const xp of [80,100,150])assert.ok(quest.includes(xp+' XP'),'Published blueprint XP '+xp);
const genesis=fs.readFileSync(path.join(out,'genesis.html'),'utf8');
assert.ok(genesis.includes('#/pilot/witness-ai-builders'),'Actual CE pilot handoff is required');
assert.ok(genesis.includes('OWNER ACTIVATION'),'No fake live owner claim');
const reputation=fs.readFileSync(path.join(out,'reputation.html'),'utf8');
assert.ok(reputation.includes('#/profile'),'Authenticated real member desk required');
const arena=fs.readFileSync(path.join(out,'arena.html'),'utf8');
assert.ok(arena.includes('LOCAL SIMULATION ONLY'),'Demo must not claim a live execution');
const assets=fs.readdirSync(path.join(out,'assets')).sort();
assert.deepEqual(assets,['app.css','app.js','mark.svg','og.svg'],'No legacy assets can ship');
const script=fs.readFileSync(path.join(out,'assets','app.js'),'utf8');
assert.doesNotMatch(script,/Stripe|Noetfield|mailto:|fetch\s*\(/i);
assert.match(script,/witnessbc\.com\/genesis/);
assert.match(script,/farcaster|telegram/i);
console.log('PASS Witness Web3-only release: 10 pages, 4 assets, no legacy checkout, institutional content or false user/economic claims.');
