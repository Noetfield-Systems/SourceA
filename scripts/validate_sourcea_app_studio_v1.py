#!/usr/bin/env python3
"""SourceA v4 app studio source-quality gate. Stdlib only; no external services."""
from __future__ import annotations
import json
import re
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GREEN=ROOT/"SourceA-landing"/"green-unified"
class AuditHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]
        self.ids=set()
        self.links=[]
        self.errors=[]
        self.meta={}
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        self.tags.append(tag)
        if "id" in a:
            if a["id"] in self.ids:self.errors.append(f"duplicate ID: {a['id']}")
            self.ids.add(a["id"])
        if tag=="a":
            if not a.get("href"):self.errors.append("anchor with no href")
            self.links.append(a.get("href",""))
        if tag in {"meta","link"}:
            key=a.get("name") or a.get("property") or a.get("rel")
            if key:self.meta[key]=a.get("content") or a.get("href","")
def main():
    home=(GREEN/"founder-home.html").read_text()
    studio=(GREEN/"app-studio.html").read_text()
    css=(GREEN/"app-studio.css").read_text()
    teaser=(GREEN/"app-studio-teaser.css").read_text()
    share=(GREEN/"app-studio-share.js").read_text()
    pos=json.loads((GREEN/"data/sourcea-positioning-v1.json").read_text())
    routes=(ROOT/"scripts/sourcea_clean_urls_v1.py").read_text()
    audit=AuditHTML();audit.feed(studio)
    errors=list(audit.errors)
    def need(ok,label):
        if not ok:errors.append(label)
    need(pos.get("schema")=="sourcea-positioning-v1","positioning schema")
    need(pos.get("primary_cta")=="/apps","studio CTA source of truth")
    need(pos.get("secondary_cta")=="/sourcea/forge/terminal","Forge CTA source of truth")
    need(pos.get("app_studio_path")=="/apps","studio path")
    need('("/apps", "/sourcea/app-studio")' in routes and '("/studio", "/sourcea/app-studio")' in routes,"both alias routes")
    need("app-studio-teaser.css" in home and "next-generation-apps" in home,"homepage teaser markup and style")
    need("sourcea-positioning-wire-v1.js" in home,"positioning wire preserved")
    need("sourcea/proof/live" in home and "sourcea/forge/terminal" in home,"existing execution/proof links retained")
    need("Noetfield Systems Inc." in home,"existing SourceA legal ownership footer preserved")
    need("MIRRA" in home and "Atelier" in home and "independent identity and ownership" in home,"independent venture disclaimers on home")
    need("mirra-psychology.vercel.app" in studio and "atelier-connection.vercel.app" in studio,"two real public previews")
    need("forge/terminal" in studio,"existing real execution tool")
    need("https://sourcea.app/sourcea/app-studio" in studio,"canonical studio URL")
    need("hello@sourcea.app" in studio,"existing legitimate sender")
    need("data-studio-share=\"mirra\"" in studio and "data-studio-share=\"atelier\"" in studio and "data-studio-share=\"sourcea\"" in studio,"three real share invitations")
    need('id="studio-share-status"' in studio and 'role="status"' in studio,"accessible sharing feedback")
    need("navigator.share" in share and "navigator.clipboard.writeText" in share,"native share and clipboard fallback")
    need(".share-grid" in css and ".share-actions" in css,"responsive share UI")
    need("menu-open" in studio and 'aria-expanded' in studio,"accessible mobile navigation")
    need('prefers-reduced-motion' in css and 'focus-visible' in css,"motion and keyboard accessibility")
    need("max-width:540px" in css and "max-width:780px" in css,"mobile responsive rules")
    need("max-width:610px" in teaser,"homepage teaser mobile responsive rule")
    need(len(set(audit.links))>=8,"studio has useful distinct destinations")
    need(not re.search(r'fake users|100k users|verified investor interest|guaranteed viral',studio,re.I),"no fabricated traction")
    need("id=\"work\"" in studio and "id=\"method\"" in studio and "id=\"partners\"" in studio,"navigation anchors")
    need(not any(x.startswith("http://") for x in audit.links),"external links use HTTPS")
    result={"schema":"sourcea.app-studio-source-quality-v1","ok":not errors,"studio_links":len(audit.links),"studio_tags":len(audit.tags),"homepage_teaser":True,"errors":errors}
    print(json.dumps(result,indent=2))
    return 0 if not errors else 1
if __name__=="__main__":raise SystemExit(main())
