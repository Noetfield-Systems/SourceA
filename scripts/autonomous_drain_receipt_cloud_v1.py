#!/usr/bin/env python3
"""Autonomous drain cycle receipts — cloud persist + optional Supabase + Mac mirror."""
from __future__ import annotations

import html
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
MAC_CYCLE_DIR = SINA / "autonomous-forge-run-cycle-receipts"
LOG_NAME = "autonomous-forge-run-cycle-log-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_headless() -> bool:
    if str(os.environ.get("FBE_MODE", "")).lower() == "headless":
        return True
    if os.environ.get("FBE_HOME", "").strip() == "/app":
        return True
    return Path("/app/receipts").is_dir()


def cloud_cycle_dir() -> Path:
    if _is_headless():
        return Path("/app/receipts/cloud/autonomous-forge-run-cycles")
    return ROOT / "receipts" / "cloud" / "autonomous-forge-run-cycles"


def cloud_log_path() -> Path:
    return cloud_cycle_dir().parent / LOG_NAME


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _supabase_cfg() -> dict[str, str]:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    )
    table = os.environ.get("AUTONOMOUS_DRAIN_SUPABASE_TABLE", "autonomous_drain_cycles").strip()
    return {"url": url, "key": key, "table": table or "autonomous_drain_cycles"}


def persist_cycle_receipt(doc: dict[str, Any]) -> dict[str, Any]:
    """Write per-cycle file + append log + optional Supabase upsert."""
    at = str(doc.get("at") or _now())
    safe_at = at.replace(":", "").replace("-", "")
    cycle_dir = cloud_cycle_dir()
    cycle_dir.mkdir(parents=True, exist_ok=True)
    path = cycle_dir / f"cycle-{safe_at}-v1.json"
    _write(path, doc)

    log_path = cloud_log_path()
    log = _read(log_path)
    cycles = list(log.get("cycles") or [])
    cycles.append(
        {
            "at": at,
            "path": str(path),
            "verdict": (doc.get("decision") or {}).get("verdict"),
            "trigger_source": doc.get("trigger_source"),
            "plan_id": (doc.get("belt") or {}).get("SHIP", {}).get("plan_id"),
            "prove_ok": (doc.get("belt") or {}).get("PROVE", {}).get("ok"),
            "ship_ok": (doc.get("belt") or {}).get("SHIP", {}).get("ok"),
        }
    )
    log_row = {
        "schema": "autonomous-forge-run-cycle-log-v1",
        "at": _now(),
        "cycles": cycles[-50:],
        "count": len(cycles),
    }
    _write(log_path, log_row)

    sb = _supabase_cfg()
    sb_result: dict[str, Any] = {"ok": False, "skipped": True}
    if sb["url"] and sb["key"]:
        sb_result = _supabase_upsert(doc, cfg=sb)

    return {
        "ok": True,
        "path": str(path),
        "log_path": str(log_path),
        "supabase": sb_result,
    }


def _supabase_upsert(doc: dict[str, Any], *, cfg: dict[str, str]) -> dict[str, Any]:
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{cfg['table']}"
    row = {
        "cycle_at": doc.get("at"),
        "trigger_source": doc.get("trigger_source"),
        "verdict": (doc.get("decision") or {}).get("verdict"),
        "queue_head": doc.get("queue_head"),
        "prove_ok": (doc.get("belt") or {}).get("PROVE", {}).get("ok"),
        "ship_ok": (doc.get("belt") or {}).get("SHIP", {}).get("ok"),
        "plan_id": (doc.get("belt") or {}).get("SHIP", {}).get("plan_id"),
        "receipt": doc,
    }
    payload = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Prefer": "return=minimal",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"ok": 200 <= resp.status < 300, "status": resp.status}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": exc.read().decode("utf-8", errors="replace")[:200]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def load_last_cycles(*, limit: int = 10) -> list[dict[str, Any]]:
    cycle_dir = cloud_cycle_dir()
    if not cycle_dir.is_dir():
        return []
    paths = sorted(cycle_dir.glob("cycle-*.json"))[-limit:]
    out: list[dict[str, Any]] = []
    for p in paths:
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return out


