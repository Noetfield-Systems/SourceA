(function () {
  "use strict";

  const API = window.location.origin;
  const $ = (id) => document.getElementById(id);
  let state = { prompts: { extract: "", unify: "" }, last_unified: null, openExtract: null, autoImportDone: false, autoStructureDone: false };

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

  async function api(body) {
    const res = await fetch(`${API}/api/chat-unify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || { action: "report" }),
    });
    return res.json();
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
      el.textContent = `Connected · v${json.version || "1.3"} · ${n} extract${n === 1 ? "" : "s"} · ${ready} ready${qual}${merged}${wire}${aiLine}`;
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
      const stat = $("stat-extracts");
      if (stat) stat.textContent = String(n);
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
    $("btn-save")?.addEventListener("click", saveExtract);
    $("btn-structure-all")?.addEventListener("click", structureAll);
    $("btn-unify-all")?.addEventListener("click", () => unifyAll(false));
    $("btn-export-brief")?.addEventListener("click", exportBrief);
    $("btn-wire-n8n")?.addEventListener("click", wireN8n);
    $("btn-sync-cursor")?.addEventListener("click", syncCursor);
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
  setInterval(() => {
    if (!document.hidden) load();
  }, 45000);
})();
