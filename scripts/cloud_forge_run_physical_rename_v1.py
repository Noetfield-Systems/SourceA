#!/usr/bin/env python3
"""Physical rename: cloud-drain → cloud-forge-run · drain scripts → forge-run/auto-runtime."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# git mv: old relative path -> new relative path
FILE_RENAMES: list[tuple[str, str]] = [
    # Core scripts
    ("scripts/cloud_drain_auto_runtime_v1.py", "scripts/cloud_auto_runtime_v1.py"),
    ("scripts/hub_cloud_drain_proceed_v1.py", "scripts/hub_cloud_forge_run_proceed_v1.py"),
    ("scripts/cloud_drain_queue_path_v1.py", "scripts/cloud_forge_run_queue_path_v1.py"),
    ("scripts/cloud_drain_single_cycle_gate_v1.py", "scripts/cloud_auto_runtime_single_cycle_gate_v1.py"),
    ("scripts/cloud_drain_seal__complete_v1.py", "scripts/cloud_forge_run_seal__complete_v1.py"),
    ("scripts/cloud_drain_wire_batch_chain_v1.py", "scripts/cloud_forge_run_wire_batch_chain_v1.py"),
    ("scripts/cloud_drain_cf_secrets_v1.sh", "scripts/cloud_auto_runtime_cf_secrets_v1.sh"),
    ("scripts/n8n_wire_cloud_drain_v1.sh", "scripts/n8n_wire_cloud_auto_runtime_v1.sh"),
    ("scripts/generate_secondary_cloud_drain_batch_v1.py", "scripts/generate_secondary_cloud_forge_run_batch_v1.py"),
    ("scripts/generate_secondary_cloud_drain_next_100_v1.py", "scripts/generate_secondary_cloud_forge_run_next_100_v1.py"),
    ("scripts/generate__5000_drain_patch_v1.py", "scripts/generate__5000_forge_run_patch_v1.py"),
    ("scripts/fbe/lib/cloud_drain_queue_v1.py", "scripts/fbe/lib/cloud_forge_run_queue_v1.py"),
    ("scripts/test_cloud_drain_advance_head_guard_v1.py", "scripts/test_cloud_forge_run_advance_head_guard_v1.py"),
    ("scripts/test_cloud_drain_idle_batch_no_fake_green_v1.py", "scripts/test_cloud_auto_runtime_idle_batch_no_fake_green_v1.py"),
    ("scripts/validate-hub-cloud-drain-proceed-v1.sh", "scripts/validate-hub-cloud-forge-run-proceed-v1.sh"),
    ("scripts/validate-cloud-drain-hundred-rows-vocabulary-v1.sh", "scripts/validate-cloud-forge-run-hundred-rows-vocabulary-v1.sh"),
    ("scripts/validate-secondary-cloud-drain-next-100-v1.sh", "scripts/validate-secondary-cloud-forge-run-next-100-v1.sh"),
    # Data SSOT
    ("data/cloud-drain-auto-runtime-v1.json", "data/cloud-auto-runtime-v1.json"),
    ("data/cloud-drain-queue-active-v1.json", "data/cloud-forge-run-queue-active-v1.json"),
    ("data/cloud-drain-batch-pipeline-v1.json", "data/cloud-forge-run-batch-pipeline-v1.json"),
    ("data/cloud-drain-full-pack-pattern-v1.json", "data/cloud-forge-run-full-pack-pattern-v1.json"),
    ("data/cloud-drain-hundred-rows-per-turn-vocabulary-v1.json", "data/cloud-forge-run-hundred-rows-per-turn-vocabulary-v1.json"),
    ("data/cloud-drain--5000-patch-v1.json", "data/cloud-forge-run--5000-patch-v1.json"),
    ("data/hub-cloud-drain-proceed-v1.json", "data/hub-cloud-forge-run-proceed-v1.json"),
    ("data/secondary-cloud-drain-next-100-v1.json", "data/secondary-cloud-forge-run-next-100-v1.json"),
    # Laws
    (
        "brain-os/law/enforcement/SOURCEA_CLOUD_DRAIN_FULL_PACK_PATTERN_LOCKED_v1.md",
        "brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_FULL_PACK_PATTERN_LOCKED_v1.md",
    ),
    (
        "brain-os/law/enforcement/SOURCEA_CLOUD_DRAIN_HUNDRED_ROWS_PER_TURN_TERMINOLOGY_LOCKED_v1.md",
        "brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_HUNDRED_ROWS_PER_TURN_TERMINOLOGY_LOCKED_v1.md",
    ),
    # Incidents + reports
    (
        "brain-os/incidents/SINA_CLOUD_DRAIN_BATCH3_RAILWAY_CHAIN_INCIDENT_042_LOCKED_v1.md",
        "brain-os/incidents/SINA_CLOUD_FORGE_RUN_BATCH3_RAILWAY_CHAIN_INCIDENT_042_LOCKED_v1.md",
    ),
    (
        "brain-os/incidents/SINA_CLOUD_DRAIN_HUNDRED_ROWS_VOCABULARY_INCIDENT_043_LOCKED_v1.md",
        "brain-os/incidents/SINA_CLOUD_FORGE_RUN_HUNDRED_ROWS_VOCABULARY_INCIDENT_043_LOCKED_v1.md",
    ),
    (
        "SINA_CLOUD_DRAIN_BATCH3_RAILWAY_CHAIN_INCIDENT_042_REPORT_LOCKED_v1.md",
        "SINA_CLOUD_FORGE_RUN_BATCH3_RAILWAY_CHAIN_INCIDENT_042_REPORT_LOCKED_v1.md",
    ),
    (
        "SINA_CLOUD_DRAIN_HUNDRED_ROWS_VOCABULARY_INCIDENT_043_REPORT_LOCKED_v1.md",
        "SINA_CLOUD_FORGE_RUN_HUNDRED_ROWS_VOCABULARY_INCIDENT_043_REPORT_LOCKED_v1.md",
    ),
    # Docs + n8n
    ("docs/CLOUD_DRAIN_AUTO_RUNTIME_PLAN_v1.md", "docs/CLOUD_AUTO_RUNTIME_PLAN_v1.md"),
    ("n8n/workflows/wf-cloud-drain-auto-v1.json", "n8n/workflows/wf-cloud-auto-runtime-v1.json"),
    # Cursor rules
    (".cursor/rules/037-cloud-drain-hundred-rows-per-turn-v1.mdc", ".cursor/rules/037-cloud-forge-run-hundred-rows-per-turn-v1.mdc"),
]

SKIP_GLOBS = {
    ".git",
    "node_modules",
    "brand/macos-apps",
    ".cursor/debug",
    "receipts",
    "__pycache__",
    ".sina-loop",
}

# Text replacements after file renames (order matters — longer first)
TEXT_REPLACEMENTS: list[tuple[str, str]] = [
    ("secondary-cloud-drain-batch-", "secondary-cloud-forge-run-batch-"),
    ("secondary_cloud_drain_batch", "secondary_cloud_forge_run_batch"),
    ("cloud-drain-hundred-rows-per-turn-vocabulary", "cloud-forge-run-hundred-rows-per-turn-vocabulary"),
    ("cloud-drain--5000-patch", "cloud-forge-run--5000-patch"),
    ("cloud-drain-full-pack-pattern", "cloud-forge-run-full-pack-pattern"),
    ("cloud-drain-batch-pipeline", "cloud-forge-run-batch-pipeline"),
    ("cloud-drain-queue-active", "cloud-forge-run-queue-active"),
    ("cloud-drain-auto-runtime", "cloud-auto-runtime"),
    ("hub-cloud-drain-proceed", "hub-cloud-forge-run-proceed"),
    ("hub_cloud_drain_proceed_v1", "hub_cloud_forge_run_proceed_v1"),
    ("cloud_drain_auto_runtime_v1", "cloud_auto_runtime_v1"),
    ("cloud_drain_single_cycle_gate_v1", "cloud_auto_runtime_single_cycle_gate_v1"),
    ("cloud_drain_queue_path_v1", "cloud_forge_run_queue_path_v1"),
    ("cloud_drain_queue_v1", "cloud_forge_run_queue_v1"),
    ("cloud_drain_seal__complete_v1", "cloud_forge_run_seal__complete_v1"),
    ("cloud_drain_wire_batch_chain_v1", "cloud_forge_run_wire_batch_chain_v1"),
    ("cloud_drain_cf_secrets_v1", "cloud_auto_runtime_cf_secrets_v1"),
    ("generate_secondary_cloud_drain_batch_v1", "generate_secondary_cloud_forge_run_batch_v1"),
    ("generate__5000_drain_patch_v1", "generate__5000_forge_run_patch_v1"),
    ("validate-hub-cloud-drain-proceed", "validate-hub-cloud-forge-run-proceed"),
    ("validate-cloud-drain-hundred-rows", "validate-cloud-forge-run-hundred-rows"),
    ("SOURCEA_CLOUD_DRAIN_HUNDRED_ROWS", "SOURCEA_CLOUD_FORGE_RUN_HUNDRED_ROWS"),
    ("SOURCEA_CLOUD_DRAIN_FULL_PACK", "SOURCEA_CLOUD_FORGE_RUN_FULL_PACK"),
    ("SINA_CLOUD_DRAIN_HUNDRED_ROWS", "SINA_CLOUD_FORGE_RUN_HUNDRED_ROWS"),
    ("SINA_CLOUD_DRAIN_BATCH3", "SINA_CLOUD_FORGE_RUN_BATCH3"),
    ("037-cloud-drain-hundred-rows", "037-cloud-forge-run-hundred-rows"),
    ("cloud-drain-tick-v1", "cloud-auto-runtime-tick-v1"),
    ("sourcea-cloud-drain-tick-v1", "sourcea-cloud-auto-runtime-tick-v1"),
    ("wf-cloud-drain-auto", "wf-cloud-auto-runtime"),
    ("run_pack_loop", "run_auto_runtime_pack"),
    ("/api/cloud-drain/", "/api/cloud-forge-run/"),
    ("cloud-drain/phase-observed", "cloud-forge-run/phase-observed"),
    ("cloud-drain/phase-observed-v1.json", "cloud-forge-run/phase-observed-v1.json"),
    ("receipts/cloud-drain/", "receipts/cloud-forge-run/"),
    ("CLOUD_DRAIN_AUTO_PROCEED", "CLOUD_FORGE_RUN_AUTO_PROCEED"),
    ("cloud_drain_head", "cloud_forge_run_head"),
    ("cloud_drain_last_completed", "cloud_forge_run_last_completed"),
    ("cloud-drain-queue-head", "cloud-forge-run-queue-head"),
    ("cloud-drain-pack", "cloud-forge-run-pack"),
    ("cloud-drain-auto-tick", "cloud-auto-runtime-tick"),
    ("autonomous-drain-observer", "autonomous-forge-run-observer"),
    ("autonomous-drain-ramp", "autonomous-forge-run-ramp"),
    ("autonomous-drain-cycle", "autonomous-forge-run-cycle"),
    ("cloud-drain-single-cycle-gate", "cloud-auto-runtime-single-cycle-gate"),
    ("hub-cloud-drain-proceed", "hub-cloud-forge-run-proceed"),
    ("secondary-cloud-drain-next-100", "secondary-cloud-forge-run-next-100"),
    ("CLOUD_DRAIN_AUTO_RUNTIME_PLAN", "CLOUD_AUTO_RUNTIME_PLAN"),
    ("cloud_drain_boot_heal", "cloud_forge_run_boot_heal"),
    ("cloud-drain-boot_heal", "cloud-forge-run-boot_heal"),
    ("cloud-drain-", "cloud-forge-run-"),
    ("cloud-drain-batch", "cloud-forge-run-batch"),
    ("cloud-drain-queue", "cloud-forge-run-queue"),
    ("Cloud Forge Run", "Cloud Forge Run"),
    ("cloud-drain", "cloud-forge-run"),
    ("cloud_drain", "cloud_forge_run"),
]


def _should_skip(path: Path) -> bool:
    parts = path.parts
    return any(p in SKIP_GLOBS for p in parts)


def git_mv(old: Path, new: Path) -> None:
    new.parent.mkdir(parents=True, exist_ok=True)
    if not old.is_file() and not old.is_dir():
        if new.exists():
            return
        raise SystemExit(f"FAIL missing {old}")
    if new.exists():
        return
    proc = subprocess.run(["git", "mv", str(old), str(new)], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        shutil.move(str(old), str(new))


def rename_batch_files() -> int:
    n = 0
    for p in sorted(ROOT.glob("data/secondary-cloud-drain-batch-*")):
        new_name = p.name.replace("secondary-cloud-drain-", "secondary-cloud-forge-run-")
        new = p.parent / new_name
        if p.name != new_name:
            git_mv(p, new)
            n += 1
    return n


def rename_cf_worker() -> None:
    old = ROOT / "cloud/workers/cloud-drain-tick-v1"
    new = ROOT / "cloud/workers/cloud-auto-runtime-tick-v1"
    if old.is_dir() and not new.exists():
        subprocess.run(["git", "mv", str(old), str(new)], cwd=ROOT, check=True)


def apply_text_replacements() -> int:
    touched = 0
    exts = {".py", ".sh", ".json", ".md", ".mdc", ".js", ".html", ".toml", ".yaml", ".yml", ".txt", ".plist"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or _should_skip(path):
            continue
        if path.suffix.lower() not in exts and path.name not in ("Dockerfile.fbe-runner", "railway.toml"):
            continue
        if "cloud_forge_run_physical_rename_v1.py" in str(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        orig = text
        for old, new in TEXT_REPLACEMENTS:
            text = text.replace(old, new)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            touched += 1
    return touched


def main() -> int:
    dry = "--dry-run" in sys.argv
    if dry:
        print("DRY RUN — renames:")
        for o, n in FILE_RENAMES:
            print(f"  {o} -> {n}")
        print("  data/secondary-cloud-drain-batch-* -> secondary-cloud-forge-run-batch-*")
        print("  cloud/workers/cloud-drain-tick-v1 -> cloud-auto-runtime-tick-v1")
        return 0

    for old_rel, new_rel in FILE_RENAMES:
        git_mv(ROOT / old_rel, ROOT / new_rel)

    batches = rename_batch_files()
    rename_cf_worker()
    touched = apply_text_replacements()

    # Pointer stub for old auto-runtime filename in vocabulary SSOT
    vocab = ROOT / "data/cloud-motor-founder-vocabulary-v1.json"
    if vocab.is_file():
        doc = json.loads(vocab.read_text(encoding="utf-8"))
        doc["physical_rename"] = "scripts/cloud_forge_run_physical_rename_v1.py"
        doc["version"] = "3.0.0"
        doc["saved_at"] = "2026-06-24T22:00:00Z"
        for term in (doc.get("terms") or {}).values():
            term.pop("machine_paths_unchanged", None)
            term["renamed"] = True
        vocab.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"ok": True, "batch_files_renamed": batches, "text_files_touched": touched}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