def _plan_context(plan_id: str) -> dict[str, Any]:
    """Resolve queue head plan — title, recipe (cloud_action), registry row."""
    if not plan_id:
        return {}
    try:
        from fbe.lib.cloud_forge_run_queue_v1 import _plan_by_id, drain_ssot_path  # noqa: WPS433

        plan = _plan_by_id(plan_id) or {}
        batch = _read(drain_ssot_path())
        return {
            "plan_id": plan_id,
            "title": plan.get("title"),
            "cloud_action": plan.get("cloud_action"),
            "": plan.get(""),
            "maps_registry": plan.get("maps_registry"),
            "workstream": plan.get("workstream"),
            "tier": plan.get("tier"),
            "stack": batch.get("stack"),
            "batch_id": batch.get("batch_id"),
            "recipe_pipeline": ["PLAN", "BUILD", "VALIDATE", "RECEIPT"],
        }
    except Exception:
        return {"plan_id": plan_id}


def _cycle_proof_slice(cycle_doc: dict[str, Any]) -> dict[str, Any]:
    """Extract founder-visible plan · task · evidence · recipe from one cycle receipt."""
    pack = cycle_doc.get("pack")
    if not isinstance(pack, dict):
        pack = (cycle_doc.get("cycle") or {}).get("pack") if isinstance(cycle_doc.get("cycle"), dict) else {}
    pack = pack if isinstance(pack, dict) else {}
    last = pack.get("last_proceed") if isinstance(pack.get("last_proceed"), dict) else {}
    resolved = last.get("resolved") if isinstance(last.get("resolved"), dict) else {}
    dispatch = last.get("cloud_dispatch") if isinstance(last.get("cloud_dispatch"), dict) else {}
    forge = last.get("forge_seed_artifact") if isinstance(last.get("forge_seed_artifact"), dict) else {}
    snippets = list(dispatch.get("evidence_snippets") or forge.get("evidence_snippets") or [])[:4]
    artifact_path = str(last.get("artifact_path") or forge.get("build", {}).get("artifact_json") or "")
    receipt_url = str(dispatch.get("receipt_url") or "")
    return {
        "head_start": pack.get("head_start"),
        "head_now": pack.get("head_now"),
        "batch_id": pack.get("batch_id"),
        "shipped": pack.get("shipped") or pack.get("advanced"),
        "skipped": pack.get("skipped"),
        "plan_id": last.get("plan_id") or resolved.get("task_id"),
        "title": resolved.get("title") or last.get("title"),
        "maps_registry": last.get("maps_registry") or resolved.get("maps_registry"),
        "": dispatch.get("") or forge.get(""),
        "cloud_action": dispatch.get("cloud_action") or forge.get("cloud_action"),
        "source_url": dispatch.get("source_url") or forge.get("source_url"),
        "pipeline": last.get("pipeline") or forge.get("pipeline") or ["PLAN", "BUILD", "VALIDATE", "RECEIPT"],
        "validator_result": last.get("validator_result") or forge.get("dispatch_status"),
        "evidence_snippets": snippets,
        "artifact_path": artifact_path,
        "dispatch_receipt_url": receipt_url,
        "pack_results_tail": pack.get("pack_results_tail") or [],
    }


def _forge_seed_root() -> Path:
    if _is_headless():
        return Path("/app/receipts/forge-seed")
    return ROOT / "receipts" / "forge-seed"


def _cycle_verdict(cycle_doc: dict[str, Any]) -> str:
    decision = cycle_doc.get("decision")
    if isinstance(decision, dict):
        v = str(decision.get("verdict") or "")
        if v:
            return v
    pack = cycle_doc.get("pack")
    if isinstance(pack, dict) and pack.get("ok") and int(pack.get("shipped") or pack.get("advanced") or 0) > 0:
        return "approved"
    return ""


