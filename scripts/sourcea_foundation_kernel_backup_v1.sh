#!/usr/bin/env bash
# Foundation + kernel backup — local broker + git bundle (other repos depend on this).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="${1:-$(date -u +%Y-%m-%d)}"
BACKUP_ROOT="${HOME}/Desktop/SinaaiDataBase/archive/sourcea-foundation-kernel-backup-${STAMP}"
BUNDLE="${BACKUP_ROOT}/sourcea-main.git.bundle"
TREE="${BACKUP_ROOT}/sourcea-working-tree.tgz"
MANIFEST="${BACKUP_ROOT}/manifest.json"

mkdir -p "${BACKUP_ROOT}"
cd "${ROOT}"

echo "=== SourceA foundation-kernel backup → ${BACKUP_ROOT} ==="

git bundle create "${BUNDLE}" HEAD
echo "OK git bundle: ${BUNDLE}"

tar -czf "${TREE}" \
  --exclude='./.git' \
  --exclude='./commercial-video-factory/node_modules' \
  --exclude='./.cursor/debug-*.log' \
  -C "${ROOT}" .
echo "OK working tree: ${TREE}"

python3 - <<PY
import json, subprocess
from datetime import datetime, timezone
from pathlib import Path

root = Path("${ROOT}")
backup = Path("${BACKUP_ROOT}")
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=root, text=True).strip()
row = {
    "schema": "sourcea-foundation-kernel-backup-v1",
    "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "git_head": head,
    "git_branch": branch,
    "bundle": str(backup / "sourcea-main.git.bundle"),
    "working_tree": str(backup / "sourcea-working-tree.tgz"),
    "repo": str(root),
    "law": "SourceA = foundation kernel for all repos; commercial plane is separate.",
    "restore_bundle": f"git clone {backup / 'sourcea-main.git.bundle'} sourcea-restored",
}
(backup / "manifest.json").write_text(json.dumps(row, indent=2) + "\\n", encoding="utf-8")
print("OK manifest:", backup / "manifest.json")
PY

echo "DONE: foundation-kernel backup at ${BACKUP_ROOT}"
