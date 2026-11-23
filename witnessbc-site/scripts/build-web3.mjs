// Witness Web3 Genesis: only a positive allowlist is published.
// The old institutional/Stripe site remains in Git history but is deliberately
// absent from the production output. No legacy asset or checkout can leak.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const web=path.join(root,'web3');
const out=path.join(root,'dist','deploy');
fs.rmSync(out,{recursive:true,force:true});
fs.mkdirSync(path.join(out,'assets'),{recursive:true});
const pages={
 'index':{title:'Witness — Build the rules. Prove the work.',description:'A Web3-native AI governance builders community. Enter Genesis, contribute evidence, earn reviewed reputation and help shape shared governance.',eyebrow:'THE GENESIS PORTAL'},
 'genesis':{title:'Genesis & Season Zero — Witness',description:'Join the Witness Genesis pilot, enter Season Zero and discover the founding community without a mandatory wallet.',eyebrow:'SEASON ZERO'},
 'quests':{title:'Quests — Witness',description:'Three founding AI governance quests. Submit reproducible evidence, receive human review and earn reputation XP.',eyebrow:'BUILD • VERIFY • EARN'},
 'guild':{title:'Builders Guild — Witness',description:'Find a role in the Witness Web3 builders community. Developers, adversarial testers, governance designers, educators and onchain contributors.',eyebrow:'JOIN THE BUILDERS'},
 'arena':{title:'Policy Arena — Witness',description:'Try an interactive, clearly labelled local agent policy decision demo, then contribute a real reproducible test through Witness Genesis.',eyebrow:'PUBLIC EXPERIMENT'},
 'reputation':{title:'Reputation — Witness',description:'Earned contribution XP, review evidence and referral activation, all grounded in real authenticated Community Economy records.',eyebrow:'PROOF OF CONTRIBUTION'},
 'governance':{title:'Governance — Witness',description:'Proposals, community decision-making and a progressive Web3-native governance model. No token or profit rights are implied.',eyebrow:'DECIDE TOGETHER'},
 'economy':{title:'Community Economy — Witness',description:'A useful Web3 community economy built on real contributions, reviewed bounties and optional crypto-native primitives.',eyebrow:'UTILITY BEFORE SPECULATION'},
 'builders':{title:'Open Builder Missions — Witness',description:'BuildRelay collaboration sprints and source-linked AI governance builder roles, independent of Witness reputation and treasury.',eyebrow:'FIND YOUR BUILD TEAM'},
 'dignity':{title:"Dignity Desk — Community Rights and Human Dignity | Witness BC",description:"Community concerns, gig workers, vulnerable people, public case tracker and accountability in British Columbia.",eyebrow:'DIGNITY FIRST'},
 'dignity/report':{title:"Report a Dignity Concern | Witness BC",description:"Prepare a first-hand community report and open an email draft. Learn about evidence and privacy.",eyebrow:'DIGNITY FIRST'},
 'dignity/cases':{title:"Community Dignity Case Tracker | Witness BC",description:"Evidence-labelled community issue summaries, right of reply, status updates and corrections.",eyebrow:'DIGNITY FIRST'},
 'dignity/cases/richmond-delivery':{title:"Richmond Delivery Worker Treatment — Witness BC",description:"A delivery worker reports repeated disrespect at Richmond McDonald's pickups; the report is not independently verified.",eyebrow:'DIGNITY FIRST'},
 'dignity/press':{title:"Press and Right-of-Reply Desk | Witness BC",description:"Research links, case records, journalist contact, public sources and correction policies.",eyebrow:'DIGNITY FIRST'},
 'dignity/standards':{title:"Evidence, Privacy and Reporting Standards | Witness BC",description:"Independent community reporting standards, privacy, protected groups and accurate sourcing.",eyebrow:'DIGNITY FIRST'},
 'manifesto':{title:'Manifesto — Witness',description:'Witness is a Web3-native builder society. Community first, crypto native, contribution before credentials.',eyebrow:'OUR DOCTRINE'}
};
const nav=[['/dignity','Dignity Desk'],['/genesis','Genesis'],['/quests','Quests'],['/guild','Guild'],['/arena','Arena'],['/economy','Economy'],['/governance','Governance']];
const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const navHtml=nav.map(([url,label])=>'<a href="'+url+'" class="nav-link" data-route="'+url+'">'+label+'</a>').join('');
const header='<header class="site-header" id="siteHeader"><div class="site-header-inner"><a class="brand" href="/" aria-label="Witness AI home"><svg class="brand-hex" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 2L4 6v12l8 4 8-4V6l-8-4z" stroke="currentColor" stroke-width="1.5"/><path d="M12 2v20M4 6l8 4 8-4" stroke="currentColor" stroke-width="1.5" opacity="0.5"/></svg><span class="brand-word">Witness AI<span class="brand-micro">WITNESS BC · WEB3 COMMUNITY</span></span></a><nav class="desktop-nav" aria-label="Main navigation">'+navHtml+'</nav><div class="nav-actions"><button class="theme-toggle" id="themeToggle" type="button" aria-label="Switch to dark theme" aria-pressed="false"><span class="theme-icon" aria-hidden="true">☾</span></button><a class="connect-link" href="/reputation">My reputation</a><a class="nav-join" href="/genesis">Enter Genesis ↗</a><button type="button" class="menu-toggle" id="menuToggle" aria-label="Open navigation" aria-expanded="false" aria-controls="mobileNav"><span></span><span></span><span></span></button></div></div><nav class="mobile-nav" id="mobileNav" aria-label="Mobile navigation" hidden>'+navHtml+'<a href="/reputation">My reputation</a><a href="/genesis" class="mobile-join">Enter Genesis ↗</a></nav></header>';
const footer='<footer class="site-footer"><div class="footer-top"><div><a class="footer-brand" href="/">WITNESS<span class="footer-dot">.</span></a><p>An independent Web3-native AI governance<br>builders community. Work before claims.</p></div><div class="footer-col"><strong>Explore</strong><a href="/dignity">Dignity Desk</a><a href="/dignity/cases">Cases</a><a href="/genesis">Genesis</a><a href="/quests">Quests</a><a href="/guild">Guild</a><a href="/arena">Policy Arena</a></div><div class="footer-col"><strong>Community</strong><a href="/reputation">Reputation</a><a href="/governance">Governance</a><a href="/builders">BuildRelay missions</a><a href="/economy">Economy</a></div><div class="footer-col"><strong>Connect</strong><a href="/dignity/report">Report a concern</a><a href="/dignity/press">Press</a><a href="/dignity/standards">Standards</a><a href="/manifesto">Manifesto</a><a href="https://community-economy-production.up.railway.app/#/pilot/witness-ai-builders" target="_blank" rel="noopener noreferrer">Community Economy ↗</a><button type="button" class="share-inline" data-share="copy">Copy invitation</button></div></div><div class="footer-bottom"><span>© '+new Date().getUTCFullYear()+' WITNESS · INDEPENDENT WEB3 COMMUNITY</span><span>NO TOKEN SALE · NO FAKE MEMBER COUNTS · WALLET OPTIONAL</span><a href="/manifesto">Community doctrine ↗</a></div></footer>';
for(const [key,metadata] of Object.entries(pages)){
 const bodyPath=path.join(web,'pages',key+'.html');
 if(!fs.existsSync(bodyPath))throw Error('Missing Web3 source page '+bodyPath);
 const body=fs.readFileSync(bodyPath,'utf8');
 const title=escape(metadata.title),description=escape(metadata.description),isHome=key==='index';
 const canonical='https://witnessbc.com/'+(isHome?'':key);
 const structured=JSON.stringify({'@context':'https://schema.org','@type':'WebPage',name:metadata.title,description:metadata.description,url:canonical,publisher:{'@type':'Organization',name:'Witness BC',url:'https://witnessbc.com/',description:'Independent community initiative, not a government agency.'}});
 const html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#ffffff"><title>'+title+'</title><meta name="description" content="'+description+'"><link rel="canonical" href="'+canonical+'"><meta property="og:type" content="website"><meta property="og:title" content="'+title+'"><meta property="og:description" content="'+description+'"><meta property="og:url" content="'+canonical+'"><meta property="og:image" content="https://witnessbc.com/assets/og.svg"><meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">'+structured+'</script><link rel="icon" type="image/svg+xml" href="/assets/mark.svg"><link rel="stylesheet" href="/assets/app.css"><script defer src="/assets/app.js"></script></head><body data-page="'+key+'"><a class="skip-link" href="#main-content">Skip to content</a><div class="top-bar"><span class="signal-beacon"></span> WITNESS BC <span class="top-spacer">/</span> DIGNITY · COMMUNITY · EVIDENCE <a href="/dignity">DIGNITY DESK ↗</a></div>'+header+'<main id="main-content">'+body+'</main>'+footer+'<div class="toast-root" id="toastRoot" role="status" aria-live="polite"></div></body></html>';
 const target=path.join(out,key+'.html');fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,html);
}
for(const asset of ['app.css','app.js','mark.svg','og.svg'])fs.copyFileSync(path.join(web,'assets',asset),path.join(out,'assets',asset));
fs.writeFileSync(path.join(out,'robots.txt'),'User-agent: *\nAllow: /\nSitemap: https://witnessbc.com/sitemap.xml\n');
const today=new Date().toISOString().slice(0,10);
fs.writeFileSync(path.join(out,'sitemap.xml'),'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+Object.keys(pages).map(key=>'<url><loc>https://witnessbc.com/'+(key==='index'?'':key)+'</loc></url>').join('')+'</urlset>');
const forbidden=[/buy\.stripe\.com/i,/stripe\.com/i,/noetfield\.com/i,/book[^<]{0,35}(call|meeting|demo)/i,/CISO/i,/institutional alignment/i,/shadow cohort/i,/corporate consulting/i,/mailto:/i];
for(const file of Object.keys(pages).map(x=>x+'.html')){
 const src=fs.readFileSync(path.join(out,file),'utf8');
 for(const pattern of forbidden)if(pattern.test(src))throw Error('Forbidden legacy acquisition in '+file+': '+pattern);
 if(!src.includes('WITNESS BC · WEB3 COMMUNITY'))throw Error('Not a Web3 document: '+file);
}
console.log('PASS Witness community + Dignity Desk built '+Object.keys(pages).length+' pages / zero legacy corporate or Stripe outputs. Published only allowlisted Web3 sources.');
