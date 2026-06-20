(function () {
  "use strict";

  const API = window.location.origin;
  const CLIENT_UI_VERSION = "3.4.0";
  const $ = (id) => document.getElementById(id);
  const FOUNDER_SETTINGS_KEY = "chat-unify-founder-v1";
  let state = {
    prompts: { extract: "", unify: "" },
    last_unified: null,
    openExtract: null,
    autoImportDone: false,
    autoStructureDone: false,
    founderText: "",
    reasoningText: "",
    loopSendback: "",
    workOrder: null,
    ordReport: "",
    ordConfidence: null,
    ordRunId: null,
    ordDecision: null,
    ordStats: null,
    founderRunId: null,
  };
  let founderDebounce = null;
  let ordDebounce = null;
  const ORD_SETTINGS_KEY = "chat-unify-ord-v1";
  const LOOP_STAGES = ["language", "reasoning", "proof", "action", "advisor", "critic", "close"];
  const STAGE_WAIT_LABEL = {
    language: "",
    reasoning: "Waiting for Language…",
    proof: "Waiting for Reasoning…",
    action: "Waiting for Proof…",
    advisor: "Waiting for Action…",
    critic: "Waiting for Advisor…",
    close: "Waiting for Critic…",
  };
  const ORD_STAGES = ["parse", "classify", "consistency", "attribution", "simplify", "redflags", "report"];
  const ORD_WAIT_LABEL = {
    parse: "",
    classify: "Waiting for Parser…",
    consistency: "Waiting for Classifier…",
    attribution: "Waiting for Consistency…",
    simplify: "Waiting for Source trace…",
    redflags: "Waiting for Simplifier…",
    report: "Waiting for Red flags…",
  };

  function newRunId(prefix) {
    const hex = [...crypto.getRandomValues(new Uint8Array(6))]
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    return `${prefix}-${hex.slice(0, 12)}`;
  }

  function renderTruthSidebar(json) {
    const sidebar = $("truth-sidebar");
    if (!sidebar) return;

    const atoms =
      json?.atoms ||
      json?.kernel?.atoms ||
      json?.stages?.attribution?.atoms ||
      json?.stages?.classify?.atoms ||
      [];
    const decision = json?.decision || json?.truth_gate || null;
    const stats = json?.stats || json?.kernel_summary || null;
    const issues = json?.stages?.consistency?.issues || [];

    if (!atoms.length && !decision) {
      sidebar.hidden = true;
      return;
    }
    sidebar.hidden = false;

    const runEl = $("truth-sidebar-run");
    if (runEl) runEl.textContent = json?.run_id ? String(json.run_id).slice(0, 18) : "";

    const verdictEl = $("truth-sidebar-verdict");
    if (verdictEl) {
      if (decision?.action) {
        const act = String(decision.action).toLowerCase();
        verdictEl.textContent = act.toUpperCase();
        verdictEl.className = `cu-truth-sidebar-verdict cu-truth-gate-${act}`;
      } else {
        verdictEl.textContent = "PENDING";
        verdictEl.className = "cu-truth-sidebar-verdict";
      }
    }

    const scoreEl = $("truth-sidebar-score");
    if (scoreEl) {
      const ts = decision?.truth_score;
      const reportConf = json?.confidence ?? json?.stages?.report?.confidence;
      const lines = [];
      if (ts != null) lines.push(`Truth gate: ${ts}/100`);
      if (reportConf != null) lines.push(`Report confidence: ${reportConf}/100`);
      scoreEl.textContent = lines.join(" · ") || "";
    }

    const compEl = $("truth-sidebar-components");
    if (compEl) {
      const wc = decision?.inputs?.weighted?.components || decision?.inputs?.stats?.weighted?.components;
      const parts = [];
      if (stats?.checkable_count != null) parts.push(`${stats.checkable_count} checkable`);
      if (stats?.verified != null) parts.push(`${stats.verified} verified`);
      if (stats?.unverified != null && stats.unverified > 0) parts.push(`${stats.unverified} unverified`);
      if (stats?.opinion_count != null && stats.opinion_count > 0) parts.push(`${stats.opinion_count} opinion`);
      if (stats?.disk_mismatch != null && stats.disk_mismatch > 0) parts.push(`${stats.disk_mismatch} mismatch`);
      if (wc) {
        parts.push(
          `disk ${wc.disk_pct}% · consistency ${wc.consistency_pct}% · source ${wc.source_pct}% · heuristic ${wc.heuristic_pct}%`
        );
      }
      compEl.textContent = parts.join(" · ") || "";
    }

    const reasonsEl = $("truth-sidebar-reasons");
    if (reasonsEl) {
      const reasons = [];
      if (decision?.founder_line) reasons.push(decision.founder_line);
      if (decision?.reason && decision.reason !== decision.founder_line) reasons.push(decision.reason);
      const actions = json?.stages?.report?.verify_actions || [];
      actions.slice(0, 3).forEach((a) => reasons.push(`Next: ${a}`));
      issues.slice(0, 2).forEach((i) => reasons.push(i));
      atoms
        .filter((a) => a.disk_status === "mismatch" && a.verify_reason)
        .slice(0, 4)
        .forEach((a) => reasons.push(`${a.id}: ${a.verify_reason}`));
      reasonsEl.innerHTML = reasons.length
        ? reasons.map((r) => `<li>${esc(r)}</li>`).join("")
        : "<li>No blockers yet — finish report stage.</li>";
    }

    const tbody = $("truth-sidebar-atoms-body");
    if (tbody) {
      tbody.innerHTML = atoms
        .map((a) => {
          const st = a.disk_status || "n/a";
          const cls =
            st === "verified"
              ? "cu-atom-verified"
              : st === "mismatch"
                ? "cu-atom-mismatch"
                : st === "opinion" || st === "skip"
                  ? "cu-atom-opinion"
                  : "cu-atom-unverified";
          const ct = a.claim_type || "—";
          const title = esc(a.verify_reason || a.text || "");
          return `<tr><td>${esc(a.id)}</td><td>${esc(ct)}</td><td class="${cls}">${esc(st)}</td><td title="${title}">${esc((a.text || "").slice(0, 56))}</td></tr>`;
        })
        .join("");
    }

    const hint = $("truth-sidebar-hint");
    if (hint) {
      hint.textContent = decision?.dispatch_blocked
        ? "Dispatch blocked — run Founder loop only after you fix or override consciously."
        : "Founder close reads this ORD gate when runs are linked (same session ordRunId).";
    }
  }

  function clearTruthSidebar() {
    const sidebar = $("truth-sidebar");
    if (sidebar) sidebar.hidden = true;
    const tbody = $("truth-sidebar-atoms-body");
    if (tbody) tbody.innerHTML = "";
    const reasonsEl = $("truth-sidebar-reasons");
    if (reasonsEl) reasonsEl.innerHTML = "";
    const verdictEl = $("truth-sidebar-verdict");
    if (verdictEl) {
      verdictEl.textContent = "—";
      verdictEl.className = "cu-truth-sidebar-verdict";
    }
  }

  function renderTruthGate(el, decision) {
    if (!el) return;
    if (!decision || !decision.action) {
      el.hidden = true;
      el.textContent = "";
      el.className = "cu-truth-gate";
      return;
    }
    const action = String(decision.action).toLowerCase();
    el.hidden = false;
    el.className = `cu-truth-gate cu-truth-gate-${action}`;
    const score = decision.truth_score != null ? `${decision.truth_score}/100` : "—";
    const line = decision.founder_line || decision.reason || "";
    const block = decision.dispatch_blocked ? " · dispatch blocked" : "";
    el.innerHTML = `<strong>${esc(action.toUpperCase())}</strong> · score ${esc(score)} — ${esc(line)}${esc(block)}`;
  }

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function toast(msg, ms) {
    const el = document.createElement("div");
    el.className = "cu-toast";
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), ms || 4000);
  }

  async function api(body, opts = {}) {
    const timeoutMs = opts.timeoutMs || 45000;
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      const res = await fetch(`${API}/api/chat-unify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body || { action: "report" }),
        signal: ctrl.signal,
      });
      clearTimeout(timer);
      const text = await res.text();
      try {
        return JSON.parse(text);
      } catch {
        return { ok: false, error: "bad_json", message: text.slice(0, 200) || "Server returned invalid JSON" };
      }
    } catch (err) {
      clearTimeout(timer);
      if (err && err.name === "AbortError") {
        return { ok: false, error: "timeout", message: "Timed out — try again or paste a shorter answer." };
      }
      return { ok: false, error: "network", message: "Connection lost — quit and reopen Chat Unify." };
    }
  }

  function formatExtractOutput(ex) {
    if (!ex) return "";
    const p = ex.parsed || {};
    const parts = [];
    parts.push(`# ${ex.label || p.title || "Chat extract"}`);
    parts.push(`Saved: ${ex.saved_at || "—"} · ${ex.chars || 0} chars`);
    if ((ex.tags || []).length) parts.push(`Tags: ${ex.tags.join(", ")}`);
    if (p.raw_paste) {
      parts.push("\n⚠ RAW CHAT (not structured CHAT EXTRACT)");
      if (p.hint) parts.push(p.hint);
    }
    if (p.rollup) parts.push(`\n## Summary\n${p.rollup}`);
    if ((p.decisions || []).length) {
      parts.push("\n## Decisions");
      p.decisions.forEach((row) => parts.push(`- ${row.join(" · ")}`));
    }
    if ((p.threads || []).length) {
      parts.push("\n## Threads");
      p.threads.forEach((row) => parts.push(`- ${row.join(" · ")}`));
    }
    if ((p.facts || []).length) {
      parts.push("\n## Key lines");
      p.facts.slice(0, 30).forEach((f) => parts.push(`- ${f}`));
    }
    parts.push("\n## Full saved text\n");
    parts.push(ex.text || "");
    return parts.join("\n");
  }

  function showExtractOutput(ex) {
    state.openExtract = ex;
    const out = $("extract-output");
    const title = $("output-title");
    const hint = $("output-hint");
    if (title) title.textContent = ex.label || ex.parsed?.title || ex.id || "Extract";
    if (hint) {
      if (ex.parsed?.raw_paste) {
        hint.textContent = "Raw chat — tap Fix this extract → run prompt in Cursor, then re-save.";
      } else if (ex.weak || (!ex.parsed?.decisions?.length && !ex.parsed?.threads?.length)) {
        hint.textContent = "Weak extract (0 decisions, 0 threads) — merge will warn until structured.";
      } else {
        hint.textContent = "Structured CHAT EXTRACT — ready to merge.";
      }
    }
    if (out) out.textContent = formatExtractOutput(ex);
    $("output-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function openExtract(id) {
    const json = await api({ action: "get_extract", id });
    if (json.ok && json.extract) {
      showExtractOutput(json.extract);
      toast(`Opened «${json.extract.label}»`);
    } else {
      toast(json.error || "Could not open extract", 5000);
    }
  }

  async function fixExtract(id) {
    const row = await api({ action: "get_extract", id });
    const ex = row.extract;
    if (row.ok && ex && (ex.weak || ex.raw_paste || ex.parsed?.raw_paste)) {
      const structured = await api({ action: "structure_one", id });
      if (structured.ok && !structured.still_weak) {
        toast("Structured locally — ready to merge");
        await load({ skipAutoImport: true, skipAutoStructure: true });
        await openExtract(id);
        return;
      }
    }
    await sendCursor("send_extract_prompt");
    toast("Extract prompt sent — run in Cursor, then re-save this chat");
    if (id) await openExtract(id);
  }

  async function structureOne(id) {
    const json = await api({ action: "structure_one", id });
    if (json.ok) {
      toast(json.still_weak ? "Still weak — try Fix for Cursor prompt" : "Structured — ready to merge");
      await load({ skipAutoImport: true, skipAutoStructure: true });
      if (id) await openExtract(id);
    } else {
      toast(json.message || json.error || "Structure failed", 5000);
    }
  }

  function renderTagSuggestions(tags) {
    const dl = $("tag-suggestions");
    if (!dl) return;
    dl.innerHTML = (tags || []).map((t) => `<option value="${esc(t)}"></option>`).join("");
  }

  function renderTranscriptSelect(candidates) {
    const sel = $("select-transcript");
    if (!sel) return;
    const cur = sel.value;
    sel.innerHTML =
      '<option value="">Import transcript…</option>' +
      (candidates || [])
        .map((c) => `<option value="${esc(c.path)}">${esc(c.name)} · ${esc((c.mtime || "").slice(0, 10))}</option>`)
        .join("");
    if (cur) sel.value = cur;
  }

  function resetOutputPanel() {
    state.openExtract = null;
    if ($("extract-output")) $("extract-output").textContent = "No output yet — tap Open on a library item.";
    if ($("output-title")) $("output-title").textContent = "select a library item";
    if ($("output-hint")) $("output-hint").textContent = "Saved text and parsed summary appear here when you open a library item.";
  }

  function renderLibrary(extracts) {
    const list = $("library-list");
    if (!list) return;
    if (!extracts || !extracts.length) {
      list.innerHTML = "<li class='cu-empty'><em>No extracts yet — paste and save in step 1.</em></li>";
      return;
    }
    list.innerHTML = extracts
      .map((e) => {
        const tags = (e.tags || []).slice(0, 2).map((t) => `<span class="cu-tag-pill">${esc(t)}</span>`).join("");
        const imported = e.imported_from ? ' <span class="cu-import-tag">transcript</span>' : "";
        const badges =
          (e.raw_paste ? ' <span class="cu-raw-tag">raw</span>' : "") +
          (e.weak ? ' <span class="cu-weak-tag">weak</span>' : ' <span class="cu-ready-tag">ready</span>');
        return `<li class="cu-lib-row">
          <div class="cu-lib-body" data-open="${esc(e.id)}" role="button" tabindex="0">
            <div class="cu-lib-title">${esc(e.label || e.title || e.id)}${badges}${imported} ${tags}</div>
            <div class="cu-lib-meta">${esc(e.decision_count || 0)} decisions · ${esc(e.thread_count || 0)} threads · ${esc(e.chars || 0)} chars · archive: ${esc(e.archive || "?")}</div>
          </div>
          <div class="cu-lib-btns">
            <button type="button" class="cu-btn cu-btn-sm cu-btn-primary" data-open="${esc(e.id)}">Open</button>
            ${e.weak || e.raw_paste ? `<button type="button" class="cu-btn cu-btn-sm cu-btn-gold" data-structure="${esc(e.id)}">Structure</button>` : ""}
            <button type="button" class="cu-btn cu-btn-sm cu-btn-gold" data-fix="${esc(e.id)}">Fix</button>
            <button type="button" class="cu-btn cu-btn-sm cu-btn-danger" data-del="${esc(e.id)}">Delete</button>
          </div>
        </li>`;
      })
      .join("");
    list.querySelectorAll("[data-open]").forEach((el) => {
      const open = () => openExtract(el.dataset.open);
      el.addEventListener("click", open);
      el.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          open();
        }
      });
    });
    list.querySelectorAll("[data-fix]").forEach((btn) => {
      btn.addEventListener("click", async (ev) => {
        ev.stopPropagation();
        await fixExtract(btn.dataset.fix);
      });
    });
    list.querySelectorAll("[data-structure]").forEach((btn) => {
      btn.addEventListener("click", async (ev) => {
        ev.stopPropagation();
        await structureOne(btn.dataset.structure);
      });
    });
    list.querySelectorAll("[data-del]").forEach((btn) => {
      btn.addEventListener("click", async (ev) => {
        ev.stopPropagation();
        if (!confirm("Delete this extract?")) return;
        const json = await api({ action: "delete_extract", id: btn.dataset.del });
        if (json.ok) {
          toast("Deleted");
          if (state.openExtract?.id === btn.dataset.del) resetOutputPanel();
          load();
        } else toast(json.error || "Delete failed");
      });
    });
  }

  function renderContradictions(data) {
    const list = $("contradiction-list");
    const meta = $("contradiction-meta");
    const items = (data && data.contradictions) || [];
    const stat = $("stat-contradictions");
    const crit = items.filter((c) => c.severity === "critical").length;
    const high = items.filter((c) => c.severity === "high").length;
    if (stat) {
      stat.textContent = items.length
        ? `${crit ? crit + " critical · " : ""}${high ? high + " high · " : ""}${items.length} issue${items.length === 1 ? "" : "s"}`
        : "0 issues";
    }
    if (meta) {
      meta.textContent = items.length
        ? `${items.length} issue(s) found across ${data.extract_count || "?"} chat(s)`
        : "No cross-chat contradictions detected by local rules.";
    }
    if (!list) return;
    if (!items.length) {
      list.innerHTML = '<li class="sev-low"><em>Clean merge — still review decisions before archiving chats.</em></li>';
      return;
    }
    list.innerHTML = items
      .map(
        (c) => `<li class="sev-${esc(c.severity || "medium")}">
          <strong>[${esc((c.severity || "").toUpperCase())}]</strong> ${esc(c.kind)} — ${esc(c.detail)}
          <div class="cu-lib-meta">${esc(c.source)}</div>
        </li>`
      )
      .join("");
  }

  function renderBrief(last) {
    const pre = $("unified-brief");
    const summary = $("merge-summary");
    if (!pre) return;
    const text = (last && last.unified_brief) || "";
    pre.textContent = text || "Save extracts → tap Merge all to build your unified brief.";
    if (summary) {
      if (last && last.ok) {
        summary.hidden = false;
        const receipt = last.receipt?.path ? ` · receipt saved` : "";
        summary.innerHTML = `<span class="cu-merge-pill">${esc(last.extract_count)} chats merged</span>
          <span class="cu-merge-pill">${esc(last.contradiction_count)} contradictions</span>
          <span class="cu-merge-pill">${(text || "").length} chars brief${receipt}</span>`;
      } else {
        summary.hidden = true;
      }
    }
  }

  function renderStatus(json) {
    const el = $("status-line");
    const live = $("live-badge");
    if (!json.ok) {
      if (el) {
        el.textContent = "Offline — double-click Chat Unify again.";
        el.classList.add("cu-status-error");
      }
      if (live) live.classList.remove("cu-badge-live");
      return;
    }
    const n = (json.extracts || []).length;
    const weak = (json.extracts || []).filter((e) => e.weak).length;
    const ready = n - weak;
    const merged = json.last_unified ? " · merged" : "";
    const qual = json.quality?.ok ? " · merge-ready" : weak ? ` · ${weak} need structure` : "";
    const wire = json.n8n_wire?.wired ? " · n8n wired" : " · n8n not wired";
    const ai = json.ai_api;
    const aiLine = ai?.openrouter_ready || ai?.gemini_direct_ready
      ? ` · AI ${ai.auto_provider || "ready"}`
      : " · AI keys missing";
    if (el) {
      const loops = $("tab-ord") ? " · Founder + ORD" : " · ORD tab missing";
      el.textContent = `Connected · UI ${CLIENT_UI_VERSION}${loops} · ${n} extract${n === 1 ? "" : "s"} · ${ready} ready${qual}${merged}${wire}${aiLine}`;
      el.classList.remove("cu-status-error");
    }
    if (live) live.classList.add("cu-badge-live");
    const issues = (json.contradictions || []).length;
    const set = (id, text) => {
      const node = $(id);
      if (node) node.textContent = text;
    };
    set("tile-extracts", String(n));
    set("tile-issues", String(issues));
    set("tile-ready", String(ready));
    set("tile-brief", json.last_unified ? "yes" : "—");
    const sub = $("stat-contradictions");
    if (sub) sub.textContent = `${issues} issue${issues === 1 ? "" : "s"}`;
  }

  async function autoImportLatestTranscript() {
    if (state.autoImportDone) return null;
    state.autoImportDone = true;
    try {
      const json = await api({
        action: "import_latest_transcript",
        tags: ["THREAD-CHAT-CONSOLIDATION"],
      });
      if (json.ok && !json.skipped && json.extract) {
        toast(`Auto-imported «${json.extract.label}»`);
        return json.extract;
      }
      if (json.skipped && json.extract) {
        return json.extract;
      }
    } catch {
      /* non-fatal */
    }
    return null;
  }

  async function structureAll() {
    const json = await api({ action: "structure_all" });
    if (json.ok) {
      toast(`Structured ${json.upgraded_count || 0} extract(s)`);
      await load({ skipAutoImport: true, skipAutoStructure: true });
      if (json.quality?.ok) {
        toast("Merge-ready — tap Merge all & scan");
      }
    } else {
      toast(json.message || json.error || "Structure failed", 5000);
    }
  }

  async function autoStructureWeak() {
    if (state.autoStructureDone) return;
    state.autoStructureDone = true;
    try {
      const json = await api({ action: "structure_all" });
      if (json.ok && json.upgraded_count) {
        toast(`Auto-structured ${json.upgraded_count} extract(s)`);
      }
    } catch {
      /* non-fatal */
    }
  }

  async function load(opts = {}) {
    try {
      if (!opts.skipAutoImport) {
        await autoImportLatestTranscript();
      }
      if (!opts.skipAutoStructure) {
        const rep = await api({ action: "report" });
        const weak = (rep.extracts || []).filter((e) => e.weak).length;
        if (weak) {
          state.autoStructureDone = true;
          const structured = await api({ action: "structure_all" });
          if (structured.ok && structured.upgraded_count) {
            toast(`Auto-structured ${structured.upgraded_count} extract(s)`);
          }
        } else {
          state.autoStructureDone = true;
        }
      }
      const json = await api({ action: "report" });
      if (!json.ok) {
        toast(json.error || "Could not load");
        renderStatus({ ok: false });
        return;
      }
      state.prompts = json.prompts || state.prompts;
      state.last_unified = json.last_unified;
      renderTagSuggestions(json.suggested_tags);
      renderTranscriptSelect(json.transcript_candidates);
      const n = (json.extracts || []).length;
      const tileExt = $("tile-extracts");
      if (tileExt) tileExt.textContent = String(n);
      renderLibrary(json.extracts);
      renderStatus(json);
      const ids = new Set((json.extracts || []).map((e) => e.id));
      if (state.openExtract?.id && !ids.has(state.openExtract.id)) resetOutputPanel();
      if (json.last_unified) {
        renderContradictions(json.last_unified);
        renderBrief(json.last_unified);
      } else {
        renderContradictions(null);
        renderBrief(null);
      }
    } catch {
      renderStatus({ ok: false });
      toast("Connection lost — is the app running?", 5000);
    }
  }

  function readTags() {
    const raw = ($("input-tags")?.value || "").trim();
    if (!raw) return [];
    return raw.split(/[,#\s]+/).filter(Boolean);
  }

  async function saveExtract() {
    const text = ($("input-paste")?.value || "").trim();
    const label = ($("input-label")?.value || "").trim();
    const tags = readTags();
    if (!text) {
      toast("Paste a CHAT EXTRACT first");
      return;
    }
    const json = await api({ action: "save_extract", label, text, tags });
    if (json.ok) {
      if (json.duplicate || json.skipped) {
        toast(json.message || `Already saved as «${json.extract?.label || "extract"}»`);
        if (json.extract?.id) await openExtract(json.extract.id);
        return;
      }
      toast(`Saved «${json.extract.label}»`);
      if ($("input-paste")) $("input-paste").value = "";
      if ($("input-label")) $("input-label").value = "";
      await load();
      showExtractOutput(json.extract);
    } else toast(json.message || json.error || "Save failed", 5000);
  }

  async function unifyAll(force) {
    const json = await api({ action: "unify", force: !!force });
    if (json.ok) {
      state.last_unified = json;
      const n8n = json.n8n_notify;
      const n8nLine = n8n?.ok ? " · n8n notified" : n8n ? " · n8n notify skipped" : "";
      toast(`Merged ${json.extract_count} chat(s) · ${json.contradiction_count} contradiction(s)${n8nLine}`);
      renderContradictions(json);
      renderBrief(json);
      await load();
      $("panel-brief")?.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    if (json.error === "merge_quality_gate" && !force) {
      const weak = (json.quality?.weak || []).map((w) => w.label).join(", ");
      const go = confirm(
        `${json.message}\n\nWeak extracts: ${weak || "?"}\n\nMerge anyway with incomplete structure?`
      );
      if (go) return unifyAll(true);
      toast("Merge cancelled — fix extracts first", 5000);
      return;
    }
    toast(json.message || json.error || "Merge failed", 5000);
  }

  async function exportBrief() {
    const json = await api({ action: "export_brief" });
    if (json.ok) {
      toast(`Exported → ${(json.path || "").split("/").pop() || "brief.md"}`);
    } else {
      toast(json.message || json.error || "Export failed", 5000);
    }
  }

  async function importTranscript() {
    const path = $("select-transcript")?.value || "";
    if (!path) {
      toast("Pick a transcript first");
      return;
    }
    const json = await api({ action: "import_transcript", path, tags: readTags() });
    if (json.ok) {
      toast(`Imported «${json.extract.label}»`);
      await load();
      showExtractOutput(json.extract);
    } else {
      toast(json.message || json.error || "Import failed", 5000);
    }
  }

  async function sendCursor(action) {
    const json = await api({ action });
    if (json.ok || json.injected || json.clipboard_fallback) {
      toast(json.message || "Sent to Cursor — check your chat");
    } else {
      toast(json.message || json.error || "Send failed — try Copy instead", 6000);
    }
  }

  function copyText(text, label) {
    if (!text) {
      toast("Nothing to copy");
      return;
    }
    navigator.clipboard.writeText(text).then(
      () => toast(`Copied ${label}`),
      () => toast("Copy failed")
    );
  }

  function applyDroppedFile(file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const text = String(reader.result || "").trim();
      if ($("input-paste")) $("input-paste").value = text;
      if ($("input-label") && !$("input-label").value) {
        $("input-label").value = file.name.replace(/\.[^.]+$/, "").slice(0, 60);
      }
      toast(`Loaded ${file.name} — review and Save`);
    };
    reader.readAsText(file);
  }

  function bindDropzone() {
    const zone = $("dropzone");
    const paste = $("input-paste");
    if (!zone) return;
    const over = (ev) => {
      ev.preventDefault();
      zone.classList.add("cu-dropzone-active");
    };
    const leave = () => zone.classList.remove("cu-dropzone-active");
    zone.addEventListener("dragover", over);
    zone.addEventListener("dragleave", leave);
    zone.addEventListener("drop", (ev) => {
      ev.preventDefault();
      leave();
      const file = ev.dataTransfer?.files?.[0];
      if (file) applyDroppedFile(file);
    });
    if (paste) {
      paste.addEventListener("dragover", (ev) => ev.preventDefault());
      paste.addEventListener("drop", (ev) => {
        ev.preventDefault();
        const file = ev.dataTransfer?.files?.[0];
        if (file) applyDroppedFile(file);
      });
    }
  }

  async function wireN8n() {
    const json = await api({ action: "wire_n8n", import_cursor: true, limit: 2 });
    if (json.ok) {
      toast(json.founder_line || "n8n wired");
      await load();
    } else {
      toast(json.error || json.founder_line || "Wire failed", 5000);
    }
  }

  async function syncCursor() {
    const json = await api({ action: "sync_cursor", limit: 3 });
    if (json.ok) {
      toast(`Imported ${json.imported_count || 0} Cursor transcript(s)`);
      await load();
    } else {
      toast(json.error || json.message || "Import failed", 5000);
    }
  }

  function setLoopStageMeta(stage, meta) {
    const el = $(`loop-meta-${stage}`);
    if (!el) return;
    el.textContent = meta?.text || "";
    el.className = "cu-machine-meta" + (meta?.className ? ` ${meta.className}` : "");
  }

  function machineMetaForStage(sid, st, json) {
    const method = st?.method || "";
    if (!st?.text && !st?.ok) return { text: "idle", className: "" };
    if (sid === "language") {
      return { text: method === "ai" || method === "openrouter" ? "AI" : "rules", className: method.includes("ai") || method === "openrouter" ? "cu-meta-ai" : "cu-meta-ok" };
    }
    if (sid === "reasoning") {
      return { text: method || "rules", className: method.includes("ai") || method === "openrouter" ? "cu-meta-ai" : "" };
    }
    if (sid === "proof") {
      const ev = st?.eval_1b || {};
      if (!ev.present) return { text: "no Eval-1b", className: "cu-meta-warn" };
      if (ev.mode === "live" && ev.live_ok) return { text: "Eval live OK", className: "cu-meta-ok" };
      if (ev.mode === "live" && ev.live_ok === false) return { text: "Eval live FAIL", className: "cu-meta-warn" };
      return { text: `Eval ${ev.mode || "?"}`, className: ev.ok ? "cu-meta-ok" : "cu-meta-warn" };
    }
    if (sid === "action") {
      return { text: st?.one_action ? "1 step" : "rules", className: "cu-meta-ok" };
    }
    if (sid === "advisor" || sid === "critic") {
      const ai = method.includes("ai") || method === "openrouter";
      return { text: ai ? "AI" : "rules only", className: ai ? "cu-meta-ai" : "cu-meta-warn" };
    }
    if (sid === "close") {
      const wo = json?.work_order || st?.work_order;
      if (wo?.dispatch_blocked) return { text: "blocked", className: "cu-meta-warn" };
      if (wo?.id) return { text: wo.id.replace("wo-cu-", "").slice(0, 8), className: "cu-meta-ok" };
      return { text: "proposed", className: "" };
    }
    return { text: method || "done", className: "cu-meta-ok" };
  }

  function formatCloseDisplay(text, workOrder) {
    if (!text) return "—";
    const idx = text.indexOf("Work order (proposed");
    if (idx > 0) {
      const human = text.slice(0, idx).trim();
      const woId = workOrder?.id || "proposed";
      const blocked = workOrder?.dispatch_blocked ? "\n⚠ Dispatch blocked until Eval-1b proof passes." : "";
      return `${human}\n\n[Work order ${woId} on disk — tap WO to copy JSON]${blocked}`;
    }
    return text;
  }

  function setLoopStageState(stage, state, text, opts = {}) {
    const pre = $(`loop-out-${stage}`);
    const li = document.querySelector(`.cu-loop-step[data-stage="${stage}"]`);
    if (li) {
      li.classList.toggle("cu-loop-active", state === "running");
      li.classList.toggle("cu-loop-done", state === "done");
      li.classList.toggle("cu-loop-waiting", state === "waiting");
    }
    if (!pre) return;
    if (state === "running") {
      pre.textContent = "Running…";
      pre.title = "";
      return;
    }
    if (state === "waiting") {
      pre.textContent = text || "Waiting…";
      pre.title = "";
      return;
    }
    let display = text;
    if (stage === "close" && text && opts.workOrder) {
      display = formatCloseDisplay(text, opts.workOrder);
    }
    pre.textContent = display || "—";
    pre.title = (text || "").slice(0, 4000);
  }

  function resetLoopPipelineUI() {
    LOOP_STAGES.forEach((sid, i) => {
      if (i === 0) {
        setLoopStageState(sid, "idle", "—");
        setLoopStageMeta(sid, { text: "", className: "" });
      } else {
        setLoopStageState(sid, "waiting", STAGE_WAIT_LABEL[sid]);
        setLoopStageMeta(sid, { text: "wait", className: "" });
      }
    });
  }

  function applyLoopProgress(progress) {
    const current = progress.current_stage;
    const completed = new Set(progress.completed_stages || []);
    const stages = progress.stages || {};
    LOOP_STAGES.forEach((sid) => {
      const st = stages[sid] || {};
      if (completed.has(sid) && (st.text || st.ok)) {
        setLoopStageState(sid, "done", st.text || "", {
          workOrder: sid === "close" ? st.work_order || progress.work_order : null,
        });
        setLoopStageMeta(sid, machineMetaForStage(sid, st, progress));
      } else if (sid === current) {
        setLoopStageState(sid, "running", "");
        setLoopStageMeta(sid, { text: "…", className: "" });
      } else if (!completed.has(sid)) {
        setLoopStageState(sid, "waiting", STAGE_WAIT_LABEL[sid] || "Waiting…");
        setLoopStageMeta(sid, { text: "wait", className: "" });
      }
    });
    const stat = $("loop-status");
    if (stat && progress.running && current) {
      stat.textContent = `Running ${current}… (${completed.size}/${LOOP_STAGES.length} done)`;
    }
  }

  function renderLoop(json) {
    const stages = json?.stages || {};
    LOOP_STAGES.forEach((sid) => {
      const st = stages[sid] || {};
      setLoopStageState(sid, st.text ? "done" : "idle", st.text || "—", {
        workOrder: sid === "close" ? json?.work_order || st?.work_order : null,
      });
      setLoopStageMeta(sid, machineMetaForStage(sid, st, json));
    });
    state.founderText = stages.language?.text || "";
    state.reasoningText = stages.reasoning?.text || "";
    state.loopSendback = json?.sendback || stages.close?.sendback || "";
    state.workOrder = json?.work_order || stages.close?.work_order || null;
    const status = $("loop-status");
    if (status) {
      const methods = LOOP_STAGES.map((s) => stages[s]?.method).filter(Boolean);
      const wo = state.workOrder;
      const woLine = wo?.id ? ` · work-order ${wo.id}` : "";
      const evalLine = stages.proof?.eval_1b?.present
        ? ` · Eval-1b ${stages.proof.eval_1b.mode || "?"}`
        : " · Eval-1b missing";
      const tg = json?.truth_gate;
      const tgLine = tg?.action ? ` · truth gate ${String(tg.action).toUpperCase()}` : "";
      const blockLine = wo?.dispatch_blocked ? " · dispatch blocked" : "";
      status.textContent = json?.ok
        ? `Pipeline complete · v${json.version || "2.9"}${woLine}${evalLine}${tgLine}${blockLine}`
        : "";
    }
    renderTruthGate($("founder-truth-gate"), json?.truth_gate || null);
    const ordLink = $("founder-ord-link");
    if (ordLink) {
      const linked = state.ordRunId || json?.ord_run_id || json?.kernel?.ord_run_id;
      if (linked) {
        ordLink.hidden = false;
        const tg = json?.truth_gate;
        const tgLine = tg?.action ? ` · gate ${String(tg.action).toUpperCase()} ${tg.truth_score || "?"}/100` : "";
        ordLink.textContent = `Linked ORD run: ${String(linked).slice(0, 20)}${tgLine}`;
      } else {
        ordLink.hidden = true;
        ordLink.textContent = "";
      }
    }
  }

  async function runStagePipeline(opts) {
    const {
      stages,
      action,
      draft,
      context,
      useAi,
      resetUI,
      setStage,
      setMeta,
      metaFor,
      waitLabels,
      statusEl,
      fromAuto,
      doneLabel,
      runIdPrefix,
      runIdStateKey,
      ordRunId,
      onStageComplete,
    } = opts;

    resetUI();
    let runId = newRunId(runIdPrefix || "cu");
    if (runIdStateKey) state[runIdStateKey] = runId;
    let lastJson = null;

    for (let i = 0; i < stages.length; i++) {
      const sid = stages[i];
      stages.forEach((other, j) => {
        if (j > i) {
          setStage(other, "waiting", waitLabels[other] || "Waiting…");
          setMeta(other, { text: "wait", className: "" });
        }
      });
      setStage(sid, "running", "");
      if (statusEl) {
        statusEl.textContent = `Step ${i + 1}/${stages.length}: ${sid} · run ${runId.slice(0, 16)}…`;
      }

      const payload = {
        action,
        stage: sid,
        text: draft,
        founder_message: context,
        use_ai: useAi,
        run_id: runId,
        write_receipt: i === stages.length - 1,
      };
      if (ordRunId) payload.ord_run_id = ordRunId;

      const json = await api(payload, { timeoutMs: 120000 });

      if (!json.ok) {
        setStage(sid, "idle", json.message || json.error || "Blocked");
        if (statusEl) statusEl.textContent = json.message || "Pipeline blocked";
        if (!fromAuto) toast(json.message || json.error || "Stage blocked", 6000);
        return null;
      }

      runId = json.run_id || runId;
      if (runIdStateKey) state[runIdStateKey] = runId;

      const st = (json.stages || {})[sid] || {};
      setStage(sid, "done", st.text || "", {
        workOrder: sid === "close" ? json.work_order : null,
      });
      setMeta(sid, metaFor(sid, st, json));
      lastJson = json;
      if (typeof onStageComplete === "function") onStageComplete(json, sid);
      await new Promise((r) => setTimeout(r, 280));
    }

    if (statusEl && lastJson) {
      statusEl.textContent = doneLabel(lastJson) || "Pipeline complete";
    }
    return lastJson;
  }

  async function runFullLoop(opts = {}) {
    const draft = ($("input-founder-draft")?.value || "").trim();
    const context = ($("input-founder-context")?.value || "").trim();
    if (!draft) {
      if (!opts.fromAuto) toast("Paste the agent answer first");
      return null;
    }

    const json = await runStagePipeline({
      stages: LOOP_STAGES,
      action: "founder_loop_stage",
      draft,
      context,
      useAi: !!$("founder-use-ai")?.checked,
      resetUI: resetLoopPipelineUI,
      setStage: setLoopStageState,
      setMeta: setLoopStageMeta,
      metaFor: machineMetaForStage,
      waitLabels: STAGE_WAIT_LABEL,
      statusEl: $("loop-status"),
      fromAuto: opts.fromAuto,
      runIdPrefix: "cu",
      runIdStateKey: "founderRunId",
      ordRunId: state.ordRunId || null,
      doneLabel: (row) => {
        const wo = row.work_order;
        const woLine = wo?.id ? ` · work-order ${wo.id}` : "";
        return `Founder loop complete · sequential · v${row.version || "2.8"}${woLine}`;
      },
    });

    if (!json) return null;
    renderLoop(json);
    if (!opts.fromAuto) toast("Founder loop complete (sequential)");
    if ($("founder-auto-send")?.checked && state.loopSendback) {
      await sendLoopToCursor({ silent: true });
    }
    return json;
  }

  async function sendLoopToCursor(opts = {}) {
    const text = (state.loopSendback || $(`loop-out-close`)?.textContent || "").trim();
    if (!text || text === "—" || text.startsWith("Running")) {
      if (!opts.silent) toast("Run loop first — no close order");
      return;
    }
    const json = await api({ action: "send_founder_reply", text });
    if (json.ok || json.clipboard_fallback) {
      toast(json.message || "Close order sent to Cursor");
    } else if (!opts.silent) {
      toast(json.message || json.error || "Send failed", 6000);
    }
  }

  function clearFounderLanguage() {
    if ($("input-founder-draft")) $("input-founder-draft").value = "";
    if ($("input-founder-context")) $("input-founder-context").value = "";
    resetLoopPipelineUI();
    const stat = $("loop-status");
    if (stat) stat.textContent = "";
    state.founderText = "";
    state.reasoningText = "";
    state.loopSendback = "";
    state.workOrder = null;
    state.founderRunId = null;
    renderTruthGate($("founder-truth-gate"), null);
  }

  /* —— ORD loop (reverse debug) —— */
  function setOrdStageMeta(stage, meta) {
    const el = $(`ord-meta-${stage}`);
    if (!el) return;
    el.textContent = meta?.text || "";
    el.className = "cu-machine-meta" + (meta?.className ? ` ${meta.className}` : "");
  }

  function ordMetaForStage(sid, st, json) {
    const method = st?.method || "";
    if (sid === "parse" && st?.parsed) {
      const p = st.parsed;
      return { text: `${p.line_count || 0} lines`, className: "cu-meta-ok" };
    }
    if (sid === "classify") {
      const n = st?.atom_count ?? st?.atoms?.length ?? 0;
      if (n) return { text: `${n} atoms`, className: "cu-meta-ok" };
      const buckets = st?.buckets;
      const typed = buckets ? Object.values(buckets).reduce((a, b) => a + (b?.length || 0), 0) : 0;
      return { text: `${typed} typed`, className: "cu-meta-ok" };
    }
    if (sid === "consistency") {
      const n = st?.issues?.length || 0;
      const c = st?.stats?.contradictions ?? json?.stats?.contradictions;
      const edge = c != null ? ` · ${c}↔` : "";
      return { text: n ? `${n} issues${edge}` : `clean${edge}`, className: n ? "cu-meta-warn" : "cu-meta-ok" };
    }
    if (sid === "attribution") {
      const n = st?.atoms?.length || json?.atoms?.length || 0;
      const ai = method.includes("ai") || method.includes("openrouter");
      return { text: n ? `${n} tagged` : ai ? "AI" : "rules", className: ai ? "cu-meta-ai" : "cu-meta-ok" };
    }
    if (sid === "simplify") {
      return { text: method.includes("ai") ? "AI plain" : "rules", className: method.includes("ai") ? "cu-meta-ai" : "cu-meta-ok" };
    }
    if (sid === "redflags") {
      const n = st?.flags?.length || 0;
      return { text: `${n} flags`, className: n > 2 ? "cu-meta-warn" : "cu-meta-ok" };
    }
    if (sid === "report") {
      const c = json?.confidence ?? st?.confidence;
      const stt = json?.stats || st?.stats || json?.kernel_summary;
      if (stt?.verified != null) {
        return {
          text: `${stt.verified}✓ ${stt.disk_mismatch || 0}✗`,
          className: (stt.disk_mismatch || 0) > 0 ? "cu-meta-warn" : "cu-meta-ok",
        };
      }
      if (c != null) return { text: `${c}/100`, className: c >= 60 ? "cu-meta-ok" : "cu-meta-warn" };
      return { text: "done", className: "cu-meta-ok" };
    }
    return { text: method || "done", className: "" };
  }

  function setOrdStageState(stage, stateName, text) {
    const pre = $(`ord-out-${stage}`);
    const li = document.querySelector(`.cu-loop-step[data-ord-stage="${stage}"]`);
    if (li) {
      li.classList.toggle("cu-loop-active", stateName === "running");
      li.classList.toggle("cu-loop-done", stateName === "done");
      li.classList.toggle("cu-loop-waiting", stateName === "waiting");
    }
    if (!pre) return;
    if (stateName === "running") {
      pre.textContent = "Running…";
      return;
    }
    if (stateName === "waiting") {
      pre.textContent = text || "Waiting…";
      return;
    }
    pre.textContent = text || "—";
    pre.title = (text || "").slice(0, 4000);
  }

  function resetOrdPipelineUI() {
    ORD_STAGES.forEach((sid, i) => {
      if (i === 0) {
        setOrdStageState(sid, "idle", "—");
        setOrdStageMeta(sid, { text: "", className: "" });
      } else {
        setOrdStageState(sid, "waiting", ORD_WAIT_LABEL[sid]);
        setOrdStageMeta(sid, { text: "wait", className: "" });
      }
    });
  }

  function applyOrdProgress(progress) {
    const current = progress.current_stage;
    const completed = new Set(progress.completed_stages || []);
    const stages = progress.stages || {};
    ORD_STAGES.forEach((sid) => {
      const st = stages[sid] || {};
      if (completed.has(sid) && (st.text || st.ok)) {
        setOrdStageState(sid, "done", st.text || "");
        setOrdStageMeta(sid, ordMetaForStage(sid, st, progress));
      } else if (sid === current) {
        setOrdStageState(sid, "running", "");
        setOrdStageMeta(sid, { text: "…", className: "" });
      } else if (!completed.has(sid)) {
        setOrdStageState(sid, "waiting", ORD_WAIT_LABEL[sid] || "Waiting…");
        setOrdStageMeta(sid, { text: "wait", className: "" });
      }
    });
    const stat = $("ord-status");
    if (stat && progress.running && current) {
      stat.textContent = `ORD · ${current}… (${completed.size}/${ORD_STAGES.length})`;
    }
  }

  function renderOrd(json) {
    const stages = json?.stages || {};
    ORD_STAGES.forEach((sid) => {
      const st = stages[sid] || {};
      setOrdStageState(sid, st.text ? "done" : "idle", st.text || "—");
      setOrdStageMeta(sid, ordMetaForStage(sid, st, json));
    });
    state.ordRunId = json?.run_id || state.ordRunId;
    state.ordReport = stages.report?.text || "";
    state.ordConfidence = json?.confidence ?? stages.report?.confidence ?? null;
    state.ordDecision = json?.decision || json?.truth_gate || stages.report?.decision || null;
    state.ordStats = json?.stats || stages.report?.stats || json?.kernel_summary || null;
    const stat = $("ord-status");
    if (stat && json?.ok) {
      const conf = state.ordConfidence != null ? ` · confidence ${state.ordConfidence}/100` : "";
      const rid = json.run_id ? ` · run ${String(json.run_id).slice(0, 14)}` : "";
      const dg = state.ordDecision?.action ? ` · ${String(state.ordDecision.action).toUpperCase()}` : "";
      const counts = state.ordStats
        ? ` · ${state.ordStats.verified || 0} verified · ${state.ordStats.disk_mismatch || 0} mismatch`
        : "";
      stat.textContent = `ORD complete · v${json.version || "0.3"}${conf}${dg}${counts}${rid}`;
    }
    renderTruthGate($("ord-truth-gate"), state.ordDecision);
    renderTruthSidebar(json);
  }

  async function runOrdLoop(opts = {}) {
    const draft = ($("input-ord-draft")?.value || "").trim();
    const context = ($("input-ord-context")?.value || "").trim();
    if (!draft) {
      if (!opts.fromAuto) toast("Paste AI output first");
      return null;
    }

    const json = await runStagePipeline({
      stages: ORD_STAGES,
      action: "ord_loop_stage",
      draft,
      context,
      useAi: !!$("ord-use-ai")?.checked,
      resetUI: resetOrdPipelineUI,
      setStage: setOrdStageState,
      setMeta: setOrdStageMeta,
      metaFor: ordMetaForStage,
      waitLabels: ORD_WAIT_LABEL,
      statusEl: $("ord-status"),
      fromAuto: opts.fromAuto,
      runIdPrefix: "ord",
      runIdStateKey: "ordRunId",
      onStageComplete: (row, sid) => {
        if (sid === "consistency" || sid === "report") renderTruthSidebar(row);
      },
      doneLabel: (row) => {
        const conf = row.confidence != null ? ` · confidence ${row.confidence}/100` : "";
        const dg = row.decision?.action ? ` · ${String(row.decision.action).toUpperCase()}` : "";
        return `ORD complete · sequential · v${row.version || "0.2"}${conf}${dg}`;
      },
    });

    if (!json) return null;
    renderOrd(json);
    if (!opts.fromAuto) toast("ORD loop complete (sequential)");
    return json;
  }

  function clearOrd() {
    if ($("input-ord-draft")) $("input-ord-draft").value = "";
    if ($("input-ord-context")) $("input-ord-context").value = "";
    resetOrdPipelineUI();
    const stat = $("ord-status");
    if (stat) stat.textContent = "";
    state.ordReport = "";
    state.ordConfidence = null;
    state.ordRunId = null;
    state.ordDecision = null;
    state.ordStats = null;
    renderTruthGate($("ord-truth-gate"), null);
    clearTruthSidebar();
  }

  function loadOrdSettings() {
    try {
      const s = JSON.parse(localStorage.getItem(ORD_SETTINGS_KEY) || "{}");
      if ($("ord-auto-loop")) $("ord-auto-loop").checked = !!s.autoLoop;
      if ($("ord-use-ai")) $("ord-use-ai").checked = !!s.useAi;
    } catch {
      /* ignore */
    }
  }

  function saveOrdSettings() {
    try {
      localStorage.setItem(
        ORD_SETTINGS_KEY,
        JSON.stringify({
          autoLoop: !!$("ord-auto-loop")?.checked,
          useAi: !!$("ord-use-ai")?.checked,
        })
      );
    } catch {
      /* ignore */
    }
  }

  function bindOrdPaste() {
    const ta = $("input-ord-draft");
    if (!ta) return;
    ta.addEventListener("paste", () => {
      setTimeout(() => {
        if (!$("ord-auto-loop")?.checked) return;
        const draft = (ta.value || "").trim();
        if (draft.length < 80) return;
        clearTimeout(ordDebounce);
        ordDebounce = setTimeout(() => runOrdLoop({ fromAuto: true }), 900);
      }, 120);
    });
  }

  function bindOrdCopyButtons() {
    document.querySelectorAll("[data-ord-copy]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const sid = btn.getAttribute("data-ord-copy");
        copyText($(`ord-out-${sid}`)?.textContent || "", `ord-${sid}`);
      });
    });
    $("btn-copy-ord-report")?.addEventListener("click", () => {
      const text = state.ordReport || $(`ord-out-report`)?.textContent || "";
      if (!text || text === "—") {
        toast("Run ORD loop first");
        return;
      }
      copyText(text, "ORD report");
    });
  }

  function switchTab(tabId) {
    const isOrd = tabId === "ord";
    $("tab-founder")?.classList.toggle("cu-tab-active", !isOrd);
    $("tab-ord")?.classList.toggle("cu-tab-active", isOrd);
    $("tab-founder")?.setAttribute("aria-selected", String(!isOrd));
    $("tab-ord")?.setAttribute("aria-selected", String(isOrd));
    const founderPanel = $("panel-founder-loop");
    const ordPanel = $("panel-ord-loop");
    if (founderPanel) {
      founderPanel.classList.toggle("cu-tab-panel-active", !isOrd);
      if (isOrd) founderPanel.setAttribute("hidden", "");
      else founderPanel.removeAttribute("hidden");
    }
    if (ordPanel) {
      ordPanel.classList.toggle("cu-tab-panel-active", isOrd);
      if (isOrd) ordPanel.removeAttribute("hidden");
      else ordPanel.setAttribute("hidden", "");
    }
    try {
      localStorage.setItem("chat-unify-active-tab-v1", tabId);
      if (isOrd) history.replaceState(null, "", "#ord");
      else history.replaceState(null, "", location.pathname + location.search);
    } catch {
      /* ignore */
    }
  }

  function bindTabs() {
    document.querySelectorAll(".cu-tab[data-tab]").forEach((btn) => {
      btn.addEventListener("click", () => switchTab(btn.getAttribute("data-tab") || "founder"));
    });
    try {
      const hash = (location.hash || "").replace("#", "");
      const saved = localStorage.getItem("chat-unify-active-tab-v1");
      if (hash === "ord" || saved === "ord") switchTab("ord");
    } catch {
      /* ignore */
    }
  }

  async function refreshAiStatus() {
    try {
      const res = await fetch(`${API}/health`, { cache: "no-store" });
      const h = await res.json();
      state.openrouterReady = !!h.openrouter_ready;
      state.aiProvider = h.ai_provider || "none";
      const orLabel = $("ord-openrouter-label");
      const fuLabel = $("founder-openrouter-label");
      const line = state.openrouterReady
        ? `OpenRouter · ${state.aiProvider}`
        : "OpenRouter · key missing (~/.sina/secrets.env)";
      if (orLabel) orLabel.textContent = line;
      if (fuLabel) fuLabel.textContent = line;
      if (state.openrouterReady && $("ord-use-ai") && !$("ord-use-ai").dataset.userTouched) {
        $("ord-use-ai").checked = true;
      }
    } catch {
      /* ignore */
    }
  }

  function bindAiCheckboxes() {
    $("ord-use-ai")?.addEventListener("change", () => {
      if ($("ord-use-ai")) $("ord-use-ai").dataset.userTouched = "1";
      saveOrdSettings();
    });
  }

  async function verifyUiFreshness() {
    const metaVer =
      document.querySelector('meta[name="chat-unify-ui-version"]')?.getAttribute("content") || CLIENT_UI_VERSION;
    const hasOrdTab = !!$("tab-ord");
    let serverVer = "";
    try {
      const res = await fetch(`${API}/health`, { cache: "no-store" });
      const h = await res.json();
      serverVer = h.ui_version || h.version || "";
    } catch {
      /* offline handled elsewhere */
    }
    const mismatch =
      !hasOrdTab ||
      (serverVer && serverVer !== metaVer) ||
      (serverVer && serverVer !== CLIENT_UI_VERSION);
    if (!mismatch) return;

    let banner = $("cu-stale-banner");
    if (!banner) {
      banner = document.createElement("div");
      banner.id = "cu-stale-banner";
      banner.className = "cu-stale-banner";
      banner.innerHTML =
        'Stale Chat Unify UI — tabs or ORD loop missing. <button type="button" id="cu-stale-reload">Reload now</button>';
      $("status-line")?.after(banner);
      $("cu-stale-reload")?.addEventListener("click", () => {
        location.href = `${API}/?ui=${CLIENT_UI_VERSION}&t=${Date.now()}`;
      });
    }
    if (!sessionStorage.getItem("cu-auto-reload")) {
      sessionStorage.setItem("cu-auto-reload", "1");
      setTimeout(() => {
        location.href = `${API}/?ui=${CLIENT_UI_VERSION}&t=${Date.now()}`;
      }, 1200);
    }
  }

  function loadFounderSettings() {
    try {
      const s = JSON.parse(localStorage.getItem(FOUNDER_SETTINGS_KEY) || "{}");
      if ($("founder-auto-loop")) $("founder-auto-loop").checked = s.autoLoop !== false && (s.autoLoop || s.autoTranslate);
      if ($("founder-auto-send")) $("founder-auto-send").checked = !!s.autoSend;
      if ($("founder-use-ai")) $("founder-use-ai").checked = !!s.useAi;
    } catch {
      /* ignore */
    }
  }

  function saveFounderSettings() {
    try {
      localStorage.setItem(
        FOUNDER_SETTINGS_KEY,
        JSON.stringify({
          autoLoop: !!$("founder-auto-loop")?.checked,
          autoSend: !!$("founder-auto-send")?.checked,
          useAi: !!$("founder-use-ai")?.checked,
        })
      );
    } catch {
      /* ignore */
    }
  }

  function bindFounderPaste() {
    const ta = $("input-founder-draft");
    if (!ta) return;
    ta.addEventListener("paste", () => {
      setTimeout(() => {
        if (!$("founder-auto-loop")?.checked) return;
        const draft = (ta.value || "").trim();
        if (draft.length < 60) return;
        clearTimeout(founderDebounce);
        founderDebounce = setTimeout(() => runFullLoop({ fromAuto: true }), 900);
      }, 120);
    });
  }

  function bindFounderSettings() {
    $("founder-auto-loop")?.addEventListener("change", saveFounderSettings);
    $("founder-auto-send")?.addEventListener("change", saveFounderSettings);
    $("founder-use-ai")?.addEventListener("change", saveFounderSettings);
  }

  function bindLoopCopyButtons() {
    document.querySelectorAll("[data-copy]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const sid = btn.getAttribute("data-copy");
        copyText($(`loop-out-${sid}`)?.textContent || "", sid);
      });
    });
    $("btn-copy-work-order")?.addEventListener("click", () => {
      if (!state.workOrder) {
        toast("Run loop first — no work order");
        return;
      }
      copyText(JSON.stringify(state.workOrder, null, 2), "work-order");
    });
  }

  /* legacy stubs — loop replaces separate translate/reason */
  async function translateFounder(opts = {}) {
    return runFullLoop(opts);
  }
  async function reasonFounder(opts = {}) {
    return runFullLoop(opts);
  }
  async function runBothMachines() {
    return runFullLoop();
  }
  async function sendFounderToCursor(opts = {}) {
    return sendLoopToCursor(opts);
  }

  async function aiPolish() {
    const brief = state.last_unified?.unified_brief || "";
    if (!brief.trim()) {
      toast("Merge chats first — no brief to polish");
      return;
    }
    toast("Calling Gemini via API…");
    const json = await api({ action: "ai_polish" });
    if (json.ok && json.response) {
      state.last_unified = { ...(state.last_unified || {}), unified_brief: json.response, ai_polished: true };
      renderBrief(state.last_unified);
      const path = json.export_path ? ` → ${json.export_path.split("/").pop()}` : "";
      toast(`AI polish done${path}`);
    } else if (json.blocked) {
      toast(json.message || "Blocked by model dispatch gate", 6000);
    } else {
      toast(json.error || json.response || "AI polish failed", 6000);
    }
  }

  async function aiCritique() {
    const brief = state.last_unified?.unified_brief || "";
    if (!brief.trim()) {
      toast("Merge chats first — no brief to critique");
      return;
    }
    toast("Running governance critique…");
    const json = await api({ action: "ai_critique" });
    if (json.ok && json.response) {
      const pre = $("unified-brief");
      if (pre) {
        pre.textContent = `--- AI CRITIQUE ---\n\n${json.response}\n\n--- ORIGINAL BRIEF ---\n\n${brief}`;
      }
      toast("Critique appended above brief");
    } else if (json.blocked) {
      toast(json.message || "Blocked by model dispatch gate", 6000);
    } else {
      toast(json.error || json.response || "Critique failed", 6000);
    }
  }

  function bind() {
    bindDropzone();
    bindTabs();
    loadFounderSettings();
    loadOrdSettings();
    bindFounderPaste();
    bindOrdPaste();
    bindFounderSettings();
    $("ord-auto-loop")?.addEventListener("change", saveOrdSettings);
    $("ord-use-ai")?.addEventListener("change", saveOrdSettings);
    $("btn-save")?.addEventListener("click", saveExtract);
    $("btn-structure-all")?.addEventListener("click", structureAll);
    $("btn-unify-all")?.addEventListener("click", () => unifyAll(false));
    $("btn-export-brief")?.addEventListener("click", exportBrief);
    $("btn-wire-n8n")?.addEventListener("click", wireN8n);
    $("btn-sync-cursor")?.addEventListener("click", syncCursor);
    bindLoopCopyButtons();
    bindOrdCopyButtons();
    bindAiCheckboxes();
    refreshAiStatus();
    $("btn-run-full-loop")?.addEventListener("click", () => runFullLoop());
    $("btn-run-ord-loop")?.addEventListener("click", () => runOrdLoop());
    $("btn-send-loop-cursor")?.addEventListener("click", () => sendLoopToCursor());
    $("btn-clear-founder")?.addEventListener("click", clearFounderLanguage);
    $("btn-clear-ord")?.addEventListener("click", clearOrd);
    $("btn-ai-polish")?.addEventListener("click", aiPolish);
    $("btn-ai-critique")?.addEventListener("click", aiCritique);
    $("btn-ai-polish-brief")?.addEventListener("click", aiPolish);
    $("btn-refresh")?.addEventListener("click", load);
    $("btn-import-transcript")?.addEventListener("click", importTranscript);
    $("btn-send-extract-cursor")?.addEventListener("click", () => sendCursor("send_extract_prompt"));
    $("btn-send-unify-cursor")?.addEventListener("click", () => sendCursor("send_unify_prompt"));
    $("btn-copy-extract-prompt")?.addEventListener("click", () => copyText(state.prompts.extract, "extract prompt"));
    $("btn-copy-unify-prompt")?.addEventListener("click", () => copyText(state.prompts.unify, "unify prompt"));
    $("btn-copy-brief")?.addEventListener("click", () => copyText(state.last_unified?.unified_brief || "", "unified brief"));
    $("btn-copy-output")?.addEventListener("click", () =>
      copyText(state.openExtract ? formatExtractOutput(state.openExtract) : "", "output")
    );
    $("btn-fix-extract")?.addEventListener("click", () => {
      if (!state.openExtract) {
        toast("Open a library item first");
        return;
      }
      fixExtract(state.openExtract.id);
    });
    $("btn-edit-output")?.addEventListener("click", () => {
      if (!state.openExtract) {
        toast("Open a library item first");
        return;
      }
      if ($("input-paste")) $("input-paste").value = state.openExtract.text || "";
      if ($("input-label")) $("input-label").value = state.openExtract.label || "";
      if ($("input-tags") && state.openExtract.tags) {
        $("input-tags").value = state.openExtract.tags.join(", ");
      }
      toast("Loaded into paste box — edit and Save again");
      $("panel-save")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    document.addEventListener("keydown", (ev) => {
      if ((ev.metaKey || ev.ctrlKey) && ev.key === "s") {
        ev.preventDefault();
        saveExtract();
      }
      if ((ev.metaKey || ev.ctrlKey) && ev.key === "r") {
        ev.preventDefault();
        load();
      }
    });
  }

  bind();
  load();
  verifyUiFreshness();
  setInterval(() => {
    if (!document.hidden) load();
  }, 45000);
})();
