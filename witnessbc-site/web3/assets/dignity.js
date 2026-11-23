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
  website:val(report,'website')
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
let operatorKey=null,cursor=null;
const operatorLogin=$('#dignityOperatorLogin');
const operatorHeaders=()=>({'Authorization':'Bearer '+operatorKey});
async function operatorGET(query=''){const r=await fetch('/api/dignity/admin'+query,{headers:operatorHeaders(),cache:'no-store'});const x=await r.json();if(!r.ok)throw Error(x.error||'Operator access failed');return x;}
async function refreshOperator(query=''){
 const r=await operatorGET(query);cursor=r.nextCursor;const box=$('#dignityOperatorList');box.textContent='';
 for(const item of r.reports||[]){
  const b=document.createElement('button');b.type='button';b.className='dignity-operator-entry';
  b.textContent=item.id+' · '+item.status+' · '+item.category;
  const small=document.createElement('small');small.textContent=item.place+' · '+item.createdAt+' · '+(item.organization||'No organization named');b.append(small);b.addEventListener('click',()=>detail(item.id));box.append(b);
 }
 if(!r.reports?.length){const p=document.createElement('p');p.textContent='No reports on this page.';box.append(p);}
 $('#dignityNext').hidden=!cursor;
}
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
 try{const r=await post('/api/dignity/admin',{id:val(update,'id'),status:val(update,'status'),internalNote:val(update,'internalNote'),publicNote:val(update,'publicNote'),evidenceUrl:val(update,'evidenceUrl')},operatorHeaders());txt('#dignityOperatorUpdateFeedback','Event saved: '+r.status+' at '+r.at,'success');await detail(r.id);}
 catch(err){txt('#dignityOperatorUpdateFeedback',err.message,'error');}
});
$$('.dignity-share').forEach(button=>button.addEventListener('click',async()=>{const url=button.dataset.url;if(!url)return;const done=await copy(url);button.textContent=done?'Public link copied':'Copy link: '+url;}));
})();