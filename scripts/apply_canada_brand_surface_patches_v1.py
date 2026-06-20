#!/usr/bin/env python3
"""Apply Canada June 2026 vertical patches across TrustField · Noetfield surfaces."""
from __future__ import annotations

from pathlib import Path

TF_COMPLIANCE = Path.home() / "Desktop/TrustField Technologies/templates/compliance.html"
NF_BANK = Path.home() / "Desktop/Noetfield/Noetfield-All-Documents/Noetfield/bank-pilot/index.html"
NF_COPILOT = Path.home() / "Desktop/Noetfield/Noetfield-All-Documents/Noetfield/copilot/index.html"

TF_BLOCK = """
    <div class="rounded-xl border border-trust-500/40 bg-trust-950/30 p-5">
      <h2 class="font-semibold text-white">Canada tokenization &amp; RWA — June 2026</h2>
      <p class="mt-2 text-slate-400">CSA Project Tokenization, Bill C-15 stablecoin readiness, and FINTRAC/CIRO examination pressure mean issuers, EMDs, and MSBs need <strong class="text-slate-300">evidence of governed operations</strong> — not another tokenization pitch.</p>
      <ul class="mt-3 space-y-2 text-slate-400 text-sm">
        <li><strong class="text-slate-300">EMD / fractional CRE / digital securities</strong> — Trust Brief + partner receipt pack (T-P6)</li>
        <li><strong class="text-slate-300">MSB &amp; CIRO dealers</strong> — FINTRAC evidence chain pilot (TF-P1-DP)</li>
        <li><strong class="text-slate-300">Stablecoin &amp; custody rails</strong> — RPAA/FINTRAC readiness module (TF-001)</li>
      </ul>
      <p class="mt-3 text-slate-400 text-sm">Shadow pilot · one metric · CAD deposit refunded if missed · live tamper-FAIL demo in five minutes. <strong class="text-slate-300">Advisory only</strong> — no custody, no payment initiation.</p>
      <p class="mt-2 text-sm"><a class="text-trust-500 hover:underline" href="/pilot">RPAA readiness pilot →</a> · <a class="text-trust-500 hover:underline" href="mailto:hello@trustfield.ca?subject=Canada%20RWA%20evidence%20pilot">Book 15-min evidence walkthrough →</a></p>
    </div>
"""

NF_CANADA_SECTION = """
 <section class="nf-section-block nf-section-block--canada" aria-labelledby="canada-mortgage">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">CA</span><div>
 <p class="nf-eyebrow" id="canada-mortgage">Canada · June 2026</p><h2>CSA tokenization + AI mortgage ops — governance receipt</h2>
 <p class="nf-section-lead">Canadian lenders and AI mortgage platforms face OSFI E-23 and FINTRAC explainability pressure on <strong>internal AI</strong> — separate from commercial attestation rails (TrustField). Noetfield governs at dispatch: evaluate → signed TLE → replay → tamper-FAIL.</p>
 </div></div>
 <div class="nf-trust-signals-grid"><div class="nf-trust-signal"><span class="nf-trust-signal-label">Fundmore.ai · AI underwriting ops</span><span class="nf-signal-badge nf-signal-badge--available">NF-RD fit</span></div><div class="nf-trust-signal"><span class="nf-trust-signal-label">Pineapple broker AI (split thread)</span><span class="nf-signal-badge nf-signal-badge--orientation">AI ops only</span></div><div class="nf-trust-signal"><span class="nf-trust-signal-label">Payment rails / MSB execution</span><span class="nf-signal-badge nf-signal-badge--na">TrustField lane</span></div></div>
 <div class="nf-cta-actions" style="margin-top:1.25rem"><a class="btn btn-primary" href="/trust-brief/intake/?interest=pilot&vector=bank-pilot">Apply for Canada shadow pilot</a><a class="btn btn-secondary" href="/copilot/demo/">5-minute demo</a></div>
 </section>
"""


def patch_tf() -> bool:
    if not TF_COMPLIANCE.is_file():
        return False
    text = TF_COMPLIANCE.read_text(encoding="utf-8")
    if "Canada tokenization &amp; RWA" in text:
        return True
    needle = '      <p class="mt-2 text-slate-400 text-sm">Canada’s federal'
    if needle not in text:
        return False
    text = text.replace(needle, TF_BLOCK.strip() + "\n      " + needle)
    TF_COMPLIANCE.write_text(text, encoding="utf-8")
    return True


def patch_nf(path: Path) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if "nf-section-block--canada" in text:
        return True
    needle = ' <section class="nf-trust-signals"'
    if needle not in text:
        return False
    text = text.replace(needle, NF_CANADA_SECTION + needle, 1)
    path.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    results = {
        "trustfield_compliance": patch_tf(),
        "noetfield_bank_pilot": patch_nf(NF_BANK),
        "noetfield_copilot": patch_nf(NF_COPILOT),
    }
    print(results)
    return 0 if any(results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
