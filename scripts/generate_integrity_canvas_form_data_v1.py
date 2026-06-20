#!/usr/bin/env python3
"""Generate integrity-form-data.generated.ts for M1 Canvas (100 agent POV + live open rows)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = Path.home() / ".sina/agent-workspaces/trustfield/commercial-goal/forms/SOURCEA_100_AGENT_POV_FORM_v2.yaml"
OUT_PATH = (
    Path.home()
    / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/integrity-form-data.generated.ts"
)
M1_CANVAS = (
    Path.home()
    / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.tsx"
)
OPEN_ROW_SPEC_PATH = M1_CANVAS.parent / "integrity-open-row-spec.ts"
GEN_BEGIN = "// @generated-integrity-form-data-begin"
GEN_END = "// @generated-integrity-form-data-end"
OPEN_ROW_BEGIN = "// @generated-integrity-open-row-spec-begin"
OPEN_ROW_END = "// @generated-integrity-open-row-spec-end"

PHASE_CATEGORY = {
    1: "p0-freeze",
    2: "product-surface",
    3: "agents-council",
    4: "p0-freeze",
    5: "p0-freeze",
    6: "agents-council",
    7: "agents-council",
    8: "incidents-trust",
    9: "commercial",
    10: "steady-state",
}

CATEGORY_LABEL = {c["id"]: c["label"] for c in []}  # filled below from M1

DECISIVE_OPTS = [
    ("A", "Option A — primary", "A", "Primary path per agent brief."),
    ("B", "Option B — alternate", "B", "Alternate path · disk + Track updated."),
    ("C", "Option C — defer", "C", "Deferred · background only."),
    ("D", "Option D — reject", "D", "Rejected or parked until ASF reopens."),
]
AUDIT_OPTS = [
    ("PASS", "PASS — proof accepted", "PASS", "Maintainer marks step DONE with proof path."),
    ("FAIL", "FAIL — needs fix", "FAIL", "Track row opens · Maintainer remediate before DONE."),
    ("SKIP", "SKIP this cycle", "SKIP", "Step stays open · no false DONE."),
    ("DISCUSS", "Need explanation", "Discuss", "Comment box · agent prepares brief."),
]

AGENT_LABELS = {
    "brain": "Brain",
    "commercial": "Commercial Specialist",
    "gov": "Gov Specialist",
    "research": "Research Brief Specialist",
    "maintainer_1": "Maintainer 1",
    "maintainer_2": "Maintainer 2",
    "anchor": "Maintainer 3 · Anchor (Mono)",
    "aect": "AECT",
}

OPEN_ROW_AGENT_BY_ID: dict[str, str] = {
    "Q-MONO-SSOT-LANE": "anchor",
    "Q-ENGINE-TEST-01": "anchor",
    "Q-ENGINE-TEST-02": "anchor",
    "Q-WIRE-G3": "anchor",
    "Q-ACTIVE-NOW-SYNC": "maintainer_2",
    "Q-HUB-LAG": "maintainer_1",
    "Q-M2-029": "maintainer_2",
    "Q-M2-REG": "maintainer_2",
    "Q-M2-READ": "maintainer_2",
    "Q-M2-FORM-SYNC": "maintainer_2",
    "Q-INC-015": "gov",
    "Q-JUDGE-STACK-v1": "gov",
    "Q-FR-002-WTM": "research",
    "Q-FR-1013f0": "commercial",
    "Q-PLAN-300": "commercial",
    "11.01": "commercial",
    "11.02": "commercial",
    "11.03": "maintainer_2",
    "11.04": "commercial",
    "11.05": "commercial",
    "Q-NF-SPEC-PROMOTE": "research",
    "Q-THREAD-ROOM-v1": "maintainer_1",
    "Q-SYS-INTEGRITY-RESUME": "maintainer_2",
    "Q-1.10-SEAL": "maintainer_2",
    "Q-BC-01": "brain",
    "Q-BC-02": "brain",
    "Q-BC-03": "brain",
    "Q-BC-04": "brain",
    "Q-BC-05": "brain",
    "Q-BC-06": "brain",
    "Q-BC-07": "brain",
    "Q-BC-08": "brain",
    "Q-BC-09": "brain",
    "Q-BC-10": "brain",
    "Q-GATH-01": "brain",
    "Q-GATH-02": "brain",
    "Q-GATH-03": "brain",
    "Q-GATH-04": "brain",
    "Q-GATH-05": "brain",
    "Q-FINAL-01": "brain",
    "Q-FINAL-02": "brain",
    "Q-FINAL-03": "anchor",
    "Q-FINAL-04": "commercial",
    "Q-FINAL-05": "brain",
    "Q-FINAL-06": "brain",
    "Q-FINAL-07": "brain",
    "Q-CONF-PICK-Q-M2-REG": "maintainer_2",
    "Q-CONF-PICK-Q-FR-002-WTM": "research",
    "Q-CONF-PICK-Q-FR-1013f0": "commercial",
    "Q-CONF-U031-BAY": "brain",
    "Q-CONF-F002-BROKER": "brain",
    "Q-CONF-B0503-CONSUMER": "brain",
    "Q-CONF-MCP-PHASE2": "brain",
    "Q-CONF-DUAL-NORTHSTAR": "brain",
    "Q-CONF-CREED-36V14": "commercial",
    "Q-CONF-FBE-MONO-EXEC": "anchor",
    "Q-CONF-PLUSONE-MOTOR": "brain",
    "Q-CONF-FALSE-DONE-GUARD": "maintainer_2",
    "7.05": "aect",
    "7.06": "aect",
    "7.07": "aect",
    "8.09": "gov",
    "2.02": "maintainer_1",
}


def _resolve_open_row_agent(q: dict) -> str:
    if q.get("agent"):
        return str(q["agent"])
    qid = str(q["id"])
    if qid in OPEN_ROW_AGENT_BY_ID:
        return OPEN_ROW_AGENT_BY_ID[qid]
    if qid.startswith("Q-BC-"):
        return "brain"
    if qid.startswith("Q-FINAL-"):
        return "brain"
    if qid.startswith("Q-CONF-"):
        return "brain"
    if qid.startswith("Q-GATH-"):
        return "brain"
    if qid.startswith("ENF-"):
        return "commercial"
    if qid.startswith("Q-M2-"):
        return "maintainer_2"
    if qid.startswith("Q-INC-"):
        return "gov"
    if qid.startswith("Q-FR-"):
        return "research" if "WTM" in qid else "commercial"
    if qid.startswith("Q-NF-"):
        return "research"
    if qid.startswith("Q-HUB") or qid.startswith("Q-THREAD"):
        return "maintainer_1"
    if qid.startswith("Q-ENGINE") or qid.startswith("Q-WIRE") or qid.startswith("Q-MONO"):
        return "anchor"
    blocks = str(q.get("blocks") or q.get("help") or "").lower()
    if "thread-enforcement" in blocks or "commercial specialist" in blocks:
        return "commercial"
    if "conflict" in blocks or qid.startswith("7."):
        return "aect"
    if qid.startswith("8."):
        return "gov"
    if qid.startswith("2."):
        return "maintainer_1"
    return "maintainer_2"


def _load_yaml_questions() -> list[dict]:
    import yaml

    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    return list(data.get("questions") or [])


def _load_open_questions() -> list[dict]:
    raw = subprocess.check_output(
        [sys.executable, str(ROOT / "scripts/live_founder_decision_form_v1.py"), "--json"],
        text=True,
    )
    payload = json.loads(raw)
    return list(payload.get("open_questions") or [])


def _opts(decisive: bool) -> list[dict]:
    src = DECISIVE_OPTS if decisive else AUDIT_OPTS
    return [
        {"key": k, "label": label, "short": short, "ifYouPick": effect}
        for k, label, short, effect in src
    ]


def _ts_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def _question_ts(q: dict, *, open_row: bool = False) -> str:
    phase = int(q.get("phase") or 0)
    cat = PHASE_CATEGORY.get(phase, "steady-state")
    cat_labels = {
        "p0-freeze": "P0, freeze & factory pace",
        "product-surface": "Product & public surface",
        "commercial": "Commercial & partners",
        "agents-council": "Agents, council & conflicts",
        "incidents-trust": "Incidents & trust",
        "steady-state": "Steady-state & execution",
    }
    agent = str(q.get("agent") or "maintainer_2")
    decisive = bool(q.get("decisive")) if not open_row else True
    opts = _opts(decisive)
    if open_row and q.get("options"):
        opts = []
        for o in q["options"]:
            if isinstance(o, str):
                key = o.split(" — ")[0].strip() if " — " in o else o.split()[0]
                effects = q.get("option_effects") or {}
                ifYouPick = effects.get(key) or str(
                    q.get("effect") or "Maintainer 2 records your pick on disk · owner agent executes."
                )
                opts.append(
                    {
                        "key": key,
                        "label": o,
                        "short": key,
                        "ifYouPick": ifYouPick,
                    }
                )
    rec = str(q.get("recommended") or q.get("shipped") or (opts[0]["key"] if opts else "A"))
    shipped = q.get("shipped")
    lines = [
        "  {",
        f'    id: {_ts_str(str(q["id"]))},',
        f'    phase: {_ts_str(f"P{phase}" if phase else "OPEN")},',
        f'    category: {_ts_str(cat)},',
        f'    categoryLabel: {_ts_str(cat_labels.get(cat, cat))},',
        f'    subject: {_ts_str(str(q.get("title") or q.get("subject") or q["id"]))},',
        f'    question: {_ts_str(str(q.get("question") or ""))},',
        f'    help: {_ts_str(str(q.get("blocks") or q.get("help") or "FORM_OFFICIAL open row — pick then confirm."))},',
        f'    diskToday: {_ts_str(str(q.get("disk") or q.get("diskToday") or ""))},',
        '    type: "choice4" as const,',
        f'    recommended: {_ts_str(rec)},',
        "    options: [",
    ]
    for o in opts:
        lines.append(
            f'      {{ key: {_ts_str(o["key"])}, label: {_ts_str(o["label"])}, '
            f'short: {_ts_str(o["short"])}, ifYouPick: {_ts_str(o["ifYouPick"])} }},'
        )
    lines.append("    ],")
    lines.append(f'    maintainerAction: {_ts_str("Maintainer 2 writes your PICK to form JSON only (~30s). Owner agent executes.")},')
    lines.append(f'    founderAction: {_ts_str("Read case · pick option · Confirm · Submit (header/footer) when batch ready.")},')
    lines.append(f'    agent: {_ts_str(agent)},')
    lines.append(f'    agentLabel: {_ts_str(AGENT_LABELS.get(agent, agent))},')
    lines.append(f'    decisive: {str(decisive).lower()},')
    if shipped:
        lines.append(f'    shipped: {_ts_str(str(shipped))},')
    lines.append("  },")
    return "\n".join(lines)


def main() -> int:
    import yaml

    if not YAML_PATH.is_file():
        print(f"FAIL: missing {YAML_PATH}", file=sys.stderr)
        return 1

    yaml_rows = _load_yaml_questions()
    open_rows = _load_open_questions()

    agents_meta = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8")).get("agents") or {}
    agent_entries = []
    for aid, meta in agents_meta.items():
        agent_entries.append(
            f'  {{ id: {_ts_str(aid)}, label: {_ts_str(meta.get("label", aid))}, '
            f'role: {_ts_str(meta.get("role", ""))} }},'
        )

    phases = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8")).get("phases") or []
    by_phase: dict[int, list[str]] = {}
    for q in yaml_rows:
        by_phase.setdefault(int(q["phase"]), []).append(str(q["id"]))
    phase_entries = []
    for p in phases:
        pid = int(p["id"])
        ids = by_phase.get(pid) or []
        phase_entries.append(
            f'  {{ id: {pid}, title: {_ts_str(p["title"])}, '
            f"stepIds: [{', '.join(_ts_str(s) for s in ids)}] }},"
        )

    body = [
        "/** AUTO-GENERATED — scripts/generate_integrity_canvas_form_data_v1.py */",
        "/* eslint-disable */",
        "",
        "export const AGENT_POV_AGENTS = [",
        *agent_entries,
        "] as const;",
        "",
        "export const AGENT_POV_PHASES = [",
        *phase_entries,
        "] as const;",
        "",
        "export const AGENT_POV_FORM_QUESTIONS = [",
        *[_question_ts(q) for q in yaml_rows],
        "];",
        "",
        "export const OPEN_FORM_QUESTIONS = [",
        *[
            _question_ts(
                {**q, "phase": 0, "decisive": True, "agent": _resolve_open_row_agent(q)},
                open_row=True,
            )
            for q in open_rows
        ],
        "];",
        "",
    ]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(body) + "\n", encoding="utf-8")

    inline = [
        GEN_BEGIN,
        "/** AUTO-GENERATED — scripts/generate_integrity_canvas_form_data_v1.py · inline for Canvas SDK (no relative imports) */",
        "const AGENT_POV_AGENTS = [",
        *agent_entries,
        "] as const;",
        "",
        "const AGENT_POV_PHASES = [",
        *phase_entries,
        "] as const;",
        "",
        "const AGENT_POV_FORM_QUESTIONS = [",
        *[_question_ts(q) for q in yaml_rows],
        "];",
        "",
        "const OPEN_FORM_QUESTIONS = [",
        *[
            _question_ts(
                {**q, "phase": 0, "decisive": True, "agent": _resolve_open_row_agent(q)},
                open_row=True,
            )
            for q in open_rows
        ],
        "];",
        GEN_END,
    ]
    _patch_m1_canvas("\n".join(inline) + "\n")
    _patch_open_row_spec()

    print(f"OK: {OUT_PATH} · 100 agent POV · {len(open_rows)} open rows · M1 canvas inlined")
    return 0


def _open_row_inline_block() -> str:
    if not OPEN_ROW_SPEC_PATH.is_file():
        raise SystemExit(f"FAIL: missing open-row spec {OPEN_ROW_SPEC_PATH}")
    src = OPEN_ROW_SPEC_PATH.read_text(encoding="utf-8")
    body = src.replace("export type OpenRowSpec", "type OpenRowSpec")
    body = body.replace("export const FORM_TERMINOLOGY_REQUIRED", "const FORM_TERMINOLOGY_REQUIRED")
    body = body.replace("export const OPEN_ROW_SPEC", "const OPEN_ROW_SPEC")
    body = body.replace("export function getOpenRowSpec", "function getOpenRowSpec")
    return (
        OPEN_ROW_BEGIN
        + "\n// ─── FORM_OFFICIAL open-row spec (inlined — Canvas SDK forbids relative imports) ───\n"
        + body
        + "\n"
        + OPEN_ROW_END
        + "\n"
    )


def _patch_open_row_spec() -> None:
    if not M1_CANVAS.is_file():
        print(f"WARN: missing M1 canvas {M1_CANVAS}", file=sys.stderr)
        return
    block = _open_row_inline_block()
    text = M1_CANVAS.read_text(encoding="utf-8")
    text = re.sub(
        re.escape(OPEN_ROW_BEGIN) + r".*?" + re.escape(OPEN_ROW_END) + r"\n?",
        block,
        text,
        count=1,
        flags=re.DOTALL,
    )
    # Remove forbidden relative import if reintroduced
    text = re.sub(
        r'\nimport \{ FORM_TERMINOLOGY_REQUIRED, getOpenRowSpec \} from "\./integrity-open-row-spec";\n',
        "\n",
        text,
    )
    M1_CANVAS.write_text(text, encoding="utf-8")


def _patch_m1_canvas(inline_block: str) -> None:
    if not M1_CANVAS.is_file():
        print(f"WARN: missing M1 canvas {M1_CANVAS}", file=sys.stderr)
        return
    text = M1_CANVAS.read_text(encoding="utf-8")
    import_re = re.compile(
        r'\nimport \{\n  AGENT_POV_AGENTS,\n  AGENT_POV_FORM_QUESTIONS,\n  AGENT_POV_PHASES,\n  OPEN_FORM_QUESTIONS,\n\} from "\./integrity-form-data\.generated";\n',
    )
    if import_re.search(text):
        text = import_re.sub("\n" + inline_block + "\n", text, count=1)
    elif GEN_BEGIN in text and GEN_END in text:
        text = re.sub(
            re.escape(GEN_BEGIN) + r".*?" + re.escape(GEN_END) + r"\n?",
            inline_block + "\n",
            text,
            count=1,
            flags=re.DOTALL,
        )
    else:
        raise SystemExit(f"FAIL: cannot patch M1 canvas — add markers or import block in {M1_CANVAS}")
    M1_CANVAS.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
