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
  retaliationConcern:Boolean(report.elements.namedItem('retaliationConcern')?.checked),safetyConcern:Boolean(report.elements.namedItem('safetyConcern')?.checked)
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
  const p=document.createElement('p');p.textContent='Current stage: '+(r.nextStep||r.status.replaceAll('_',' '))+' · Last update: '+new Date(r.updatedAt).toLocaleString();out.append(p);
  for(const ev of r.history||[]){const row=document.createElement('p');row.textContent=new Date(ev.at).toLocaleDateString()+': '+ev.note;out.append(row);}
  txt('#dignityTrackFeedback','Receipt verified. Only permitted status details are shown.','success');
 }catch(err){$('#dignityStatusResult').hidden=true;txt('#dignityTrackFeedback',err.message,'error');}
});

/* Public sector routing: only categories, official published URLs and caveats are retrieved. */
const routeCategory=$('#dignityRouteCategory');
if(routeCategory){
 const panel=$('#dignityRoutingPanel');
 const renderRoute=route=>{
  $('#dignityRouteSystem').textContent=route?.system||'System-level review';
  $('#dignityRoutePrimary').textContent=route?.primary||'Clarify the responsible institution and policy.';
  const links=$('#dignityRouteLinks');links.textContent='';
  for(const item of route?.referrals||[]){
   const el=document.createElement('article');el.className='dstream-referral';
   const title=document.createElement(item.url?'a':'strong');
   title.textContent=item.name+(item.url?' ↗':'');
   if(item.url){title.href=item.url;title.target='_blank';title.rel='noopener noreferrer';}
   const p=document.createElement('p');p.textContent=item.condition+'. '+item.description;
   el.append(title,p);links.append(el);
  }
 };
 fetch('/api/dignity/routes',{cache:'force-cache'}).then(async r=>{if(!r.ok)throw Error('Routes unavailable');return r.json();})
  .then(data=>{const draw=()=>renderRoute(data.routes?.[routeCategory.value]);routeCategory.addEventListener('change',draw);draw();})
  .catch(()=>{const p=document.createElement('p');p.textContent='Specialist recommendations are temporarily unavailable. You can still submit a report; no referral has been sent.';$('#dignityRouteLinks').replaceChildren(p);});
}
/* Authenticated operator stream — credentials remain in memory only. */
let operatorKey=null,cursor=null,loadedReports=[];
const operatorLogin=$('#dignityOperatorLogin');
const operatorHeaders=()=>({'Authorization':'Bearer '+operatorKey});
const safeString=x=>String(x??'');
const operatorGET=async(query='')=>{
 const r=await fetch('/api/dignity/admin'+query,{headers:operatorHeaders(),cache:'no-store'});
 const x=await r.json().catch(()=>({error:'Invalid server response'}));
 if(!r.ok)throw Error(x.error||'Operator access failed');return x;
};
function operatorMetrics(){
 const open=loadedReports.filter(x=>x.open).length;
 const overdue=loadedReports.filter(x=>x.overdue).length;
 const p1=loadedReports.filter(x=>x.open&&x.priority==='P1').length;
 const unassigned=loadedReports.filter(x=>x.open&&x.owner==='Unassigned').length;
 for(const [id,value] of [['#dignityKpiOpen',open],['#dignityKpiOverdue',overdue],['#dignityKpiPriority',p1],['#dignityKpiUnassigned',unassigned],['#dignityKpiTotal',loadedReports.length]]){
  if($(id))$(id).textContent=String(value);
 }
 $('#dignityPartialNote').textContent='Live private queue · '+loadedReports.length+' case(s) loaded'+(cursor?' · more pages available':'')+'. Counts reflect loaded records, not the full archive unless all pages are loaded.';
}
function renderOperatorList(){
 const filter=$('#dignityCaseFilter')?.value||'all',search=($('#dignityCaseSearch')?.value||'').toLowerCase().trim();
 const matching=loadedReports.filter(x=>{
  if(filter==='overdue'&&!x.overdue)return false;
  if(filter==='P1'&&x.priority!=='P1')return false;
  if(filter==='unassigned'&&x.owner!=='Unassigned')return false;
  if(['response_requested','under_review','resolved'].includes(filter)&&x.status!==filter)return false;
  if(search&&!([x.id,x.organization,x.place,x.category,x.status].join(' ').toLowerCase().includes(search)))return false;
  return true;
 });
 const box=$('#dignityOperatorList');box.replaceChildren();
 for(const item of matching){
  const b=document.createElement('button');b.type='button';b.className='dignity-operator-entry dstream-case-entry';
  const top=document.createElement('div');top.className='dstream-case-top';
  const title=document.createElement('strong');title.textContent=item.id;
  const badge=document.createElement('span');badge.className='dstream-case-badge';badge.textContent=item.priority+(item.overdue?' · Overdue':'');
  top.append(title,badge);
  const desc=document.createElement('p');desc.textContent=[item.organization||item.category,item.place].filter(Boolean).join(' · ');
  const small=document.createElement('small');small.textContent=item.stageLabel+' · '+item.owner+' · '+(item.dueAt?'Due '+new Date(item.dueAt).toLocaleDateString():'No open deadline');
  b.append(top,desc,small);b.addEventListener('click',()=>operatorDetail(item.id));box.append(b);
 }
 if(!matching.length){const p=document.createElement('p');p.className='dignity-note';p.textContent=loadedReports.length?'No loaded cases match this filter.':'No reports on this page.';box.append(p);}
 $('#dignityNext').hidden=!cursor;operatorMetrics();
}
async function refreshOperator(query='',append=false){
 const r=await operatorGET(query);cursor=r.nextCursor;
 loadedReports=append?[...loadedReports,...r.reports]:r.reports||[];
 renderOperatorList();
}
function privateLine(node,name,value){
 const p=document.createElement('p');p.className='dignity-private-content';
 const label=document.createElement('strong');label.textContent=name+': ';p.append(label,document.createTextNode(safeString(value)));node.append(p);
}
async function operatorDetail(id){
 const r=await operatorGET('?id='+encodeURIComponent(id));
 const node=$('#dignityOperatorDetail');node.hidden=false;node.replaceChildren();
 const h=document.createElement('h2');h.textContent=id;node.append(h);
 const stream=r.stream||{};
 privateLine(node,'Current stage',stream.stageLabel||'Received');
 privateLine(node,'Priority',stream.priority||'P3');
 privateLine(node,'Why prioritized',(stream.priorityReasons||[]).join('; '));
 privateLine(node,'Responsible reviewer',stream.owner||'Unassigned');
 privateLine(node,'Next action',stream.nextAction||'Triage');
 privateLine(node,'Follow-up target',stream.dueAt?new Date(stream.dueAt).toLocaleString():'No active due date');
 privateLine(node,'System to review',stream.route?.system||'Undetermined');
 privateLine(node,'Suggested routing',stream.route?.primary||'Operator review');
 for(const [name,v] of Object.entries(r.report||{})){
  if(['receiptHash','private','version','triageAtReceipt'].includes(name))continue;
  privateLine(node,name,v);
 }
 const sub=document.createElement('h3');sub.textContent='Recorded action history ('+(r.events||[]).length+')';node.append(sub);
 for(const ev of r.events||[]){
  const p=document.createElement('p');p.className='dignity-private-content';
  p.textContent=ev.at+' · '+ev.status+' · '+(ev.owner||'Unassigned')+' · '+(ev.internalNote||'')+(ev.outcomeType?' · Outcome: '+ev.outcomeType:'');
  node.append(p);
 }
 const form=$('#dignityOperatorUpdate');form.hidden=false;form.reset();
 form.elements.namedItem('id').value=id;
 form.elements.namedItem('status').value=stream.status==='received'?'triage':stream.status;
 form.elements.namedItem('owner').value=stream.owner==='Unassigned'?'':stream.owner||'';
 form.elements.namedItem('nextAction').value=stream.nextAction||'';
 if(stream.dueAt)form.elements.namedItem('dueAt').value=stream.dueAt.slice(0,10);
 node.scrollIntoView({behavior:'smooth',block:'start'});
}
if(operatorLogin)operatorLogin.addEventListener('submit',async e=>{
 e.preventDefault();operatorKey=val(operatorLogin,'key');
 txt('#dignityOperatorFeedback','Reading the private work queue…');
 try{await refreshOperator();$('#dignityOperatorDesk').hidden=false;operatorLogin.hidden=true;txt('#dignityOperatorFeedback','');}
 catch(err){operatorKey=null;txt('#dignityOperatorFeedback',err.message,'error');}
});
$('#dignityReload')?.addEventListener('click',()=>refreshOperator().catch(e=>txt('#dignityOperatorUpdateFeedback',e.message,'error')));
$('#dignityNext')?.addEventListener('click',()=>cursor&&refreshOperator('?cursor='+encodeURIComponent(cursor),true).catch(e=>txt('#dignityOperatorUpdateFeedback',e.message,'error')));
$('#dignityCaseFilter')?.addEventListener('change',renderOperatorList);
$('#dignityCaseSearch')?.addEventListener('input',renderOperatorList);
$('#dignityLogout')?.addEventListener('click',()=>{
 operatorKey=null;cursor=null;loadedReports=[];
 $('#dignityOperatorDesk').hidden=true;operatorLogin.hidden=false;operatorLogin.reset();
 $('#dignityOperatorList').replaceChildren();$('#dignityOperatorDetail').hidden=true;$('#dignityOperatorUpdate').hidden=true;
});
const update=$('#dignityOperatorUpdate');
if(update)update.addEventListener('submit',async e=>{
 e.preventDefault();if(!update.reportValidity())return;txt('#dignityOperatorUpdateFeedback','Recording a dated, private case event…');
 try{
  const id=val(update,'id');
  const payload={id,status:val(update,'status'),owner:val(update,'owner'),nextAction:val(update,'nextAction'),
    dueAt:val(update,'dueAt'),channel:val(update,'channel'),internalNote:val(update,'internalNote'),
    publicNote:val(update,'publicNote'),evidenceUrl:val(update,'evidenceUrl'),outcomeType:val(update,'outcomeType')};
  const r=await post('/api/dignity/admin',payload,operatorHeaders());
  if(!r.recorded)throw Error('No event storage receipt');
  await refreshOperator();await operatorDetail(r.id);
  txt('#dignityOperatorUpdateFeedback','Recorded: '+r.status+' at '+r.at,'success');
 }catch(err){txt('#dignityOperatorUpdateFeedback',err.message||'Unable to confirm the event.','error');}
});
$$('.dignity-share').forEach(button=>button.addEventListener('click',async()=>{const url=button.dataset.url;if(!url)return;const done=await copy(url);button.textContent=done?'Public link copied':'Copy link: '+url;}));
})();