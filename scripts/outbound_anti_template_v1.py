#!/usr/bin/env python3
"""U071–U080 — anti-template diversity fleet checks (OQG hard fail + fingerprint).

Law: data/outbound-factory-salvage-spec-v1.json · wave W4
Receipt: ~/.sina/outbound-anti-template-receipt-v1.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
OUTBOUND = SINA / "outbound"
COMPILE_DIR = ROOT / "data" / "icp-compile"
RECEIPT = SINA / "outbound-anti-template-receipt-v1.json"
ASSETS = ROOT / "data" / "w3-receiver-interest-assets-v1.json"
SALVAGE = ROOT / "data" / "outbound-factory-salvage-spec-v1.json"

COMMERCIAL_ACCOUNTS = ("fundmore", "ocree", "sourcea-factory")
NF_ACCOUNTS = ("fundmore", "ocree")

PATTERN_CONVERGENCE_RE = re.compile(r"one pattern keeps appearing", re.I)
ALL_CAPS_SUBJECT_RE = re.compile(r"^[A-Z0-9\s\-—–:!?]+$")
GENERIC_AFTER_ERASER_RE = re.compile(
    r"\b(teams using ai|helping teams|our platform|quick question|partnership)\b",
    re.I,
)
REPLAY_ONLY_RE = re.compile(r"five[- ]minute replay", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _compile_stub(account_id: str) -> dict:
    for name in (f"{account_id}-v1.json", f"{account_id}.json"):
        row = _read_json(COMPILE_DIR / name)
        if row:
            return row
    return {}


def _pack_row(account_id: str) -> dict:
    pack_dir = OUTBOUND / f"w3-canada-{account_id}"
    pack = _read_json(pack_dir / "pack.json")
    body = ""
    body_path = pack_dir / "body.txt"
    if body_path.is_file():
        body = body_path.read_text(encoding="utf-8")
    elif pack.get("approved_body_path"):
        ap = ROOT / str(pack["approved_body_path"])
        if ap.is_file():
            body = ap.read_text(encoding="utf-8")
    subject = pack.get("subject") or ""
    sub_path = pack_dir / "subject.txt"
    if sub_path.is_file() and not subject:
        subject = sub_path.read_text(encoding="utf-8").strip()
    return {
        "account_id": account_id,
        "pack": pack,
        "pack_dir": pack_dir,
        "body": body.strip(),
        "subject": str(subject).strip(),
        "stub": _compile_stub(account_id),
    }


def _fleet_rows() -> list[dict]:
    return [_pack_row(aid) for aid in COMMERCIAL_ACCOUNTS]


def _first_sentence(text: str) -> str:
    chunk = re.split(r"[.!?]\s", (text or "").strip(), maxsplit=1)[0]
    return chunk.strip()


def _opening_bigram(text: str) -> str:
    words = re.findall(r"[A-Za-z']+", (text or "").lower())
    if len(words) < 2:
        return ""
    return f"{words[0]} {words[1]}"


def _last_question(text: str) -> str:
    qs = [ln.strip() for ln in (text or "").splitlines() if ln.strip().endswith("?")]
    return qs[-1].lower() if qs else ""


def check_u071_pattern_skeleton(*, text: str = "") -> dict:
    """U071 — Gemini/GPT convergence phrase hard-fails via OQG."""
    sys.path.insert(0, str(SCRIPTS))
    from best_loop_oqg_score_v1 import GENERIC_SKELETON_RE, check_generic_skeleton  # noqa: WPS433

    bad = text or "One pattern keeps appearing when teams adopt AI copilots."
    good = "Fundmore's board asked what the copilot actually did six months later."
    bad_row = check_generic_skeleton(bad)
    good_row = check_generic_skeleton(good)
    wired = bool(PATTERN_CONVERGENCE_RE.search(GENERIC_SKELETON_RE.pattern))
    ok = wired and bad_row.get("hard_fail") and good_row.get("ok")
    return {
        "ok": ok,
        "upgrade": "U071",
        "wired": wired,
        "bad_hard_fail": bad_row.get("hard_fail"),
        "good_ok": good_row.get("ok"),
        "acceptance": "Gemini/GPT convergence blocked",
        "check": "python3 scripts/outbound_anti_template_v1.py --check-u071 --json",
    }


def check_u072_bigram_diversity() -> dict:
    """U072 — same opening bigram on 2+ accounts = alert."""
    rows = _fleet_rows()
    bigrams: dict[str, list[str]] = {}
    for row in rows:
        bg = _opening_bigram(row["body"])
        if not bg:
            continue
        bigrams.setdefault(bg, []).append(row["account_id"])
    dupes = {k: v for k, v in bigrams.items() if len(v) >= 2}
    alerts = [{"bigram": k, "accounts": v} for k, v in dupes.items()]
    ok = len(dupes) == 0 and len(bigrams) >= 2
    return {
        "ok": ok,
        "upgrade": "U072",
        "bigrams": bigrams,
        "alerts": alerts,
        "acceptance": "Same opener 2+ accounts = alert",
        "check": "python3 scripts/outbound_anti_template_v1.py --check-u072 --json",
    }


def check_u073_tension_uniqueness() -> dict:
    """U073 — same tension_kernel twice = warn."""
    kernels: dict[str, list[str]] = {}
    for aid in COMMERCIAL_ACCOUNTS:
        tk = str(_compile_stub(aid).get("tension_kernel") or "").strip().lower()
        if tk:
            kernels.setdefault(tk, []).append(aid)
    dupes = {k: v for k, v in kernels.items() if len(v) >= 2}
    ok = len(kernels) >= 2 and len(dupes) == 0
    return {
        "ok": ok,
        "upgrade": "U073",
        "kernels": kernels,
        "dupes": dupes,
        "acceptance": "Same tension_kernel twice = warn",
        "check": "python3 scripts/outbound_anti_template_v1.py --check-u073 --json",
    }


def check_u074_subject_case() -> dict:
    """U074 — ALL CAPS subject fail."""
    checks: list[dict] = []
    for row in _fleet_rows():
        sub = row["subject"]
        if not sub:
            checks.append({"account_id": row["account_id"], "ok": True, "skipped": True})
            continue
        all_caps = bool(ALL_CAPS_SUBJECT_RE.match(sub) and re.search(r"[A-Z]", sub))
        checks.append({"account_id": row["account_id"], "ok": not all_caps, "subject": sub[:60]})
    ok = all(c.get("ok") for c in checks)
    return {
        "ok": ok,
        "upgrade": "U074",
        "accounts": checks,
        "acceptance": "ALL CAPS subject fail",
        "check": "python3 scripts/outbound_anti_template_v1.py --check-u074 --json",
    }


def check_u075_curiosity_dedupe() -> dict:
    """U075 — duplicate curiosity question flagged."""
    questions: dict[str, list[str]] = {}
    for row in _fleet_rows():
        q = _last_question(row["body"])
        if not q:
            continue
        questions.setdefault(q, []).append(row["account_id"])
    dupes = {k: v for k, v in questions.items() if len(v) >= 2}
    ok = len(questions) >= 2 and len(dupes) == 0
    return {
        "ok": ok,
        "upgrade": "U075",
        "questions": questions,
        "dupes": dupes,
        "acceptance": "Duplicate question flagged",
        "check": "python3 scripts/outbound_anti_template_v1.py --check-u075 --json",
    }


def check_u076_brand_voice() -> dict:
    """U076 — NF accounts must not share identical first-sentence structure."""
    nf = [_pack_row(a) for a in NF_ACCOUNTS if _pack_row(a).get("body")]
    structures = [_first_sentence(r["body"]).lower() for r in nf]
    same = len(structures) >= 2 and structures[0] == structures[1]
    ok = len(nf) >= 2 and not same
    return {
        "ok": ok,
        "upgrade": "U076",
        "first_sentences": {r["account_id"]: _first_sentence(r["body"])[:80] for r in nf},
        "acceptance": "Same first sentence structure fail",
        "check": "python3 scripts/outbound_anti_template_v1.py --check-u076 --json",
    }


def check_u077_interest_asset_rotation() -> dict:
    """U077 — preview promise not always five-minute replay."""
    cfg = _read_json(ASSETS)
    labels: list[str] = []
    for aid in COMMERCIAL_ACCOUNTS:
        row = (cfg.get("accounts") or {}).get(aid) or {}
        labels.append(str(row.get("preview_promise") or row.get("interest_label") or ""))
    replay_only = all(REPLAY_ONLY_RE.search(lb or "") for lb in labels if lb)
    ok = len([x for x in labels if x.strip()]) >= 2 and not replay_only
    return {
        "ok": ok,
        "upgrade": "U077",
        "labels": labels,
        "acceptance": "Not always five-minute replay",
        "check": "python3 scripts/outbound_anti_template_v1.py --check-u077 --json",
    }


def check_u078_role_angle() -> dict:
    """U078 — different executive roles must not share identical bodies."""
    rows = _fleet_rows()
    bodies = {r["account_id"]: r["body"] for r in rows if r["body"]}
    angles = {
        r["account_id"]: str((r["stub"].get("icp_profile") or {}).get("role_angle") or r["stub"].get("angle") or "")
        for r in rows
    }
    dup_body = len(set(bodies.values())) < len(bodies) if len(bodies) >= 2 else False
    nf_angles = [angles.get(a, "") for a in NF_ACCOUNTS if angles.get(a)]
    angles_unique = len(set(a.lower() for a in nf_angles)) == len(nf_angles) if len(nf_angles) >= 2 else True
    checks = [
        {
            "account_id": aid,
            "ok": bool(bodies.get(aid)) and angles.get(aid),
            "role_angle": angles.get(aid, "")[:60],
        }
        for aid in COMMERCIAL_ACCOUNTS
    ]
    ok = not dup_body and angles_unique and all(c.get("ok") for c in checks)
    return {
        "ok": ok,
        "upgrade": "U078",
        "accounts": checks,
        "duplicate_body": dup_body,
        "angles_unique": angles_unique,
        "acceptance": "CEO vs CCO same body fail",
        "check": "python3 scripts/outbound_anti_template_v1.py --check-u078 --json",
    }


def check_u079_ai_eraser() -> dict:
    """U079 — delete company name; generic skeleton = fail."""
    checks: list[dict] = []
    for row in _fleet_rows():
        body = row["body"]
        company = str(row["pack"].get("company") or row["stub"].get("company") or "")
        erased = body
        for token in re.findall(r"\w+", company):
            if len(token) >= 4:
                erased = re.sub(re.escape(token), "", erased, flags=re.I)
        generic = bool(GENERIC_AFTER_ERASER_RE.search(erased))
        checks.append({"account_id": row["account_id"], "ok": not generic, "generic_hit": generic})
    ok = all(c.get("ok") for c in checks if not c.get("skipped"))
    return {
        "ok": ok,
        "upgrade": "U079",
        "accounts": checks,
        "acceptance": "Generic after delete = fail",
        "check": "python3 scripts/outbound_anti_template_v1.py --check-u079 --json",
    }


def _body_hash(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


def ensure_body_hashes(*, write: bool = True) -> dict:
    """U080 — stamp body_hash on approved packs when missing."""
    stamped: list[str] = []
    for aid in COMMERCIAL_ACCOUNTS:
        row = _pack_row(aid)
        body = row["body"]
        if not body:
            continue
        pack_path = row["pack_dir"] / "pack.json"
        pack = dict(row["pack"] or {"schema": "w3-canada-outbound-send-pack-v1", "account_id": aid})
        h = _body_hash(body)
        if pack.get("body_hash") != h:
            pack["body_hash"] = h
            pack["body_hash_at"] = _now()
            if write:
                row["pack_dir"].mkdir(parents=True, exist_ok=True)
                pack_path.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
            stamped.append(aid)
    return {"ok": True, "stamped": stamped}


def check_u080_body_hash() -> dict:
    """U080 — rewrite changes hash · hash present on packs."""
    ensure_body_hashes(write=True)
    rows = _fleet_rows()
    checks: list[dict] = []
    for row in rows:
        body = row["body"]
        pack = _read_json(row["pack_dir"] / "pack.json")
        h = pack.get("body_hash")
        expected = _body_hash(body) if body else None
        rewrite_ok = h == expected if body else False
        mutated = _body_hash(body + " x") if body else None
        checks.append(
            {
                "account_id": row["account_id"],
                "ok": bool(h) and rewrite_ok and mutated != h,
                "body_hash": h,
            }
        )
    ok = all(c.get("ok") for c in checks)
    return {
        "ok": ok,
        "upgrade": "U080",
        "accounts": checks,
        "acceptance": "Rewrite changes hash",
        "check": "python3 scripts/outbound_anti_template_v1.py --check-u080 --json",
    }


def build_template_fingerprint() -> dict:
    """Fleet template fingerprint for OQG receipt (U072/U080)."""
    rows = _fleet_rows()
    openers = [_opening_bigram(r["body"]) for r in rows if r["body"]]
    hashes = []
    for row in rows:
        pack = _read_json(row["pack_dir"] / "pack.json")
        if pack.get("body_hash"):
            hashes.append(pack["body_hash"])
    fleet_hash = hashlib.sha256("|".join(sorted(hashes)).encode()).hexdigest()[:12] if hashes else None
    bigram_counts = Counter(openers)
    return {
        "schema": "outbound-template-fingerprint-v1",
        "at": _now(),
        "opening_bigrams": dict(bigram_counts),
        "body_hashes": hashes,
        "fleet_hash": fleet_hash,
        "duplicate_bigram_alerts": [
            {"bigram": k, "count": v} for k, v in bigram_counts.items() if v >= 2
        ],
    }


CHECKS = {
    "U071": check_u071_pattern_skeleton,
    "U072": check_u072_bigram_diversity,
    "U073": check_u073_tension_uniqueness,
    "U074": check_u074_subject_case,
    "U075": check_u075_curiosity_dedupe,
    "U076": check_u076_brand_voice,
    "U077": check_u077_interest_asset_rotation,
    "U078": check_u078_role_angle,
    "U079": check_u079_ai_eraser,
    "U080": check_u080_body_hash,
}


def run_all_checks(*, write_receipt: bool = True) -> dict:
    results = {uid: fn() for uid, fn in CHECKS.items()}
    fp = build_template_fingerprint()
    ok = all(r.get("ok") for r in results.values())
    row = {
        "schema": "outbound-anti-template-receipt-v1",
        "at": _now(),
        "ok": ok,
        "salvage_spec": str(SALVAGE.relative_to(ROOT)),
        "checks": results,
        "template_fingerprint": fp,
        "line": f"anti-template · {sum(1 for r in results.values() if r.get('ok'))}/{len(results)} PASS",
    }
    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Outbound anti-template fleet checks U071–U080")
    for uid in CHECKS:
        ap.add_argument(f"--check-{uid.lower()}", action="store_true")
    ap.add_argument("--check-all", action="store_true")
    ap.add_argument("--fingerprint", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.fingerprint:
        row = build_template_fingerprint()
    elif args.check_all:
        row = run_all_checks()
    else:
        picked = None
        for uid in CHECKS:
            if getattr(args, f"check_{uid.lower()}", False):
                picked = CHECKS[uid]()
                break
        if picked is None:
            row = run_all_checks()
        else:
            row = picked

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or f"ok={row.get('ok')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