def _resolve_last_proof(cycle_rows: list[dict[str, Any]], cycles: list[dict[str, Any]]) -> dict[str, Any]:
    for r in reversed(cycle_rows):
        proof = r.get("proof")
        if r.get("verdict") in ("approved", "drain_complete") and isinstance(proof, dict) and proof.get("plan_id"):
            return proof
    for c in reversed(cycles):
        pack = c.get("pack")
        if not isinstance(pack, dict):
            pack = (c.get("cycle") or {}).get("pack") if isinstance(c.get("cycle"), dict) else {}
        if isinstance(pack, dict) and (pack.get("last_proceed") or pack.get("shipped")):
            return _cycle_proof_slice({**c, "pack": pack})
    return {}


def _proof_tier(evidence_source: str) -> str:
    src = (evidence_source or "").strip()
    if src == "http_fetch":
        return "verified_fetch"
    if src == "cloud_action_vendor_says":
        return "labeled_claim"
    if src == "cloud_action_locked_recipe":
        return "blocked_recipe"
    return "unknown"


def _artifact_row(d: Path) -> dict[str, Any]:
    artifact = d / "artifact-v1.json"
    row: dict[str, Any] = {
        "plan_id": d.name,
        "artifact_path": f"receipts/forge-seed/{d.name}/artifact-v1.json" if artifact.is_file() else None,
        "has_artifact": artifact.is_file(),
        "validator_result": None,
        "evidence_source": None,
        "proof_tier": "unknown",
        "sellable": False,
        "snippet_count": 0,
        "source_url": None,
        "maps_registry": None,
        "http_status": None,
        "at": None,
    }
    if not artifact.is_file():
        return row
    try:
        doc = json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        row["validator_result"] = "FAIL"
        return row
    src = str(doc.get("evidence_source") or "")
    tier = _proof_tier(src)
    row.update(
        {
            "validator_result": "PASS" if doc.get("schema") == "forge-seed-artifact-v1" else "FAIL",
            "snippet_count": len(doc.get("evidence_snippets") or []),
            "source_url": doc.get("source_url"),
            "maps_registry": doc.get("maps_registry"),
            "at": doc.get("at"),
            "": doc.get(""),
            "pipeline": doc.get("pipeline"),
        }
    )
    return _enrich_audit_row_from_artifact(row, doc)


def _tier_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"verified_fetch": 0, "labeled_claim": 0, "blocked_recipe": 0, "unknown": 0}
    for r in rows:
        tier = str(r.get("proof_tier") or "unknown")
        counts[tier] = counts.get(tier, 0) + 1
    return counts


def _dispatch_receipt_path(receipt_id: str) -> Path:
    rid = str(receipt_id or "").strip()
    if not rid:
        return Path()
    if _is_headless():
        return Path("/app/receipts/cloud-dispatch") / f"{rid}.json"
    return ROOT / "receipts" / "cloud-dispatch" / f"{rid}.json"


def _load_dispatch_receipt(receipt_id: str) -> dict[str, Any]:
    path = _dispatch_receipt_path(receipt_id)
    if not path.is_file():
        return {}
    return _read(path)


def _proof_tier_meta(*, evidence_source: str = "", http_status: int | None = None) -> dict[str, Any]:
    src = str(evidence_source or "").strip()
    if not src and http_status == 200:
        src = "http_fetch"
    if src == "http_fetch":
        return {
            "proof_tier": "verified_fetch",
            "badge": "http_fetch",
            "sellable": True,
            "tier_label": "Verified fetch — sellable proof",
        }
    if src == "cloud_action_vendor_says":
        return {
            "proof_tier": "labeled_claim",
            "badge": "vendor_says",
            "sellable": False,
            "tier_label": "Labeled claim — not market proof",
        }
    if src == "cloud_action_locked_recipe":
        return {
            "proof_tier": "blocked_recipe",
            "badge": "locked_recipe",
            "sellable": False,
            "tier_label": "Blocked recipe — queue motion only",
        }
    return {
        "proof_tier": "unknown",
        "badge": "unknown",
        "sellable": False,
        "tier_label": "Unknown — not sellable",
    }


