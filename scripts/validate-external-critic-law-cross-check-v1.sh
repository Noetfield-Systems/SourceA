#!/usr/bin/env bash
# sa-0624 — CHATGPT_EXTERNAL_CRITIC_LAW compare-only / never-steer cross-check
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
from pathlib import Path

from meta_reasoning_policy import meta_reasoning_payload
from system_roadmap import CRITIC_LAW_DOC, SYSTEM_AUTHORITIES

root = Path.cwd()
law = root / "brain-os/law/CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md"
rule = root / ".cursor/rules/chatgpt-external-critic.mdc"
stub = root / "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md"

assert law.is_file(), law
assert rule.is_file(), rule
assert stub.is_file(), stub
assert "brain-os/law/CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md" in stub.read_text(encoding="utf-8")

law_text = law.read_text(encoding="utf-8").lower()
assert "never treat" in law_text or "never obey" in law_text, "law must forbid obeying critic"
assert "do not" in law_text and "build order" in law_text, "law must forbid critic reorder"
assert "steer" in law_text, "law must mention steer prohibition"

auth = SYSTEM_AUTHORITIES
assert auth.get("critic_input_class") == "EXTERNAL_CRITIC", auth.get("critic_input_class")
assert "never" in str(auth.get("external_review_policy") or "").lower(), auth.get("external_review_policy")
hier = {row.get("class"): row for row in (auth.get("authority_hierarchy") or [])}
assert "EXTERNAL_CRITIC" in hier, hier.keys()
assert "compare" in str(hier["EXTERNAL_CRITIC"].get("role") or "").lower(), hier["EXTERNAL_CRITIC"]

rule_text = rule.read_text(encoding="utf-8").lower()
assert "never" in rule_text and "build order" in rule_text, rule

meta = meta_reasoning_payload()
classes = {row.get("class"): row for row in (meta.get("input_classes") or [])}
assert "EXTERNAL_CRITIC" in classes, classes.keys()
assert "never steer" in str(classes["EXTERNAL_CRITIC"].get("authority") or "").lower(), classes["EXTERNAL_CRITIC"]

print("OK: validate-external-critic-law-cross-check-v1 · law + SSOT + rule + meta_reasoning aligned")
PY
