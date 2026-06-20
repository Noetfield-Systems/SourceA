#!/usr/bin/env bash
# Brain-order: docs/system-audits/ wired into mandatory brain loop (pointers only — vault stays put).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export ROOT

python3 - <<'PY'
import os
import sys
from pathlib import Path

root = Path(os.environ["ROOT"])
errors: list[str] = []

vault = root / "docs/system-audits"
index = vault / "README_INDEX.md"
expected = [
    "OLD_BRAIN_EXTRACTION_FULL_2026-06-06.yaml",
    "MASTER_SYSTEM_AUDIT_2026-06-06.md",
    "SYSTEM_SUMMARY_2026-06-06.md",
    "E2E_LIVE_AUDIT_2026-06-06.md",
    "PRE_LLM_AND_WTM_EVIDENCE_2026-06-06.md",
    "GOVERNANCE_RULE_BREAKING_2026-06-06.md",
    "PROMPT_OS_TWO_LAYER_MODEL_2026-06-06.md",
    "ARCHITECTURE_SYNTHESIS_2026-06-06.md",
    "FOUNDER_SUPPORT_PACK_2026-06-06.md",
    "REPO_INVENTORY_2026-06-06.md",
    "README_INDEX.md",
]
for name in expected:
    if not (vault / name).is_file():
        errors.append(f"missing vault file: docs/system-audits/{name}")

checks: list[tuple[str, str]] = [
    ("brain-os/contract/MANDATORY_BRAIN_CHAT_LOCKED_v1.md", "docs/system-audits/README_INDEX.md"),
    ("brain-os/memory/BRAIN_KNOWLEDGE_INDEX_LOCKED_v1.md", "## O. System audit exports"),
    ("brain-os/memory/BRAIN_MASTER_MEMORY_LOCKED_v1.md", "docs/system-audits/README_INDEX.md"),
    ("brain-os/contract/BRAIN_FULL_TRANSFER_PROMPT_LOCKED_v1.md", "docs/system-audits/README_INDEX.md"),
    ("brain-os/law/BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md", "docs/system-audits/README_INDEX.md"),
    ("scripts/important_docs_index.py", "docs/system-audits/README_INDEX.md"),
    ("scripts/sync-brain-pack.sh", "Audits stay in"),
]
for rel, needle in checks:
    path = root / rel
    if not path.is_file():
        errors.append(f"missing {rel}")
        continue
    if needle not in path.read_text(encoding="utf-8"):
        errors.append(f"{rel}: missing {needle!r}")

sync = (root / "scripts/sync-brain-pack.sh").read_text(encoding="utf-8")
if "docs/system-audits" in sync and "cp " in sync and "system-audits" in sync.split("cp", 1)[-1][:200]:
    errors.append("sync-brain-pack.sh must not copy docs/system-audits into ~/.sina/brain")

if errors:
    for e in errors:
        print(f"FAIL: {e}")
    sys.exit(1)
print("OK: validate-system-audits-mandatory-loop-v1 · vault=11 · brain pointers wired")
PY
