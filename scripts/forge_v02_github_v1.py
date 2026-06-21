#!/usr/bin/env python3
"""Forge-v0.2 — GitHub fetch + adapter in front of unchanged Forge-v0.1 pipeline.

Architecture A: cloud-only plan ingest via GitHub API (read-only).
Stages 0a fetch → 0b inspect/adapt → 0c data health → v0.1 validate→dedup→score→rank→route.

Artifacts written to cloud receipts volume (/app/receipts/forge_v0.2/) — not Mac disk.
"""
from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "forge-github-source-v02.json"
SCORING_PATH = ROOT / "data" / "forge-scoring-ssot-v01.json"
OUTPUT_DIR_NAME = "forge_v0.2"

FORGE_REQUIRED_FIELDS = (
    "id",
    "schema_version",
    "destination_repo",
    "inputs",
    "outputs",
    "validation_rule",
)
FORGE_METADATA_FIELDS = (
    "metadata.core_capability",
    "metadata.client_problem_id",
)
FULL_SCHEMA_FIELDS = FORGE_REQUIRED_FIELDS + FORGE_METADATA_FIELDS

# Candidate source keys per forge field (first match wins during inspect).
FIELD_CANDIDATES: dict[str, tuple[str, ...]] = {
    "id": ("id", "plan_id", "planId", "n", "slug"),
    "schema_version": ("schema_version", "schemaVersion", "version", "schema"),
    "destination_repo": (
        "destination_repo",
        "destinationRepo",
        "target",
        "target_repo",
        "repo",
    ),
    "inputs": ("inputs", "input", "params", "parameters"),
    "outputs": ("outputs", "output", "deliverables", "artifacts"),
    "validation_rule": (
        "validation_rule",
        "validationRule",
        "validation",
        "verify_rule",
        "validation_rule_id",
    ),
    "metadata.core_capability": (
        "metadata.core_capability",
        "core_capability",
        "coreCapability",
        "capability",
    ),
    "metadata.client_problem_id": (
        "metadata.client_problem_id",
        "client_problem_id",
        "client_problem",
        "clientProblem",
        "problem_id",
    ),
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def load_github_config() -> dict[str, Any]:
    cfg = _read_json(CONFIG_PATH)
    env_map = cfg.get("env_overrides") or {}
    out = dict(cfg)
    out["owner"] = os.environ.get(str(env_map.get("owner") or "FORGE_GITHUB_OWNER"), cfg.get("owner", ""))
    out["repo"] = os.environ.get(str(env_map.get("repo") or "FORGE_GITHUB_REPO"), cfg.get("repo", ""))
    out["plans_path"] = os.environ.get(
        str(env_map.get("plans_path") or "FORGE_GITHUB_PLANS_PATH"), cfg.get("plans_path", "plans")
    ).strip("/")
    out["ref"] = os.environ.get(str(env_map.get("ref") or "FORGE_GITHUB_REF"), cfg.get("ref", "main"))
    out["token"] = (
        os.environ.get(str(env_map.get("token") or "GITHUB_TOKEN"), "").strip()
        or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
    )
    out["destination_repo_default"] = cfg.get("destination_repo_default") or "sourcea/fbe-cloud-worker"
    return out


def _github_request(url: str, token: str = "") -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "sourcea-forge-v0.2",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"github_api_{exc.code}: {body}") from exc


