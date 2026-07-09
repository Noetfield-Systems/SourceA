<!-- WORKER_INBOX pending=1 source=deep_research_up_dr queue=1/10 sa=sa-9041 -->
# SourceA Worker — UP-DR deep research W1

**Updated:** 2026-07-06T09:17:58Z

---

WORK: sa-9041 — Claim hygiene — install/PyPI

WORK: UP-DR-01 — Claim hygiene — install/PyPI
Path: SourceA-landing/green-unified/eval.html
Goal: Eval page and PyPI probe agree — no false install promise
Done when: probe_sourcea_boot_pypi_v1.py ok OR eval copy says GitHub clone pending
Verify: cd ~/Desktop/SourceA && python3 scripts/probe_sourcea_boot_pypi_v1.py --json && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/eval --marker "sourcea-boot" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
Proof: https://sourcea.app/eval
One bounded turn · receipt + Supabase row · WORKER_ROUND_REPORT · STOP.

---

**Worker:** one UP-DR plan · verification built in · STOP.
