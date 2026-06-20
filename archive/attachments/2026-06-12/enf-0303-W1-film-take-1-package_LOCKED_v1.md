# enf-0303 — W1 Film Take 1 Package (LOCKED v1)

**Saved:** 2026-06-12T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
| Field | Value |
|-------|-------|
| **trace_id** | `ENF-0303-W1-FILM-TAKE-1` |
| **task** | `enf-0303` · DEMO-ENF-S7 take 1 |
| **thread** | `THREAD-ENFORCEMENT` |
| **date** | 2026-06-12 |
| **worker** | SourceA Worker |
| **law** | `ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md` |

---

## Result (honest)

| Layer | Status | Proof |
|-------|--------|-------|
| **Executor witness take 1** | **PASS** | `enf-0303-W1-film-take-1-witness-log.txt` |
| **W2 write-path** | **PASS** | `validate-demo-write-path-v1.sh` |
| **Demo enforcement** | **PASS** | `validate-demo-enforcement-v1.sh` (+ tamper) |
| **Universe invariants** | **PASS** | `validate-universe-invariants-v1.sh` |
| **Founder screen/video (.mp4/.mov)** | **PENDING** | ASF one-tap screen record during same script run |

**W1 full PASS** requires founder screen recording saved beside this package. Executor cannot film on behalf of ASF.

---

## Artifacts (this folder)

| File | Role |
|------|------|
| `enf-0303-W1-film-take-1-witness-log.txt` | Terminal witness — BLOCK/ALLOW/tamper/FREEZE beats |
| `enf-0303-W1-film-take-1-receipt-snapshot.json` | Latest ALLOW receipt at take 1 time |
| `enf-0303-W1-film-take-1-package_LOCKED_v1.md` | This manifest |

**Drop zone for founder video:** save as `enf-0303-W1-film-take-1-screenrecording.<ext>` in this folder.

---

## Receipt paths (disk)

- Latest: `~/.sina/demo-enforcement/receipts/latest-demo-receipt.json`
- Spine: `GEV-454e722b5362` (at witness time)
- Run script: `bash scripts/demo-enforcement-5min-v1.sh`

---

## Validators (all OK 2026-06-12)

```bash
bash scripts/validate-demo-enforcement-v1.sh
bash scripts/validate-universe-invariants-v1.sh
bash scripts/validate-demo-write-path-v1.sh
```

---

## Forbidden (respected)

REGISTRY drain hero · hub rewrite · whitepaper-first · sa-0798 P0 promotion

---

*Take 1 executor slice done · founder screen file completes W1 film gate*