def _enrich_audit_row_from_artifact(row: dict[str, Any], doc: dict[str, Any]) -> dict[str, Any]:
    dispatch_id = str(doc.get("dispatch_receipt_id") or "")
    dispatch = _load_dispatch_receipt(dispatch_id) if dispatch_id else {}
    src = str(doc.get("evidence_source") or dispatch.get("evidence_source") or "")
    http_status = dispatch.get("http_status")
    if http_status is None:
        http_status = doc.get("http_status")
    tier = _proof_tier_meta(evidence_source=src, http_status=int(http_status) if http_status is not None else None)
    row.update(
        {
            **tier,
            "evidence_source": src or None,
            "http_status": http_status,
            "dispatch_receipt_id": dispatch_id or None,
            "dispatch_receipt_url": dispatch.get("receipt_url"),
            "cloud_action": doc.get("cloud_action"),
            "evidence_snippet_preview": (doc.get("evidence_snippets") or [""])[0][:200] if doc.get("evidence_snippets") else None,
        }
    )
    return row


def _tier_counts_on_disk() -> dict[str, int]:
    seed_root = _forge_seed_root()
    if not seed_root.is_dir():
        return {"verified_fetch": 0, "labeled_claim": 0, "blocked_recipe": 0, "unknown": 0}
    rows = [_artifact_row(d) for d in seed_root.iterdir() if d.is_dir() and d.name.startswith("CLOUD-SEC-")]
    return _tier_counts(rows)


def evidence_audit_payload(
    *,
    limit: int = 50,
    offset: int = 0,
    plan_id: str = "",
) -> dict[str, Any]:
    """Queryable list of forge-seed row evidence on cloud disk."""
    from fbe.lib.cloud_forge_run_queue_v1 import read_head  # noqa: WPS433

    seed_root = _forge_seed_root()
    head = read_head()
    all_rows: list[dict[str, Any]] = []
    page_rows: list[dict[str, Any]] = []
    if seed_root.is_dir():
        dirs = sorted(
            [d for d in seed_root.iterdir() if d.is_dir() and d.name.startswith("CLOUD-SEC-")],
            key=lambda p: p.name,
        )
        if plan_id:
            dirs = [d for d in dirs if d.name == plan_id]
        all_rows = [_artifact_row(d) for d in dirs]
        page_rows = all_rows[offset : offset + limit]
    tier_total = _tier_counts(all_rows)
    tier_page = _tier_counts(page_rows)
    return {
        "schema": "cloud-forge-run-evidence-audit-v1",
        "at": _now(),
        "ok": True,
        "proof_tier_policy": "brain-os/law/enforcement/SOURCEA_PROOF_TIER_POLICY_LOCKED_v1.md",
        "queue_head": head.get("cloud_forge_run_head"),
        "last_completed": head.get("cloud_forge_run_last_completed"),
        "seed_root": str(seed_root),
        "total_on_disk": len(all_rows),
        "offset": offset,
        "limit": limit,
        "count": len(page_rows),
        "tier_counts_total": tier_total,
        "tier_counts_page": tier_page,
        "verified_fetch_total": tier_total.get("verified_fetch", 0),
        "labeled_claim_total": tier_total.get("labeled_claim", 0),
        "blocked_recipe_total": tier_total.get("blocked_recipe", 0),
        "report_line": (
            f"{tier_total.get('verified_fetch', 0)} verified-fetch · "
            f"{tier_total.get('labeled_claim', 0)} labeled-claim · "
            f"{tier_total.get('blocked_recipe', 0)} blocked-recipe"
        ),
        "rows": page_rows,
        "recipe_pipeline": ["PLAN", "BUILD", "VALIDATE", "RECEIPT"],
    }