def _flatten_keys(obj: Any, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            keys.add(path)
            keys.update(_flatten_keys(v, path))
    elif isinstance(obj, list) and obj:
        keys.update(_flatten_keys(obj[0], prefix))
    return keys


def _get_nested(obj: dict[str, Any], dotted: str) -> Any:
    if "." not in dotted:
        return obj.get(dotted)
    head, tail = dotted.split(".", 1)
    sub = obj.get(head)
    if not isinstance(sub, dict):
        return None
    return _get_nested(sub, tail)


def _set_nested(obj: dict[str, Any], dotted: str, value: Any) -> None:
    if "." not in dotted:
        obj[dotted] = value
        return
    head, tail = dotted.split(".", 1)
    sub = obj.setdefault(head, {})
    if not isinstance(sub, dict):
        return
    _set_nested(sub, tail, value)


def stage_0a_fetch_github_plans(
    *,
    owner: str,
    repo: str,
    plans_path: str,
    ref: str,
    token: str = "",
) -> list[dict[str, Any]]:
    """Fetch every plan file under plans_path via GitHub Contents API (read-only)."""
    if not owner or not repo:
        raise ValueError("FORGE_GITHUB_OWNER and FORGE_GITHUB_REPO required")

    collected: list[dict[str, Any]] = []

    def walk(path: str) -> None:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}"
        payload = _github_request(url, token)
        if isinstance(payload, dict):
            entries = [payload]
        else:
            entries = list(payload)

        for entry in entries:
            etype = str(entry.get("type") or "")
            if etype == "dir":
                walk(str(entry.get("path") or ""))
                continue
            if etype != "file":
                continue
            name = str(entry.get("name") or "")
            lower = name.lower()
            if not (lower.endswith(".json") or lower.endswith(".md") or lower.endswith(".yaml") or lower.endswith(".yml")):
                continue
            download_url = str(entry.get("download_url") or "")
            raw_text = ""
            if download_url:
                req = urllib.request.Request(
                    download_url,
                    headers={"User-Agent": "sourcea-forge-v0.2"},
                    method="GET",
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    raw_text = resp.read().decode("utf-8", errors="replace")
            elif entry.get("content"):
                raw_text = base64.b64decode(str(entry["content"])).decode("utf-8", errors="replace")
            else:
                file_url = str(entry.get("url") or "")
                if file_url:
                    detail = _github_request(file_url, token)
                    if detail.get("content"):
                        raw_text = base64.b64decode(str(detail["content"])).decode("utf-8", errors="replace")

            parsed: dict[str, Any] | None = None
            if lower.endswith(".json"):
                try:
                    row = json.loads(raw_text)
                    parsed = row if isinstance(row, dict) else {"value": row}
                except json.JSONDecodeError:
                    parsed = None
            elif lower.endswith((".yaml", ".yml")):
                parsed = _parse_yaml_minimal(raw_text)
            elif lower.endswith(".md"):
                parsed = _parse_markdown_plan(raw_text, fallback_id=Path(name).stem)

            collected.append(
                {
                    "github_path": str(entry.get("path") or name),
                    "sha": str(entry.get("sha") or ""),
                    "raw_text": raw_text,
                    "parsed": parsed,
                }
            )

    walk(plans_path.strip("/"))
    return collected


def _parse_yaml_minimal(text: str) -> dict[str, Any] | None:
    try:
        import yaml  # type: ignore

        row = yaml.safe_load(text)
        return row if isinstance(row, dict) else None
    except Exception:
        return None


def _parse_markdown_plan(text: str, *, fallback_id: str) -> dict[str, Any]:
    """Best-effort markdown extract — never invents required forge fields."""
    out: dict[str, Any] = {"plan_id": fallback_id, "format": "markdown"}
    m = re.search(r"^#\s+([^\n—]+)", text, re.MULTILINE)
    if m:
        out["title"] = m.group(1).strip()
    tier = re.search(r"\*\*Tier:\*\*\s*(\S+)", text)
    if tier:
        out.setdefault("metadata", {})["tier"] = tier.group(1)
    ws = re.search(r"\*\*Workstream:\*\*\s*(\S+)", text)
    if ws:
        out.setdefault("metadata", {})["workstream"] = ws.group(1)
    comp = re.search(r"\*\*Competitor row:\*\*\s*(\d+)", text) or re.search(
        r"Company \| (\S+)", text
    )
    if comp:
        out.setdefault("metadata", {})["competitor_hint"] = comp.group(1)
    task = re.search(r"## Task[^\n]*\n\n([^\n#]+)", text, re.DOTALL)
    if task:
        out["inputs"] = {"action": task.group(1).strip()[:500]}
    return out


def stage_0b_inspect_and_build_adapter(
    fetched: list[dict[str, Any]],
    *,
    sample_size: int = 5,
    destination_default: str,
) -> dict[str, Any]:
    """Inspect sample files; build field mapping from actual keys seen."""
    samples = [f for f in fetched if isinstance(f.get("parsed"), dict)][:sample_size]
    observed: set[str] = set()
    for row in samples:
        observed.update(_flatten_keys(row["parsed"]))

    mapping: dict[str, str | None] = {}
    for forge_field, candidates in FIELD_CANDIDATES.items():
        chosen: str | None = None
        for cand in candidates:
            if cand in observed or any(k.endswith(f".{cand}") or k == cand for k in observed):
                # Prefer exact top-level match
                if cand in observed:
                    chosen = cand
                    break
                for k in observed:
                    if k == cand or k.endswith(f".{cand}"):
                        chosen = k
                        break
                if chosen:
                    break
        mapping[forge_field] = chosen

    mapping_record = {
        "schema": "forge-v0.2-adapter-mapping",
        "at": _now(),
        "sample_size": len(samples),
        "sample_paths": [s.get("github_path") for s in samples],
        "observed_keys": sorted(observed)[:200],
        "field_mapping": mapping,
        "destination_repo_default": destination_default,
        "note": "Maps real GitHub plan fields onto Forge schema. Missing sources stay absent — never invented.",
    }
    return mapping_record


def _resolve_source_value(parsed: dict[str, Any], source_key: str | None) -> Any:
    if not source_key:
        return None
    if "." in source_key:
        return _get_nested(parsed, source_key)
    return parsed.get(source_key)


def adapt_plan(
    parsed: dict[str, Any],
    mapping: dict[str, str | None],
    *,
    destination_default: str,
    github_path: str,
) -> tuple[dict[str, Any], list[str], list[str]]:
    """Return (blueprint_partial, missing_required, missing_metadata). Never invent values."""
    blueprint: dict[str, Any] = {
        "_source_path": github_path,
        "_adapter": "forge-v0.2",
    }
    missing_required: list[str] = []
    missing_metadata: list[str] = []

    for field in FORGE_REQUIRED_FIELDS:
        src = mapping.get(field)
        val = _resolve_source_value(parsed, src)

        if field == "destination_repo":
            if val is not None and str(val).strip():
                blueprint["destination_repo"] = str(val).strip()
            elif destination_default:
                blueprint["destination_repo"] = destination_default
            else:
                missing_required.append(field)
        elif field in ("inputs", "outputs"):
            if val is not None and isinstance(val, (dict, list)):
                blueprint[field] = val
            else:
                missing_required.append(field)
        elif val is None or (isinstance(val, str) and not str(val).strip()):
            missing_required.append(field)
        elif field == "id":
            blueprint["id"] = str(val)
        elif field == "schema_version":
            blueprint["schema_version"] = str(val)
        elif field == "validation_rule":
            blueprint["validation_rule"] = str(val)
        else:
            blueprint[field] = val

    meta: dict[str, Any] = {}
    for field in FORGE_METADATA_FIELDS:
        src = mapping.get(field)
        val = _resolve_source_value(parsed, src)
        short = field.split(".", 1)[1]
        if val is None or (isinstance(val, str) and not str(val).strip()):
            missing_metadata.append(field)
        else:
            meta[short] = val
    if meta:
        blueprint["metadata"] = meta

    # Promote metadata to v0.1 top-level scoring fields when present (no invention)
    if meta.get("core_capability"):
        blueprint["core_capability"] = meta["core_capability"]
    if meta.get("client_problem_id"):
        blueprint["client_problem"] = meta["client_problem_id"]

    return blueprint, missing_required, missing_metadata


def stage_0c_data_health_report(
    *,
    total_real: int,
    adapted_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    missing_counter: Counter[str] = Counter()
    mapped_clean = 0
    for row in adapted_rows:
        miss_req = list(row.get("missing_required") or [])
        miss_meta = list(row.get("missing_metadata") or [])
        if not miss_req and not miss_meta and row.get("blueprint") and not row.get("parse_error"):
            mapped_clean += 1
        for f in miss_req:
            missing_counter[f] += 1
        for f in miss_meta:
            missing_counter[f] += 1

    top_missing = missing_counter.most_common(5)
    return {
        "schema": "forge-v0.2-data-health",
        "at": _now(),
        "total_real_plans_found": total_real,
        "mapped_cleanly_to_full_schema": mapped_clean,
        "most_commonly_missing_fields": [
            {"field": field, "count": count} for field, count in top_missing
        ],
        "parse_failures": sum(1 for r in adapted_rows if r.get("parse_error")),
        "adapted_count": len(adapted_rows),
    }


def _one_line_reason(scored: dict[str, Any]) -> str:
    bd = scored.get("score_breakdown") or {}
    parts: list[str] = []
    if bd.get("core_capability"):
        parts.append("core capability match")
    if bd.get("client_problem"):
        parts.append("client problem match")
    if bd.get("minimal_dependencies"):
        parts.append("minimal deps")
    pat = int(bd.get("pattern_adjustment") or 0)
    if pat > 0:
        parts.append(f"pattern +{pat}")
    elif pat < 0:
        parts.append(f"pattern {pat}")
    tier = int(bd.get("tier_adjustment") or 0)
    if tier:
        parts.append(f"tier {tier:+d}")
    if bd.get("vague_keywords"):
        parts.append("vague penalty")
    if bd.get("already_implemented"):
        parts.append("already-have penalty")
    if not parts:
        parts.append(f"score {scored.get('score')}")
    inputs = scored.get("inputs") or {}
    action = inputs.get("action") if isinstance(inputs, dict) else None
    if action:
        return f"{'; '.join(parts)} — {str(action)[:80]}"
    return "; ".join(parts)


def _run_v01_pipeline(
    raw_blueprints: list[Any],
    scoring: dict[str, Any],
) -> dict[str, Any]:
    """Unchanged v0.1 stages — no 100-count gate (v0.2 uses real GitHub cardinality)."""
    from forge_v01_engine_v1 import (  # noqa: WPS433
        load_scoring_config,
        score_blueprint,
        stage_dedup,
        stage_rank,
        stage_route,
        stage_validate,
    )

    cfg = scoring or load_scoring_config()
    valid, malformed_ids = stage_validate(raw_blueprints)
    unique, duplicate_ids, already_have_ids = stage_dedup(valid, cfg)
    scored = [score_blueprint(b, cfg) for b in unique]
    ranked = stage_rank(scored)
    routed = stage_route(ranked)
    return {
        "valid": valid,
        "malformed_ids": malformed_ids,
        "duplicate_ids": duplicate_ids,
        "already_have_ids": already_have_ids,
        "unique": unique,
        "ranked": ranked,
        "routed": routed,
    }


def build_telemetry_line(
    *,
    total_real: int,
    mapped_clean: int,
    dupes: int,
    malformed: int,
    health: dict[str, Any],
) -> str:
    top = (health.get("most_commonly_missing_fields") or [{}])[0]
    field = top.get("field") or "none"
    count = top.get("count") or 0
    return (
        f"Forge v0.2: {total_real} real → {mapped_clean} mapped → {dupes} dupes → "
        f"{malformed} malformed → top 20 ranked. Most-missing field: {field} ({count})."
    )


def _fetch_plans_fixture(plans_dir: Path) -> list[dict[str, Any]]:
    """Test-only: mimic GitHub fetch from local plans/ (not used in production cloud path)."""
    collected: list[dict[str, Any]] = []
    for path in sorted(plans_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        raw_text = path.read_text(encoding="utf-8")
        try:
            parsed = json.loads(raw_text)
            if not isinstance(parsed, dict):
                parsed = None
        except json.JSONDecodeError:
            parsed = None
        collected.append(
            {
                "github_path": f"plans/{path.name}",
                "sha": "fixture",
                "raw_text": raw_text,
                "parsed": parsed,
            }
        )
    return collected


def _merge_implement_receipts(cfg: dict[str, Any], root: Path) -> dict[str, Any]:
    """Extend already-have from PASS cloud-implement receipts on cloud volume."""
    impl_dir = root / "receipts" / "cloud-implement"
    if not impl_dir.is_dir():
        return cfg
    merged = dict(cfg)
    ids = list(merged.get("already_implemented_plan_ids") or [])
    seen = set(ids)
    for path in impl_dir.glob("*.json"):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if row.get("status") != "PASS" and row.get("verdict") != "PASS":
            continue
        pid = str(row.get("plan_id") or path.stem)
        if pid and pid not in seen:
            ids.append(pid)
            seen.add(pid)
    merged["already_implemented_plan_ids"] = ids
    return merged


def run_forge_v02_from_github(
    *,
    root: Path | None = None,
    write_output: bool = True,
    owner: str = "",
    repo: str = "",
    plans_path: str = "",
    ref: str = "",
    token: str = "",
) -> dict[str, Any]:
    base = root or ROOT
    cfg = load_github_config()
    owner = owner or str(cfg.get("owner") or "")
    repo = repo or str(cfg.get("repo") or "")
    plans_path = plans_path or str(cfg.get("plans_path") or "plans")
    ref = ref or str(cfg.get("ref") or "main")
    token = token or str(cfg.get("token") or "")
    dest_default = str(cfg.get("destination_repo_default") or "sourcea/fbe-cloud-worker")

    # Stage 0a — Fetch (GitHub API first; bundled plans/ fallback for private repo without token)
    fixture_dir = os.environ.get("FORGE_V02_FIXTURE_DIR", "").strip()
    fetch_source = "github_api"
    if fixture_dir:
        fetched = _fetch_plans_fixture(Path(fixture_dir))
        fetch_source = "fixture"
    else:
        try:
            fetched = stage_0a_fetch_github_plans(
                owner=owner,
                repo=repo,
                plans_path=plans_path,
                ref=ref,
                token=token,
            )
        except RuntimeError as exc:
            msg = str(exc)
            bundled = base / "plans"
            if (
                msg.startswith(("github_api_404", "github_api_403"))
                and os.environ.get("FORGE_V02_BUNDLED_FALLBACK", "1") == "1"
                and bundled.is_dir()
            ):
                fetched = _fetch_plans_fixture(bundled)
                fetch_source = "bundled_fallback"
            else:
                raise

    # Stage 0b — Inspect & Adapt
    adapter = stage_0b_inspect_and_build_adapter(
        fetched,
        destination_default=dest_default,
    )
    mapping = adapter.get("field_mapping") or {}

    adapted_rows: list[dict[str, Any]] = []
    blueprints_for_pipeline: list[dict[str, Any]] = []

    for item in fetched:
        parsed = item.get("parsed")
        gh_path = str(item.get("github_path") or "")
        if not isinstance(parsed, dict):
            adapted_rows.append(
                {
                    "github_path": gh_path,
                    "parse_error": True,
                    "missing_required": list(FORGE_REQUIRED_FIELDS),
                    "missing_metadata": list(FORGE_METADATA_FIELDS),
                }
            )
            continue

        bp, miss_req, miss_meta = adapt_plan(
            parsed,
            mapping,
            destination_default=dest_default,
            github_path=gh_path,
        )
        full_missing = miss_req + [f for f in miss_meta if f not in miss_req]
        adapted_rows.append(
            {
                "github_path": gh_path,
                "missing_required": miss_req,
                "missing_metadata": miss_meta,
                "missing_fields": full_missing,
                "blueprint": bp,
            }
        )
        blueprints_for_pipeline.append(bp)

    # Stage 0c — Data Health
    health = stage_0c_data_health_report(
        total_real=len(fetched),
        adapted_rows=adapted_rows,
    )
    health["fetch_source"] = fetch_source

    # v0.1 pipeline unchanged
    from forge_v01_engine_v1 import load_scoring_config  # noqa: WPS433

    scoring = load_scoring_config(base / "data" / "forge-scoring-ssot-v01.json")
    scoring = _merge_implement_receipts(scoring, base)
    pipeline = _run_v01_pipeline(blueprints_for_pipeline, scoring)

    top_20 = []
    for row in pipeline["ranked"][:20]:
        top_20.append(
            {
                **{k: v for k, v in row.items() if not k.startswith("_")},
                "reason": _one_line_reason(row),
            }
        )

    telemetry_line = build_telemetry_line(
        total_real=len(fetched),
        mapped_clean=int(health.get("mapped_cleanly_to_full_schema") or 0),
        dupes=len(pipeline["duplicate_ids"]),
        malformed=len(pipeline["malformed_ids"]),
        health=health,
    )

    result = {
        "schema": "forge-v0.2-run",
        "at": _now(),
        "architecture": "A",
        "github": {"owner": owner, "repo": repo, "plans_path": plans_path, "ref": ref},
        "adapter": adapter,
        "data_health": health,
        "telemetry_line": telemetry_line,
        "funnel": {
            "totalReal": len(fetched),
            "mappedClean": health.get("mapped_cleanly_to_full_schema"),
            "dupesDropped": len(pipeline["duplicate_ids"]),
            "malformedDropped": len(pipeline["malformed_ids"]),
            "alreadyHaveDropped": len(pipeline["already_have_ids"]),
            "validRemaining": len(pipeline["unique"]),
        },
        "top_20": top_20,
        "routed": pipeline["routed"],
        "dropped_malformed_ids": pipeline["malformed_ids"],
        "dropped_duplicate_ids": pipeline["duplicate_ids"],
        "dropped_already_have_ids": pipeline["already_have_ids"],
        "urls": {
            "data_health": f"/receipts/{OUTPUT_DIR_NAME}/data_health.json",
            "forge_top": f"/receipts/{OUTPUT_DIR_NAME}/forge_v0.2_top.json",
        },
    }

    if write_output:
        out_dir = base / "receipts" / OUTPUT_DIR_NAME
        _write_json(out_dir / "data_health.json", health)
        _write_json(
            out_dir / "forge_v0.2_top.json",
            {
                "schema": "forge-v0.2-top",
                "at": _now(),
                "telemetry_line": telemetry_line,
                "github": result["github"],
                "funnel": result["funnel"],
                "top_20": top_20,
                "routed_summary": {k: len(v) for k, v in pipeline["routed"].items()},
            },
        )
        _write_json(out_dir / "forge_v0.2_run.json", result)

    return result


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Forge v0.2 — GitHub ingest + v0.1 pipeline")
    ap.add_argument("--owner", default="")
    ap.add_argument("--repo", default="")
    ap.add_argument("--plans-path", default="")
    ap.add_argument("--ref", default="")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        row = run_forge_v02_from_github(
            write_output=not args.no_write,
            owner=args.owner,
            repo=args.repo,
            plans_path=args.plans_path,
            ref=args.ref,
        )
    except Exception as exc:
        err = {"ok": False, "error": str(exc)}
        print(json.dumps(err, indent=2))
        return 1

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("telemetry_line"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
