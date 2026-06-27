#!/usr/bin/env python3
"""Evaluate live Brain chat against canonical question buckets."""
from __future__ import annotations

import argparse
import json
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_PATH = ROOT / "data" / "brain-chat-eval-canonical-v1.json"
CONFIG_PATH = ROOT / "SourceA-landing" / "green-unified" / "data" / "sourcea-brain-chat-config-v1.json"
REPORT_PATH = ROOT / "reports" / "chat_eval_last_run.json"


def load_worker_url() -> str:
    if CONFIG_PATH.exists():
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        url = cfg.get("api_worker_url", "")
        if url:
            return url
    raise SystemExit("FAIL: no api_worker_url in brain chat config")


def post_chat(url: str, message: str) -> dict:
    body = json.dumps({"message": message}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=45, context=ctx) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": str(e), "reply": e.read().decode(errors="replace")[:500]}
    except Exception as e:
        return {"ok": False, "error": str(e), "reply": ""}


def score_question(q: dict, reply: str, ok: bool) -> dict:
    r = reply.lower()
    failures: list[str] = []
    if not ok:
        failures.append("chat_not_ok")
    for phrase in q.get("required_all", []):
        if phrase.lower() not in r:
            failures.append(f"missing_required:{phrase}")
    req_any = q.get("required_any", [])
    if req_any and not any(p.lower() in r for p in req_any):
        failures.append(f"missing_any_of:{req_any}")
    for phrase in q.get("forbidden_any", []):
        if phrase.lower() in r:
            failures.append(f"forbidden:{phrase}")
    fp = q.get("forbidden_first_phrase")
    fps = fp if isinstance(fp, list) else ([fp] if fp else [])
    for phrase in fps:
        if r.strip().startswith(str(phrase).lower()):
            failures.append(f"forbidden_lead:{phrase}")
            break
    if q.get("must_not_lead_price") and any(x in r[:120] for x in ["$1", "$2", "$3", "1500", "5000"]):
        failures.append("price_too_early")
    if q.get("must_not_refuse") and any(x in r for x in ["i can't help", "i cannot help", "outside my"]):
        failures.append("wrong_refusal")
    return {"id": q["id"], "pass": not failures, "failures": failures, "reply_preview": reply[:200]}


def run_bucket(name: str, bucket: dict, url: str) -> dict:
    results = []
    for q in bucket.get("questions", []):
        resp = post_chat(url, q["message"])
        reply = (resp.get("reply") or "").strip()
        results.append(score_question(q, reply, bool(resp.get("ok"))))
    passed = sum(1 for r in results if r["pass"])
    total = len(results) or 1
    score = passed / total
    threshold = bucket.get("pass_threshold", 0.9)
    return {
        "bucket": name,
        "score": round(score, 3),
        "pass_threshold": threshold,
        "pass": score >= threshold,
        "passed": passed,
        "total": total,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--bucket", help="Run single bucket only")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--url", default="")
    args = parser.parse_args()

    eval_data = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    url = args.url or load_worker_url()
    buckets = eval_data.get("buckets", {})
    if args.bucket:
        buckets = {args.bucket: buckets[args.bucket]} if args.bucket in buckets else {}

    report = {
        "schema": "sourcea-brain-chat-eval-report-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "worker_url": url,
        "buckets": [],
        "ok": True,
    }
    for name, bucket in buckets.items():
        row = run_bucket(name, bucket, url)
        report["buckets"].append(row)
        if name.startswith("p0") and not row["pass"]:
            report["ok"] = False

    if args.write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for b in report["buckets"]:
            status = "PASS" if b["pass"] else "FAIL"
            print(f"{b['bucket']}: {status} ({b['passed']}/{b['total']} = {b['score']})")
        print(f"overall: {'PASS' if report['ok'] else 'FAIL'}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
