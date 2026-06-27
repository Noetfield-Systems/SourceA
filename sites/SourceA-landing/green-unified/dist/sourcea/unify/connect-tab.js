(function () {
  "use strict";

  const API = window.location.origin;

  function $(id) {
    return document.getElementById(id);
  }

  function toast(msg) {
    if (typeof window.cuToast === "function") window.cuToast(msg);
    else alert(msg);
  }

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      toast("Copied to clipboard");
    } catch {
      toast("Copy failed — select manually");
    }
  }

  function statusClass(status) {
    const s = String(status || "offline").toLowerCase();
    if (s === "live") return "live";
    if (s === "ready") return "ready";
    if (s === "setup") return "setup";
    return "offline";
  }

  function renderMesh(mesh) {
    const el = $("connect-mesh-strip");
    if (!el || !mesh) return;
    const rows = [
      ["Chat Unify", mesh.chat_unify],
      ["Hub", mesh.hub],
      ["n8n", mesh.n8n],
      ["Cloud Workers", mesh.cloud_workers],
    ];
    el.innerHTML = rows
      .map(function (pair) {
        const ok = pair[1] && pair[1].ok;
        return (
          '<span class="cu-mesh-pill ' +
          (ok ? "is-live" : "is-off") +
          '">' +
          pair[0] +
          " · " +
          (ok ? "LIVE" : "OFF") +
          "</span>"
        );
      })
      .join("");
  }

  function laneActions(lane) {
    const id = lane.id || "";
    const btns = [];
    if (id === "cursor_local") {
      btns.push('<button type="button" class="cu-btn cu-btn-primary cu-btn-sm" data-act="send_cursor">Send mission → Cursor</button>');
      btns.push('<button type="button" class="cu-btn cu-btn-ghost cu-btn-sm" data-act="goto_forge">Open Forge</button>');
    }
    if (id === "cursor_cloud") {
      btns.push('<button type="button" class="cu-btn cu-btn-ghost cu-btn-sm" data-act="copy_manifest">Copy plugin manifest</button>');
    }
    if (id === "n8n") {
      btns.push('<a class="cu-btn cu-btn-ghost cu-btn-sm" href="http://127.0.0.1:13026/" target="_blank" rel="noopener">Open n8n</a>');
    }
    if (id === "cloud_workers") {
      btns.push('<button type="button" class="cu-btn cu-btn-ghost cu-btn-sm" data-act="dispatch_cloud">Ping cloud</button>');
      btns.push('<a class="cu-btn cu-btn-ghost cu-btn-sm" href="http://127.0.0.1:13027/" target="_blank" rel="noopener">Open panel</a>');
    }
    if (id === "webhook_inbound") {
      btns.push('<button type="button" class="cu-btn cu-btn-primary cu-btn-sm" data-act="copy_hook">Copy webhook URL</button>');
    }
    if (id === "mcp_ready") {
      btns.push('<button type="button" class="cu-btn cu-btn-ghost cu-btn-sm" data-act="download_manifest">Download manifest</button>');
    }
    btns.push('<button type="button" class="cu-btn cu-btn-ghost cu-btn-sm" data-act="test" data-lane="' + id + '">Test</button>');
    return btns.join("");
  }

  function renderLanes(payload) {
    const grid = $("connect-lanes");
    if (!grid) return;
    const lanes = payload.lanes || [];
    grid.innerHTML = lanes
      .map(function (lane) {
        return (
          '<article class="cu-connect-card" data-lane-id="' +
          lane.id +
          '">' +
          '<div class="cu-connect-card-head">' +
          "<div><span class=\"cu-connect-cat\">" +
          (lane.category || "integration") +
          '</span><h3>' +
          (lane.label || lane.id) +
          "</h3></div>" +
          '<span class="cu-status-pill ' +
          statusClass(lane.status) +
          '">' +
          (lane.status || "offline") +
          "</span>" +
          "</div>" +
          '<p class="cu-connect-desc">' +
          (lane.description || "") +
          "</p>" +
          '<div class="cu-connect-actions">' +
          laneActions(lane) +
          "</div></article>"
        );
      })
      .join("");

    grid.querySelectorAll("[data-act]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        handleLaneAction(btn.getAttribute("data-act"), btn.getAttribute("data-lane"), payload);
      });
    });
  }

  function renderTriggers(triggers) {
    const list = $("connect-trigger-list");
    if (!list) return;
    const rows = triggers || [];
    if (!rows.length) {
      list.innerHTML = "<li>No triggers yet — POST to webhook or register below.</li>";
      return;
    }
    list.innerHTML = rows
      .slice(-12)
      .reverse()
      .map(function (t) {
        return "<li><strong>" + (t.name || t.event) + "</strong> · " + (t.created_at || "") + "</li>";
      })
      .join("");
  }

  function renderHookUrl(base) {
    const input = $("connect-hook-url");
    if (input) input.value = base + "/api/integrations/v1/hook";
  }

  async function postIntegrations(body) {
    const res = await fetch(API + "/api/integrations/v1", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return res.json();
  }

  async function handleLaneAction(act, laneId, payload) {
    if (act === "copy_hook") {
      copyText(($("connect-hook-url") || {}).value || API + "/api/integrations/v1/hook");
      return;
    }
    if (act === "goto_forge" && window.switchTab) {
      window.switchTab("forge");
      return;
    }
    if (act === "copy_manifest" || act === "download_manifest") {
      const res = await fetch(API + "/api/integrations/v1/manifest");
      const json = await res.json();
      const blob = new Blob([JSON.stringify(json.manifest || json, null, 2)], { type: "application/json" });
      if (act === "download_manifest") {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "chat-unify-cursor-plugin-v1.json";
        a.click();
        toast("Manifest downloaded");
      } else {
        copyText(JSON.stringify(json.manifest || json, null, 2));
      }
      return;
    }
    if (act === "send_cursor") {
      const mission = (window.cuGetForgeMission && window.cuGetForgeMission()) || "";
      const text = mission || prompt("Paste mission text to send to Cursor:", "") || "";
      if (!text.trim()) {
        toast("Nothing to send — forge a mission first");
        return;
      }
      const res = await fetch(API + "/api/chat-unify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "send_founder_to_cursor", text: text.trim() }),
      });
      const json = await res.json();
      toast(json.message || (json.ok ? "Sent to Cursor" : json.error || "Send failed"));
      return;
    }
    if (act === "dispatch_cloud") {
      const json = await postIntegrations({ action: "dispatch_cloud", dispatch: { kind: "ping", source: "connect_tab" } });
      toast(json.ok ? "Cloud dispatch OK" : json.message || json.error || "Dispatch failed");
      return;
    }
    if (act === "test") {
      const json = await postIntegrations({ action: "test_connection", lane: laneId });
      toast(json.ok ? laneId + " · OK" : laneId + " · check setup");
      if (json.lane) {
        const card = document.querySelector('[data-lane-id="' + laneId + '"] .cu-status-pill');
        if (card) {
          card.className = "cu-status-pill " + statusClass(json.lane.status);
          card.textContent = json.lane.status || "offline";
        }
      }
    }
  }

  async function loadConnect() {
    const status = $("connect-status-line");
    if (status) status.textContent = "Refreshing integrations…";
    try {
      const res = await fetch(API + "/api/integrations/v1");
      const json = await res.json();
      if (!json.ok) {
        if (status) status.textContent = "Connect hub offline — restart Chat Unify.";
        return;
      }
      renderMesh(json.mesh);
      renderLanes(json);
      renderTriggers(json.triggers);
      renderHookUrl(json.base_url || API);
      if (status) {
        const live = (json.lanes || []).filter(function (l) {
          return l.status === "live";
        }).length;
        status.textContent =
          "Connect live · " +
          live +
          "/" +
          (json.lanes || []).length +
          " lanes · UI " +
          (json.ui_version || "—") +
          " · forge@sourcea.app";
      }
    } catch (e) {
      if (status) status.textContent = "Could not reach integrations API.";
    }
  }

  function bindConnectPanel() {
    $("btn-connect-refresh")?.addEventListener("click", loadConnect);
    $("btn-connect-copy-hook")?.addEventListener("click", function () {
      copyText(($("connect-hook-url") || {}).value || "");
    });
    $("btn-connect-register")?.addEventListener("click", async function () {
      const name = ($("connect-trigger-name") || {}).value || "manual";
      const event = ($("connect-trigger-event") || {}).value || "custom";
      const json = await postIntegrations({ action: "register_trigger", name: name, event: event });
      toast(json.ok ? "Trigger registered" : "Register failed");
      loadConnect();
    });
    $("btn-connect-test-hook")?.addEventListener("click", async function () {
      const text = ($("connect-hook-test-text") || {}).value || "Test hook from Connect tab";
      const res = await fetch(API + "/api/integrations/v1/hook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event: "forge.mission", text: text, source: "connect_ui" }),
      });
      const json = await res.json();
      toast(json.ok ? "Hook routed to Prompt Forge" : json.error || "Hook failed");
      loadConnect();
    });
  }

  window.sinaLoadConnect = loadConnect;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindConnectPanel);
  } else {
    bindConnectPanel();
  }
})();
