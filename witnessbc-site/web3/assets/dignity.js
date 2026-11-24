/* Witness BC — zero false confirmations: only a 201 persisted API receipt is success. */
(() => {
'use strict';
const $=s=>document.querySelector(s), $$=s=>Array.from(document.querySelectorAll(s));
const txt=(selector,message,state='')=>{const el=$(selector);if(el){el.textContent=message;el.className='dignity-feedback '+(state?'is-'+state:'');}};
const val=(form,name)=>String(form.elements.namedItem(name)?.value||'').trim();
const copy=async s=>{try{await navigator.clipboard.writeText(s);return true;}catch{return false;}};
const post=async (url,data,opts={})=>{
 const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json',...opts},body:JSON.stringify(data),cache:'no-store'});
 const body=await r.json().catch(()=>({error:'Invalid server response'}));if(!r.ok)throw Error(body.error||'Request failed');return body;
};
const report=$('#dignityReportForm');
if(report){
 let lastReceipt=null;
 const compose=()=>({
  category:val(report,'category'),role:val(report,'role'),place:val(report,'place'),when:val(report,'when'),account:val(report,'account'),
  evidence:val(report,'evidence'),reply:val(report,'reply'),organization:val(report,'organization'),
  frequency:val(report,'frequency'),desiredOutcome:val(report,'desiredOutcome'),
  consent:Boolean(report.elements.namedItem('consent')?.checked),publicConsent:Boolean(report.elements.namedItem('publicConsent')?.checked),
  website:val(report,'website'),
  retaliationConcern:Boolean(report.elements.namedItem('retaliationConcern')?.checked),
  safetyConcern:Boolean(report.elements.namedItem('safetyConcern')?.checked)
 });
 const textDraft=()=>{const d=compose();return 'Witness BC report\n'+Object.entries(d).filter(([k])=>!['website','consent','publicConsent'].includes(k)).map(([k,v])=>k+': '+v).join('\n');};
 report.addEventListener('submit',async e=>{
  e.preventDefault();if(!report.reportValidity())return;
  const button=$('#dignitySubmit');button.disabled=true;txt('#dignitySubmitFeedback','Saving your confidential report…');
  try{
   const result=await post('/api/dignity/report',compose());
   if(result.saved!==true||!result.id||!result.accessCode)throw Error('No storage receipt was returned');
   lastReceipt=result;
   $('#dignityReceipt').hidden=false;$('#dignityReceiptId').textContent=result.id;$('#dignityReceiptCode').textContent=result.accessCode;
   txt('#dignitySubmitFeedback','Saved successfully. Preserve the case number and access code.','success');
   report.querySelectorAll('input,textarea,select,button').forEach(x=>{if(x.id!=='dignityCopyReceipt')x.disabled=true;});
  }catch(err){txt('#dignitySubmitFeedback',err.message||'Submission failed. No receipt was issued.','error');button.disabled=false;}
 });
 $('#copyDignityDraft')?.addEventListener('click',async()=>{if(!report.reportValidity())return;const draft=textDraft(),box=$('#dignityDraft');box.hidden=false;box.value=draft;txt('#dignitySubmitFeedback',(await copy(draft))?'Report copied. Not yet saved.':'Select the prepared report and copy it.');});
 $('#dignityCopyReceipt')?.addEventListener('click',async()=>{if(lastReceipt){const s='Witness BC case: '+lastReceipt.id+'\nPrivate access code: '+lastReceipt.accessCode+'\nTrack: https://witnessbc.com/dignity/track';txt('#dignitySubmitFeedback',(await copy(s))?'Private receipt copied. Keep it safe.':'Select the case details and copy them.');}});
}
const tracking=$('#dignityTrackForm');
if(tracking)tracking.addEventListener('submit',async e=>{
 e.preventDefault();if(!tracking.reportValidity())return;txt('#dignityTrackFeedback','Checking private receipt…');
 try{
  const r=await post('/api/dignity/status',{id:val(tracking,'id'),accessCode:val(tracking,'accessCode')});
  const out=$('#dignityStatusResult');out.hidden=false;out.textContent='';
  const h=document.createElement('h2');h.textContent='Case '+r.id;out.append(h);
  const p=document.createElement('p');p.textContent='Current status: '+r.status.replaceAll('_',' ')+' · Last update: '+new Date(r.updatedAt).toLocaleString();out.append(p);
  for(const ev of r.history||[]){const row=document.createElement('p');row.textContent=new Date(ev.at).toLocaleDateString()+': '+ev.note;out.append(row);}
  txt('#dignityTrackFeedback','Receipt verified. Only permitted status details are shown.','success');
 }catch(err){$('#dignityStatusResult').hidden=true;txt('#dignityTrackFeedback',err.message,'error');}
});
let operatorKey=null,cursor=null,loadedRows=[],currentWorkFilter='all';
const operatorLogin=$('#dignityOperatorLogin');
const operatorHeaders=()=>({'Authorization':'Bearer '+operatorKey});
async function operatorGET(query=''){const r=await fetch('/api/dignity/admin'+query,{headers:operatorHeaders(),cache:'no-store'});const x=await r.json();if(!r.ok)throw Error(x.error||'Operator access failed');return x;}
function renderOperatorBoard(){
 const rows=loadedRows;
 const due=rows.filter(item=>['due_today','overdue'].includes(item.due)).length;
 const unassigned=rows.filter(item=>!item.owner||item.owner==='Unassigned').length;
 const high=rows.filter(item=>['high','urgent'].includes(item.priority)).length;
 for(const [selector,v] of [['#wstreamLoaded',rows.length],['#wstreamDue',due],['#wstreamUnassigned',unassigned],['#wstreamHigh',high]]){const el=$(selector);if(el)el.textContent=String(v);}
 const shown=rows.filter(item=>currentWorkFilter==='all'||(currentWorkFilter==='due'&&['due_today','overdue'].includes(item.due))||(currentWorkFilter==='unassigned'&&(!item.owner||item.owner==='Unassigned'))||(currentWorkFilter==='priority'&&['high','urgent'].includes(item.priority)));
 const box=$('#dignityOperatorList');box.textContent='';
 for(const item of shown){
  const b=document.createElement('button');b.type='button';b.className='dignity-operator-entry';b.textContent=item.id+' · '+item.status.replaceAll('_',' ')+' · '+item.category;
  const small=document.createElement('small');small.textContent=[item.place,item.organization||'Organization not identified',item.priority+' priority',item.owner||'Unassigned',item.nextActionAt?('Next: '+item.nextActionAt):'Next action not scheduled',item.due==='overdue'?'OVERDUE':''].filter(Boolean).join(' · ');
  b.append(small);b.addEventListener('click',()=>detail(item.id));box.append(b);
 }
 if(!shown.length){const p=document.createElement('p');p.className='dignity-note';p.textContent='No matching cases on the currently loaded page.';box.append(p);}
 $('#dignityNext').hidden=!cursor;
 $$('.wstream-work-filters [data-work-filter]').forEach(b=>{const active=b.dataset.workFilter===currentWorkFilter;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
}
async function refreshOperator(query=''){const r=await operatorGET(query);cursor=r.nextCursor;loadedRows=r.reports||[];renderOperatorBoard();}
$$('.wstream-work-filters [data-work-filter]').forEach(b=>b.addEventListener('click',()=>{currentWorkFilter=b.dataset.workFilter;renderOperatorBoard();}));
async function detail(id){
 const r=await operatorGET('?id='+encodeURIComponent(id));const node=$('#dignityOperatorDetail');node.hidden=false;node.textContent='';
 const h=document.createElement('h2');h.textContent=id;node.append(h);
 for(const [name,v] of Object.entries(r.report||{})){
  if(['receiptHash','private','version'].includes(name))continue;
  const p=document.createElement('p');p.className='dignity-private-content';p.textContent=name+': '+String(v);node.append(p);
 }
 const h2=document.createElement('h3');h2.textContent='Append-only event history';node.append(h2);
 for(const ev of r.events||[]){const p=document.createElement('p');p.textContent=ev.at+' · '+ev.status+' · '+ev.internalNote;node.append(p);}
 const form=$('#dignityOperatorUpdate');form.hidden=false;form.elements.namedItem('id').value=id;
 const w=r.workstream||{};for(const name of ['priority','owner','nextActionAt','route','proofLevel','nextAction','channel','outcomeType']){const control=form.elements.namedItem(name);if(control&&w[name]!==undefined&&w[name]!==null)control.value=w[name];}
 const hint=document.createElement('p');hint.className='dignity-note';hint.textContent='Suggested initial routing (not a verified formal referral): '+(w.suggestedChannel||'Manual review')+' · '+(w.suggestedWhy||'Confirm jurisdiction');node.append(hint);
}
if(operatorLogin)operatorLogin.addEventListener('submit',async e=>{
 e.preventDefault();operatorKey=val(operatorLogin,'key');txt('#dignityOperatorFeedback','Opening private review desk…');
 try{await refreshOperator();$('#dignityOperatorDesk').hidden=false;operatorLogin.hidden=true;txt('#dignityOperatorFeedback','');}
 catch(err){operatorKey=null;txt('#dignityOperatorFeedback',err.message,'error');}
});
$('#dignityReload')?.addEventListener('click',()=>refreshOperator().catch(e=>txt('#dignityOperatorUpdateFeedback',e.message,'error')));
$('#dignityNext')?.addEventListener('click',()=>cursor&&refreshOperator('?cursor='+encodeURIComponent(cursor)).catch(e=>txt('#dignityOperatorUpdateFeedback',e.message,'error')));
$('#dignityLogout')?.addEventListener('click',()=>{operatorKey=null;$('#dignityOperatorDesk').hidden=true;operatorLogin.hidden=false;operatorLogin.reset();$('#dignityOperatorList').textContent='';$('#dignityOperatorDetail').hidden=true;$('#dignityOperatorUpdate').hidden=true;});
const update=$('#dignityOperatorUpdate');
if(update)update.addEventListener('submit',async e=>{
 e.preventDefault();if(!update.reportValidity())return;txt('#dignityOperatorUpdateFeedback','Saving event…');
 try{const r=await post('/api/dignity/admin',{id:val(update,'id'),status:val(update,'status'),internalNote:val(update,'internalNote'),publicNote:val(update,'publicNote'),evidenceUrl:val(update,'evidenceUrl'),owner:val(update,'owner'),priority:val(update,'priority'),nextActionAt:val(update,'nextActionAt'),route:val(update,'route'),proofLevel:val(update,'proofLevel'),nextAction:val(update,'nextAction'),channel:val(update,'channel'),outcomeType:val(update,'outcomeType')},operatorHeaders());txt('#dignityOperatorUpdateFeedback','Event saved: '+r.status+' at '+r.at,'success');await refreshOperator();await detail(r.id);}
 catch(err){txt('#dignityOperatorUpdateFeedback',err.message,'error');}
});

// The public stream only filters curated editorial records; no private case data is requested.
const stream=$('#wstreamList');
if(stream){
 const entries=$$('#wstreamList [data-stream-kind]'),empty=$('#wstreamEmpty'),count=$('#wstreamCount');
 $$('.wstream-filters [data-stream-filter]').forEach(button=>button.addEventListener('click',()=>{
  const type=button.dataset.streamFilter;let visible=0;
  entries.forEach(entry=>{const show=type==='all'||entry.dataset.streamKind===type;entry.hidden=!show;if(show)visible++;});
  empty.hidden=visible!==0;count.textContent='Showing '+visible+' editorial record'+(visible===1?'':'s');
  $$('.wstream-filters [data-stream-filter]').forEach(b=>{const active=b===button;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
 }));
}

// The sector guide is a public, read-only explainer; it never transmits a report.
const routeChooser=$('#dignityRouteCategory');
if(routeChooser){
 const render=rule=>{
  $('#dignityRouteSystem').textContent=rule?.system||'System-level review required';
  $('#dignityRouteFirst').textContent=rule?.first||'Clarify the responsible operator and policy.';
  const box=$('#dignityRouteList');box.replaceChildren();
  for(const item of rule?.referrals||[]){
   const row=document.createElement('article');row.className='dignity-route-referral';
   const h=document.createElement(item.url?'a':'strong');h.textContent=item.name+(item.url?' ↗':'');
   if(item.url){h.href=item.url;h.target='_blank';h.rel='noopener noreferrer';}
   const p=document.createElement('p');p.textContent=item.when+'. '+item.note;
   row.append(h,p);box.append(row);
  }
 };
 fetch('/api/dignity/routes',{cache:'force-cache'}).then(async r=>{
  if(!r.ok)throw Error('Routing temporarily unavailable');return r.json();
 }).then(data=>{const draw=()=>render(data.routes?.[routeChooser.value]);routeChooser.addEventListener('change',draw);draw();})
 .catch(()=>{const p=document.createElement('p');p.textContent='Routing information is temporarily unavailable; private report submissions remain independent of this guide.';$('#dignityRouteList').replaceChildren(p);});
}
$$('.dignity-share').forEach(button=>button.addEventListener('click',async()=>{const url=button.dataset.url;if(!url)return;const done=await copy(url);button.textContent=done?'Public link copied':'Copy link: '+url;}));
})();