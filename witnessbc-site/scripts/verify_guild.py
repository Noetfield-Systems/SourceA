#!/usr/bin/env python3
"""Deterministic Guild acceptance checks against canonical assembled Witness assets."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "data/pages.json").read_text())
guild_manifest = next((p for p in manifest["pages"] if p["file"] == "guild.html"), None)
assert guild_manifest is not None, "Guild missing from canonical page manifest"
assert guild_manifest["content"] == "guild.html"
assert "guild" in guild_manifest["scripts"]

guild = (root / "guild.html").read_text()
home = (root / "index.html").read_text()
proof = (root / "proof.html").read_text()
pricing = (root / "pricing.html").read_text()
header = (root / "partials/header.html").read_text()
css = (root / "assets/guild.css").read_text()
js = (root / "assets/guild.js").read_text()

for title, xp in [
    ("Proof Lab QA", "80 XP"),
    ("Governance Builder", "150 XP"),
    ("Learning Contributor", "100 XP"),
]:
    assert title in guild and xp in guild, f"Missing quest {title}: {xp}"
for must in [
    "Season Zero blueprint published",
    "Official owner activation not yet verified",
    "https://community-economy-production.up.railway.app/",
    "#/pilot/witness-ai-builders",
    "wallet required",
    "submission",
    "review",
    "toolkits.html",
    "pricing.html",
    "data-guild-link",
]:
    assert must.lower() in guild.lower(), f"Guild contract missing: {must}"
assert "href=\"guild.html\"" in header
assert "href=\"guild.html\"" in home
assert 'href="guild.html#quests"' in proof
assert "Book 15-min proof" in pricing
assert "buy.stripe.com" in pricing or "stripe" in pricing.lower(), "Published payment pathway must remain"
assert "@media(max-width:390px)" in css and "@media(max-width:700px)" in css
assert "utm_source=witnessbc" in guild
assert "utm_campaign" in js
assert (root / "dist/deploy/guild.html").is_file(), "Guild not copied to deployment artifact"
assert (root / "dist/deploy/assets/guild.css").is_file()
assert (root / "dist/deploy/assets/guild.js").is_file()
print("PASS: Witness Guild assembled, distributed, navigable, responsive and revenue path intact")
