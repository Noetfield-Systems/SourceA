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
 'index':{title:'Witness BC — Before Change · The Wildcard of Change',description:'Witness Before Change: a Web3-native cultural and social commons of stories, art, justice, fictional worlds and creative belonging. Enter Genesis and help write the next chapter.',eyebrow:'THE GENESIS PORTAL'},
 'genesis':{title:'Genesis & Season Zero — Witness',description:'Join the Witness Genesis pilot, enter Season Zero and discover the founding community without a mandatory wallet.',eyebrow:'SEASON ZERO'},
 'quests':{title:'Quests — Witness',description:'Seven social, cultural and optional technical Genesis quests. Submit reproducible evidence, receive human review and earn reputation XP.',eyebrow:'BUILD • VERIFY • EARN'},
 'guild':{title:'Builders Guild — Witness',description:'Find a role in the Witness Web3 builders community. Developers, adversarial testers, governance designers, educators and onchain contributors.',eyebrow:'JOIN THE BUILDERS'},
 'arena':{title:'Policy Arena — Witness',description:'Try an interactive, clearly labelled local agent policy decision demo, then contribute a real reproducible test through Witness Genesis.',eyebrow:'PUBLIC EXPERIMENT'},
 'reputation':{title:'Reputation — Witness',description:'Earned contribution XP, review evidence and referral activation, all grounded in real authenticated Community Economy records.',eyebrow:'PROOF OF CONTRIBUTION'},
 'governance':{title:'Governance — Witness',description:'Proposals, community decision-making and a progressive Web3-native governance model. No token or profit rights are implied.',eyebrow:'DECIDE TOGETHER'},
 'economy':{title:'Community Economy — Witness',description:'A useful Web3 community economy built on real contributions, reviewed bounties and optional crypto-native primitives.',eyebrow:'UTILITY BEFORE SPECULATION'},
 'builders':{title:'Open Builder Missions — Witness',description:'BuildRelay collaboration sprints and source-linked AI governance builder roles, independent of Witness reputation and treasury.',eyebrow:'FIND YOUR BUILD TEAM'},
 'manifesto':{title:'Manifesto — Witness',description:'Witness is an independent cultural and spiritual Web3 commons: myth, narrative, memory, law, self-awareness and social change.',eyebrow:'OUR DOCTRINE'},
 'commons':{title:'The Commons — Witness BC',description:'An independent Web3 cultural community for people, ideas, creativity, stories and change. Join without a token or mandatory wallet.',eyebrow:'SOCIAL COMMONS'},
 'stories':{title:'Story Hall — Witness BC',description:'Original fiction, personal stories with consent, cultural memory, speculative worlds and a community of thoughtful readers and creators.',eyebrow:'THE STORY HALL'},
 'circles':{title:'Open Circles — Witness BC',description:'Six social circles for stories, belonging, self-awareness, culture, governance and builders. Find your people without a token gate.',eyebrow:'THE CIRCLES'},
 'gatherings':{title:'Gatherings — Witness BC',description:'Proposed story nights, weekly questions, listening rooms and open studios. Real RSVP via authenticated community events when published.',eyebrow:'COMMUNITY RITUALS'},
 'fandom':{title:'Creative House — Witness BC',description:'Make shared lore, original characters, zines and fan art while keeping authorship, attribution and consent.',eyebrow:'CREATIVE FANDOM'},
 'collectibles':{title:'Witness Marks — Digital Culture',description:'Explore optional future cultural NFTs and digital mementos for genuine contributions; no mint, token sale or funded collection claimed.',eyebrow:'OPTIONAL COLLECTIBLES'},
 'world':{title:'Before Change — The Witness World',description:'Enter the dystopian world of Witness: the Glass City, the Underarchive, six original characters and an interactive Remember, Resist or Rebuild story.',eyebrow:'A LIVING WORLD'},
 'mythos':{title:'The Wildcard of Change — Witness BC',description:'A living archetypal universe of memory, exile, covenant, justice, rebellion, calling and renewal. Explore twelve forces and create an original mythic story seed.',eyebrow:'THE WILDCARD'}
};
const nav=[['/genesis','Genesis'],['/commons','Commons'],['/mythos','Mythos'],['/world','World'],['/stories','Stories'],['/circles','Circles']];
const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const navHtml=nav.map(([url,label])=>'<a href="'+url+'" class="nav-link" data-route="'+url+'">'+label+'</a>').join('');
const header='<header class="site-header" id="siteHeader"><div class="site-header-inner"><a class="brand" href="/" aria-label="Witness AI home"><svg class="brand-hex" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 2L4 6v12l8 4 8-4V6l-8-4z" stroke="currentColor" stroke-width="1.5"/><path d="M12 2v20M4 6l8 4 8-4" stroke="currentColor" stroke-width="1.5" opacity="0.5"/></svg><span class="brand-word">Witness AI<span class="brand-micro">WITNESS BC · WEB3 COMMUNITY</span></span></a><nav class="desktop-nav" aria-label="Main navigation">'+navHtml+'</nav><div class="nav-actions"><button class="theme-toggle" id="themeToggle" type="button" aria-label="Switch to dark theme" aria-pressed="false"><span class="theme-icon" aria-hidden="true">☾</span></button><a class="connect-link" href="/reputation">My reputation</a><a class="nav-join" href="/genesis">Enter Genesis ↗</a><button type="button" class="menu-toggle" id="menuToggle" aria-label="Open navigation" aria-expanded="false" aria-controls="mobileNav"><span></span><span></span><span></span></button></div></div><nav class="mobile-nav" id="mobileNav" aria-label="Mobile navigation" hidden>'+navHtml+'<a href="/reputation">My reputation</a><a href="/genesis" class="mobile-join">Enter Genesis ↗</a></nav></header>';
const footer='<footer class="site-footer"><div class="footer-top"><div><a class="footer-brand" href="/">WITNESS<span class="footer-dot">.</span></a><p>An independent cultural and social Web3 commons for stories, ideas and change.<br>People before tokens. Culture before speculation.</p></div><div class="footer-col"><strong>Gather</strong><a href="/commons">The Commons</a><a href="/stories">Story Hall</a><a href="/circles">Open Circles</a><a href="/gatherings">Gatherings</a></div><div class="footer-col"><strong>Create</strong><a href="/fandom">Creative House</a><a href="/world">The Living World</a><a href="/mythos">The Wildcard</a><a href="/collectibles">Witness Marks</a><a href="/quests">Founding quests</a><a href="/arena">Policy Arena</a></div><div class="footer-col"><strong>Shape</strong><a href="/genesis">Genesis</a><a href="/governance">Governance</a><a href="/guild">Builders</a><a href="/reputation">Reputation</a><a href="/manifesto">Manifesto</a><button type="button" class="share-inline" data-share="copy">Copy invitation</button></div></div><div class="footer-bottom"><span>© '+new Date().getUTCFullYear()+' WITNESS BC · INDEPENDENT WEB3 COMMUNITY</span><span>WALLET OPTIONAL · STORIES &amp; PEOPLE FIRST · NO TOKEN SALE</span><a href="/manifesto">Community doctrine ↗</a></div></footer>';
for(const [key,metadata] of Object.entries(pages)){
 const bodyPath=path.join(web,'pages',key+'.html');
 if(!fs.existsSync(bodyPath))throw Error('Missing Web3 source page '+bodyPath);
 const body=fs.readFileSync(bodyPath,'utf8');
 const title=escape(metadata.title),description=escape(metadata.description),isHome=key==='index';
 const canonical='https://witnessbc.com/'+(isHome?'':key);
 const html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#ffffff"><title>'+title+'</title><meta name="description" content="'+description+'"><link rel="canonical" href="'+canonical+'"><meta property="og:type" content="website"><meta property="og:title" content="'+title+'"><meta property="og:description" content="'+description+'"><meta property="og:url" content="'+canonical+'"><meta property="og:image" content="https://witnessbc.com/assets/og.svg"><meta name="twitter:card" content="summary_large_image"><link rel="icon" type="image/svg+xml" href="/assets/mark.svg"><link rel="stylesheet" href="/assets/app.css"><script defer src="/assets/app.js"></script></head><body data-page="'+key+'"><a class="skip-link" href="#main-content">Skip to content</a><div class="top-bar"><span class="signal-beacon"></span> WITNESS BC <span class="top-spacer">/</span> WEB3 GENESIS · SEASON ZERO <a href="/manifesto">THE COMMUNITY DOCTRINE ↗</a></div>'+header+'<main id="main-content">'+body+'</main>'+footer+'<div class="toast-root" id="toastRoot" role="status" aria-live="polite"></div></body></html>';
 fs.writeFileSync(path.join(out,key+'.html'),html);
}
for(const asset of ['app.css','app.js','mark.svg','og.svg'])fs.copyFileSync(path.join(web,'assets',asset),path.join(out,'assets',asset));
fs.writeFileSync(path.join(out,'robots.txt'),'User-agent: *\nAllow: /\nSitemap: https://witnessbc.com/sitemap.xml\n');
const today=new Date().toISOString().slice(0,10);
fs.writeFileSync(path.join(out,'sitemap.xml'),'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+Object.keys(pages).map(key=>'<url><loc>https://witnessbc.com/'+(key==='index'?'':key)+'</loc><lastmod>'+today+'</lastmod></url>').join('')+'</urlset>');
const forbidden=[/buy\.stripe\.com/i,/stripe\.com/i,/noetfield\.com/i,/book[^<]{0,35}(call|meeting|demo)/i,/CISO/i,/institutional alignment/i,/shadow cohort/i,/corporate consulting/i,/mailto:/i];
for(const file of fs.readdirSync(out).filter(x=>x.endsWith('.html'))){
 const src=fs.readFileSync(path.join(out,file),'utf8');
 for(const pattern of forbidden)if(pattern.test(src))throw Error('Forbidden legacy acquisition in '+file+': '+pattern);
 if(!src.includes('WITNESS BC · WEB3 COMMUNITY'))throw Error('Not a Web3 document: '+file);
}
console.log('PASS witness-web3-genesis built '+Object.keys(pages).length+' pages / zero legacy corporate or Stripe outputs. Published only allowlisted Web3 sources.');