def evidence_audit_row(*, plan_id: str) -> dict[str, Any]:
    """Single row — full artifact JSON when present."""
    payload = evidence_audit_payload(limit=1, offset=0, plan_id=plan_id)
    if not payload.get("rows"):
        return {"ok": False, "error": "not_found", "plan_id": plan_id}
    row = payload["rows"][0]
    seed_root = _forge_seed_root()
    artifact = seed_root / plan_id / "artifact-v1.json"
    build_md = seed_root / plan_id / "build-output-v1.md"
    out = {**payload, "plan_id": plan_id, "row": row}
    if artifact.is_file():
        try:
            out["artifact"] = json.loads(artifact.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            out["artifact"] = None
    if build_md.is_file():
        try:
            out["build_output_md"] = build_md.read_text(encoding="utf-8")[:8000]
        except OSError:
            out["build_output_md"] = None
    out["ok"] = bool(row.get("has_artifact"))
    return out


def evidence_audit_html(*, limit: int = 50, offset: int = 0, plan_id: str = "") -> str:
    payload = evidence_audit_row(plan_id=plan_id) if plan_id else evidence_audit_payload(limit=limit, offset=offset)
    tc = payload.get("tier_counts_total") or {}

    def esc(v: Any) -> str:
        return html.escape(str(v or ""))

    rows_html = []
    for r in payload.get("rows") or [payload.get("row")] if payload.get("row") else []:
        if not r:
            continue
        badge = str(r.get("badge") or r.get("proof_tier") or "unknown")
        badge_disp = {"verified_fetch": "http_fetch", "labeled_claim": "vendor_says", "blocked_recipe": "locked_recipe"}.get(
            badge, badge
        )
        cls = {"http_fetch": "tier-verified", "verified_fetch": "tier-verified", "locked_recipe": "tier-blocked", "blocked_recipe": "tier-blocked", "vendor_says": "tier-vendor", "labeled_claim": "tier-vendor"}.get(
            badge_disp, "tier-unknown"
        )
        rows_html.append(
            f"<tr><td><a href=\"?plan_id={esc(r.get('plan_id'))}\">{esc(r.get('plan_id'))}</a></td>"
            f"<td><span class=\"badge {cls}\">{esc(badge_disp)}</span></td>"
            f"<td>{esc(r.get('maps_registry'))}</td><td>{esc(r.get(''))}</td>"
            f"<td>{esc(r.get('http_status'))}</td><td>{esc(r.get('at'))}</td>"
            f"<td class=muted>{esc(r.get('evidence_snippet_preview'))}</td></tr>"
        )
    body = "\n".join(rows_html) or "<tr><td colspan=7>No rows</td></tr>"
    detail = ""
    if plan_id and payload.get("artifact"):
        art = payload["artifact"]
        detail = f"""<section class=card><h2>Row {esc(plan_id)}</h2>
<p><span class="badge {esc(payload.get('row',{}).get('badge',''))}">{esc(payload.get('row',{}).get('badge'))}</span>
 · {esc(payload.get('row',{}).get('tier_label'))}</p>
<pre class=recipe>{esc(json.dumps(art, indent=2)[:6000])}</pre></section>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>SourceA · Evidence audit</title>
<style>
body{{font-family:system-ui;background:#0b1220;color:#e8eef8;margin:0;padding:16px}}
.card{{max-width:1100px;margin:0 auto 14px;background:#141e33;border:1px solid #243352;border-radius:12px;padding:20px}}
h1{{font-size:1.2rem;margin:0}} .muted{{color:#8fa3bf;font-size:.85rem}}
table{{width:100%;border-collapse:collapse;font-size:.8rem;margin-top:12px}}
th,td{{padding:8px;border-bottom:1px solid #243352;text-align:left;vertical-align:top}}
.badge{{padding:2px 8px;border-radius:6px;font-size:.72rem;font-weight:600}}
.tier-verified{{background:#134e3a;color:#6ee7b7}}
.tier-blocked{{background:#4c1d1d;color:#fca5a5}}
.tier-vendor{{background:#422006;color:#fcd34d}}
.tier-unknown{{background:#1e293b;color:#94a3b8}}
.counts span{{margin-right:16px}}
a{{color:#7dd3fc}} pre.recipe{{font-size:.75rem;overflow:auto;background:#0f1729;padding:12px;border-radius:8px}}
</style></head><body>
<main class=card>
<h1>Cloud Forge Run · evidence audit</h1>
<p class=muted>head <strong>{esc(payload.get('queue_head'))}</strong> · total logged {esc(payload.get('total_on_disk'))} · {esc(payload.get('at'))}</p>
<p class=counts><strong>Never blend:</strong>
<span class="badge tier-verified">http_fetch {esc(tc.get('verified_fetch',0))}</span>
<span class="badge tier-vendor">vendor_says {esc(tc.get('labeled_claim',0))}</span>
<span class="badge tier-blocked">locked_recipe {esc(tc.get('blocked_recipe',0))}</span>
</p>
<p class=muted>Policy: {esc(payload.get('proof_tier_policy'))}</p>
{detail}
<table><thead><tr><th>Plan</th><th>Tier</th><th>Registry</th><th></th><th>HTTP</th><th>At</th><th>Snippet</th></tr></thead>
<tbody>{body}</tbody></table>
<p class=muted>JSON: same URL with <code>Accept: application/json</code> · single row: <code>?plan_id=CLOUD-SEC-1410</code></p>
</main></body></html>"""


def observer_payload(*, limit: int = 10) -> dict[str, Any]:
    from fbe.lib.cloud_forge_run_queue_v1 import read_head  # noqa: WPS433

    head = read_head()
    head_id = str(head.get("cloud_forge_run_head") or "")
    cycles = load_last_cycles(limit=limit)
    ramp_path = cloud_cycle_dir().parent / "autonomous-forge-run-ramp-state-v1.json"
    ramp = _read(ramp_path) if ramp_path.is_file() else _read(SINA / "autonomous-forge-run-ramp-state-v1.json")
    cycle_rows = []
    for c in cycles:
        proof = _cycle_proof_slice(c)
        verdict = _cycle_verdict(c)
        cycle_rows.append(
            {
                "at": c.get("at"),
                "trigger_source": c.get("trigger_source"),
                "verdict": verdict,
                "pack": c.get("pack") or (c.get("cycle") or {}).get("pack"),
                "prove": (c.get("belt") or {}).get("PROVE"),
                "ship": (c.get("belt") or {}).get("SHIP"),
                "proof": proof,
            }
        )
    last_proof = _resolve_last_proof(cycle_rows, cycles)
    if not isinstance(last_proof, dict):
        last_proof = {}
    return {
        "schema": "autonomous-forge-run-observer-v1",
        "at": _now(),
        "ok": True,
        "queue_head": head_id,
        "last_completed": head.get("cloud_forge_run_last_completed"),
        "head_plan": _plan_context(head_id),
        "ramp": ramp,
        "cycles": cycle_rows,
        "last_proof": last_proof,
        "last_pack": next(
            (
                p
                for c in reversed(cycles)
                for p in [c.get("pack") or (c.get("cycle") or {}).get("pack")]
                if isinstance(p, dict) and p.get("processed") is not None
            ),
            None,
        ),
    }


def mirror_cycles_to_mac(*, limit: int = 20) -> dict[str, Any]:
    """Pull cloud cycle files into ~/.sina when Mac is online."""
    MAC_CYCLE_DIR.mkdir(parents=True, exist_ok=True)
    mirrored = 0
    for doc in load_last_cycles(limit=limit):
        at = str(doc.get("at") or _now())
        safe_at = at.replace(":", "").replace("-", "")
        dest = MAC_CYCLE_DIR / f"cycle-{safe_at}-v1.json"
        _write(dest, doc)
        mirrored += 1
    return {"ok": True, "mirrored": mirrored, "mac_dir": str(MAC_CYCLE_DIR)}


def observer_html(*, limit: int = 10) -> str:
    payload = observer_payload(limit=limit)
    head_plan = payload.get("head_plan") or {}
    last_proof = payload.get("last_proof") or {}
    ramp = payload.get("ramp") or {}

    def esc(val: Any) -> str:
        return html.escape(str(val or ""))

    def receipt_href(path: str) -> str:
        p = (path or "").strip()
        if not p:
            return ""
        if p.startswith("http"):
            return p
        if not p.startswith("/"):
            p = "/" + p
        return p

    rows = []
    for c in payload.get("cycles") or []:
        prove = c.get("prove") or {}
        ship = c.get("ship") or {}
        pack = c.get("pack") or {}
        proof = c.get("proof") or {}
        proc = pack.get("processed", proof.get("shipped", "—"))
        adv = pack.get("advanced", proof.get("shipped", "—"))
        span = ""
        if proof.get("head_start") and proof.get("head_now"):
            span = f"{proof.get('head_start')}→{proof.get('head_now')}"
        rows.append(
            f"<tr><td>{esc(c.get('at',''))}</td><td>{esc(c.get('trigger_source',''))}</td>"
            f"<td>{esc(proc)}/{esc(pack.get('max_advance','100'))}</td><td>{esc(adv)}</td>"
            f"<td>{esc(span)}</td>"
            f"<td class=\"{'pass' if prove.get('ok') else 'fail'}\">{'PASS' if prove.get('ok') else 'FAIL'}</td>"
            f"<td class=\"{'pass' if ship.get('ok') else 'fail'}\">{'PASS' if ship.get('ok') else 'FAIL'}</td>"
            f"<td class=\"{'pass' if c.get('verdict')=='approved' else 'halt'}\">{esc(c.get('verdict',''))}</td></tr>"
        )
    body_rows = "\n".join(rows) or "<tr><td colspan=8>No cycles yet</td></tr>"

    snippet_lines = "".join(
        f"<li>{esc(s)}</li>" for s in (last_proof.get("evidence_snippets") or [])
    )
    if not snippet_lines:
        snippet_lines = "<li class=muted>No evidence snippets in last approved cycle yet</li>"

    tail_rows = "".join(
        f"<tr><td>{esc(r.get('plan_id'))}</td><td class={'pass' if r.get('ok') else 'fail'}>"
        f"{'PASS' if r.get('ok') else 'FAIL'}</td></tr>"
        for r in (last_proof.get("pack_results_tail") or [])
    )
    if not tail_rows:
        tail_rows = "<tr><td colspan=2 class=muted>—</td></tr>"

    pipeline = last_proof.get("pipeline") or ["PLAN", "BUILD", "VALIDATE", "RECEIPT"]
    recipe_steps = " → ".join(str(s) for s in pipeline)
    artifact_href = receipt_href(str(last_proof.get("artifact_path") or ""))
    dispatch_href = receipt_href(str(last_proof.get("dispatch_receipt_url") or ""))
    links = []
    if dispatch_href:
        links.append(f'<a href="{esc(dispatch_href)}">dispatch receipt</a>')
    if artifact_href:
        links.append(f'<a href="{esc(artifact_href)}">forge artifact</a>')
    if last_proof.get("source_url"):
        links.append(f'<a href="{esc(last_proof.get("source_url"))}" rel=noreferrer>source URL</a>')
    link_line = " · ".join(links) if links else '<span class=muted>receipt links appear after first approved SHIP</span>'

    return f"""<!DOCTYPE html>
<html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>SourceA · Cloud Forge Run observer</title>
<style>
body{{font-family:system-ui;background:#0b1220;color:#e8eef8;margin:0;padding:16px;line-height:1.45}}
.card{{max-width:920px;margin:0 auto;background:#141e33;border:1px solid #243352;border-radius:12px;padding:20px;margin-bottom:14px}}
h1{{font-size:1.25rem;margin:0 0 4px}} h2{{font-size:.95rem;margin:18px 0 8px;color:#b8c9e6}}
.muted{{color:#8fa3bf;font-size:.85rem}} .label{{color:#8fa3bf;font-size:.75rem;text-transform:uppercase;letter-spacing:.04em}}
table{{width:100%;border-collapse:collapse;margin-top:10px;font-size:.8rem}}
th,td{{padding:8px;border-bottom:1px solid #243352;text-align:left;vertical-align:top}}
.pass{{color:#3dd68c}} .fail,.halt{{color:#f87171}}
.now-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}}
@media(max-width:700px){{.now-grid{{grid-template-columns:1fr}}}}
.box{{background:#0f1729;border:1px solid #243352;border-radius:8px;padding:12px}}
.recipe{{font-family:ui-monospace,Menlo,monospace;font-size:.78rem;white-space:pre-wrap;word-break:break-word}}
ul.evidence{{margin:8px 0 0;padding-left:18px;font-size:.8rem}}
a{{color:#7dd3fc}}
</style></head><body>
<main class=card>
<h1>Cloud Forge Run observer</h1>
<p class=muted>head <strong>{esc(payload.get('queue_head','—'))}</strong> · ramp {esc(ramp.get('consecutive_green',0))}/10 · {esc(payload.get('at'))}</p>

<h2>Now — active plan &amp; recipe</h2>
<div class=now-grid>
  <div class=box>
    <div class=label>Plan / task</div>
    <div><strong>{esc(head_plan.get('plan_id') or payload.get('queue_head'))}</strong></div>
    <div>{esc(head_plan.get('maps_registry'))} · {esc(head_plan.get(''))} · {esc(head_plan.get('tier'))}</div>
    <div class=muted style="margin-top:6px">{esc(head_plan.get('title'))}</div>
  </div>
  <div class=box>
    <div class=label>Batch</div>
    <div>batch {esc(head_plan.get('batch_id'))} · stack {esc(head_plan.get('stack'))}</div>
    <div class=label style="margin-top:10px">Recipe (pipeline)</div>
    <div class=recipe>{esc(' → '.join(head_plan.get('recipe_pipeline') or []))}</div>
  </div>
</div>
<div class=box style="margin-top:12px">
  <div class=label>cloud_action — what this row must do</div>
  <div class=recipe>{esc(head_plan.get('cloud_action') or '—')}</div>
</div>

<h2>Last approved turn — proof &amp; evidence</h2>
<div class=now-grid>
  <div class=box>
    <div class=label>Range shipped</div>
    <div><strong>{esc(last_proof.get('head_start'))}</strong> → <strong>{esc(last_proof.get('head_now'))}</strong></div>
    <div class=muted>batch {esc(last_proof.get('batch_id'))} · {esc(last_proof.get('shipped'))} shipped · {esc(last_proof.get('skipped',0))} skipped</div>
    <div class=label style="margin-top:10px">Last task closed</div>
    <div><strong>{esc(last_proof.get('plan_id'))}</strong> · {esc(last_proof.get('maps_registry'))}</div>
    <div class=muted>{esc(last_proof.get('title'))}</div>
    <div style="margin-top:8px">{link_line}</div>
  </div>
  <div class=box>
    <div class=label>Recipe executed</div>
    <div class=recipe>{esc(recipe_steps)} · {esc(last_proof.get('validator_result'))}</div>
    <div class=label style="margin-top:10px">cloud_action</div>
    <div class=recipe>{esc(last_proof.get('cloud_action') or '—')}</div>
  </div>
</div>
<div class=box style="margin-top:12px">
  <div class=label>Evidence snippets (from  page fetch)</div>
  <ul class=evidence>{snippet_lines}</ul>
</div>
<div class=box style="margin-top:12px">
  <div class=label>Last 5 tasks in that turn</div>
  <table><thead><tr><th>Plan ID</th><th>Status</th></tr></thead><tbody>{tail_rows}</tbody></table>
</div>

<h2>Turn history</h2>
<table><thead><tr><th>At</th><th>Trigger</th><th>Processed</th><th>Shipped</th><th>Range</th><th>PROVE</th><th>SHIP</th><th>Verdict</th></tr></thead>
<tbody>{body_rows}</tbody></table>
<p class=muted style="margin-top:14px">JSON API: same URL with <code>Accept: application/json</code> · Queue: <a href="/api/cloud-forge-run/queue/v1">/api/cloud-forge-run/queue/v1</a></p>
</main></body></html>"""
