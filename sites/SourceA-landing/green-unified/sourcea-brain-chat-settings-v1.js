/**
 * Private founder control — Brain + Forge Terminal chat routing (sourcea.app).
 */
(function () {
  "use strict";

  const CONFIG_URL = "/sourcea/data/sourcea-brain-chat-config-v1.json";
  const MODELS_URL = "/sourcea/data/forge-terminal-models-public-v1.json";
  const KEY_STORAGE = "sourcea-brain-settings-key-v1";
  const OVERRIDE_KEY = "sourcea-brain-chat-config-override-v1";

  const $ = (id) => document.getElementById(id);
  let config = {};
  let models = [];
  let extraModels = [];

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = String(s || "");
    return d.innerHTML;
  }

  async function loadJson(url) {
    const r = await fetch(url, { cache: "no-store" });
    if (!r.ok) throw new Error(url + " " + r.status);
    return r.json();
  }

  function renderModels() {
    const el = $("sa-bcs-models");
    if (!el) return;
    const all = models.concat(extraModels);
    el.innerHTML = all
      .map(function (m) {
        const id = m.id || m.api_model || "";
        const label = m.label || id;
        return '<div class="sa-bcs-model-row"><code>' + esc(id) + "</code><span>" + esc(label) + "</span></div>";
      })
      .join("");
    const sel = $("sa-bcs-model");
    if (sel) {
      const cur = sel.value;
      sel.innerHTML = all
        .map(function (m) {
          const id = m.id || m.api_model || "";
          const label = (m.label || id) + (m.cost_band ? " · " + m.cost_band : "");
          return '<option value="' + esc(id) + '">' + esc(label) + "</option>";
        })
        .join("");
      if (cur && Array.from(sel.options).some(function (o) { return o.value === cur; })) {
        sel.value = cur;
      }
    }
  }

  function fillForm() {
    if ($("sa-bcs-provider")) $("sa-bcs-provider").value = config.provider || "";
    if ($("sa-bcs-api-url")) $("sa-bcs-api-url").value = config.api_worker_url || "";
    if ($("sa-bcs-max-len")) $("sa-bcs-max-len").value = config.max_message_len || 2000;
    if ($("sa-bcs-offline-hint")) $("sa-bcs-offline-hint").value = config.hint_offline || "";
    if ($("sa-bcs-model") && config.model) $("sa-bcs-model").value = config.model;
    const path = $("sa-bcs-disk-path");
    if (path) {
      path.textContent =
        "Ship changes: commit SourceA-landing/green-unified/data/sourcea-brain-chat-config-v1.json then deploy Pages.";
    }
  }

  async function checkWorker() {
    const st = $("sa-bcs-worker-status");
    const url = ($("sa-bcs-api-url") && $("sa-bcs-api-url").value) || config.api_worker_url;
    if (!url || !st) return;
    st.textContent = "Checking worker…";
    st.classList.remove("is-live");
    try {
      const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "status", product: "forge_terminal" }),
      });
      const row = await r.json();
      if (row.openrouter_ready || row.ok) {
        st.textContent = "Worker live · " + (row.models ? row.models.length : 0) + " models";
        st.classList.add("is-live");
      } else {
        st.textContent = "Worker reachable · models offline";
      }
    } catch (e) {
      st.textContent = "Worker unreachable — " + String(e.message || e).slice(0, 60);
    }
  }

  function buildExportConfig() {
    return {
      schema: "sourcea-brain-chat-config-v1",
      api_relative: config.api_relative || "/api/brain/chat/v1",
      api_worker_url: ($("sa-bcs-api-url") && $("sa-bcs-api-url").value) || config.api_worker_url,
      local_dev_api: config.local_dev_api || "http://127.0.0.1:13020/api/brain/chat/v1",
      provider: ($("sa-bcs-provider") && $("sa-bcs-provider").value) || config.provider,
      model: ($("sa-bcs-model") && $("sa-bcs-model").value) || config.model,
      max_message_len: Number(($("sa-bcs-max-len") && $("sa-bcs-max-len").value) || 2000),
      public_domain: config.public_domain || "https://sourcea.app",
      fallback_chips: config.fallback_chips !== false,
      hint_offline: ($("sa-bcs-offline-hint") && $("sa-bcs-offline-hint").value) || config.hint_offline,
      settings_panel: "/sourcea/brain-chat-settings",
      extra_models: extraModels,
    };
  }

  async function bootPanel() {
    try {
      config = await loadJson(CONFIG_URL);
      try {
        const ov = JSON.parse(localStorage.getItem(OVERRIDE_KEY) || "{}");
        if (ov.extra_models) extraModels = ov.extra_models;
      } catch (_) { /* quiet */ }
      const pub = await loadJson(MODELS_URL);
      models = pub.models || [];
      renderModels();
      fillForm();
      await checkWorker();
      $("sa-bcs-panel").hidden = false;
      $("sa-bcs-unlock").hidden = true;
    } catch (e) {
      alert("Load failed: " + e.message);
    }
  }

  function unlock() {
    const key = ($("sa-bcs-pass") && $("sa-bcs-pass").value) || "";
    if (!key.trim()) {
      alert("Enter founder key or edit config on disk.");
      return;
    }
    sessionStorage.setItem(KEY_STORAGE, key.trim());
    bootPanel();
  }

  function copyJson() {
    const row = buildExportConfig();
    localStorage.setItem(OVERRIDE_KEY, JSON.stringify(row));
    const text = JSON.stringify(row, null, 2);
    navigator.clipboard.writeText(text).then(
      function () {
        alert("Config JSON copied — paste into sourcea-brain-chat-config-v1.json and deploy.");
      },
      function () {
        prompt("Copy this JSON:", text);
      },
    );
  }

  function addModel() {
    const id = ($("sa-bcs-custom-id") && $("sa-bcs-custom-id").value.trim()) || "";
    const label = ($("sa-bcs-custom-label") && $("sa-bcs-custom-label").value.trim()) || id;
    if (!id) return;
    extraModels.push({ id: id, api_model: id, label: label, group: "Custom" });
    renderModels();
    if ($("sa-bcs-custom-id")) $("sa-bcs-custom-id").value = "";
    if ($("sa-bcs-custom-label")) $("sa-bcs-custom-label").value = "";
  }

  function bind() {
    $("sa-bcs-unlock-btn") && $("sa-bcs-unlock-btn").addEventListener("click", unlock);
    $("sa-bcs-refresh") && $("sa-bcs-refresh").addEventListener("click", checkWorker);
    $("sa-bcs-copy-json") && $("sa-bcs-copy-json").addEventListener("click", copyJson);
    $("sa-bcs-add-model") && $("sa-bcs-add-model").addEventListener("click", addModel);
    if (sessionStorage.getItem(KEY_STORAGE)) bootPanel();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();
