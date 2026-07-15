const API = window.location.origin;
const POLL_MS = 30000;

function esc(s) {
  const d = document.createElement("div");
  d.textContent = String(s ?? "");
  return d.innerHTML;
}

function formatWhen(iso) {
  if (!iso) return "never";
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return String(iso).slice(0, 16);
  }
}

function renderGoals(goals) {
  const el = document.getElementById("goals-list");
  if (!goals.length) {
    el.innerHTML = '<p class="ahg-meta">No goals yet — add one below.</p>';
    return;
  }
  el.innerHTML = goals
    .map(
      (g) => `<article class="ahg-goal-card">
        <strong>${esc(g.title)}</strong>
        <div class="ahg-goal-meta">${esc(g.target || "")}${g.linked_plan_id ? ` · Plan: ${esc(g.linked_plan_id)}` : ""}</div>
      </article>`
    )
    .join("");
}

function renderPlans(plans) {
  const el = document.getElementById("plans-list");
  if (!plans || !plans.length) {
    el.innerHTML = '<li class="ahg-meta">No linked plans logged — open Worker Hub roadmaps or add SourceA.</li>';
    return;
  }
  el.innerHTML = plans
    .map(
      (p) =>
        `<li><strong>${esc(p.title)}</strong> — ${esc(p.progress_label || "")} · ${esc(p.next_action || "")}</li>`
    )
    .join("");
}

function renderSleep(data) {
  const sig = data.sleep_signal || {};
  const bridge = data.sleep_bridge || {};
  const state = String(sig.state || "unknown").toLowerCase();
  const pill = document.getElementById("sleep-pill");
  const meta = document.getElementById("sleep-meta");
  const bridgeLine = document.getElementById("bridge-line");
  const autoBtn = document.getElementById("btn-auto-arm");
  const lead = document.getElementById("sleep-lead");

  if (pill) {
    pill.textContent = state.toUpperCase();
    pill.className =
      "ahg-pill " + (state === "asleep" || state === "sleeping" ? "asleep" : state === "awake" ? "awake" : "unknown");
  }
  if (meta) {
    const parts = [`Updated ${formatWhen(sig.updated_at)}`];
    if (sig.sleep_hours != null) parts.push(`${sig.sleep_hours}h sleep`);
    if (sig.steps_today != null) parts.push(`${sig.steps_today} steps`);
    meta.textContent = parts.join(" · ");
  }
  if (bridgeLine) {
    const rec = bridge.recommend || "stay";
    const fm = bridge.founder_mode || "—";
    const sleepOn = bridge.sleep_escalation ? "ON" : "off";
    bridgeLine.textContent = `Bridge: ${rec} · founder ${fm} · overnight ${sleepOn}`;
  }
  if (autoBtn) {
    autoBtn.textContent = data.auto_arm_sleep ? "Auto arm: ON" : "Auto arm: OFF";
  }
  if (lead) {
    lead.textContent = data.auto_arm_sleep
      ? "Auto arm ON — sleep signal will arm overnight when Health says asleep."
      : "Tap Auto arm ON to wire sleep → overnight engines automatically.";
  }
}

function renderStatus(data) {
  const el = document.getElementById("status-line");
  if (!el) return;
  const goals = (data.goals || []).length;
  const plans = (data.parallel_plans || []).length;
  const mode = data.standalone ? "Standalone" : "Hub";
  el.textContent = `${mode} · ${goals} goals · ${plans} plans · ~/.sina/apple-health/`;

  const sig = data.sleep_signal || {};
  const bridge = data.sleep_bridge || {};
  const state = String(sig.state || "unknown").toUpperCase();
  const set = (id, text) => {
    const node = document.getElementById(id);
    if (node) node.textContent = text;
  };
  set("stat-sleep-val", state.slice(0, 8));
  set("stat-goals-val", String(goals));
  set("stat-plans-val", String(plans));
  set("stat-bridge-val", bridge.sleep_escalation ? "ON" : "off");
}

async function postAction(action, extra = {}) {
  const res = await fetch(`${API}/api/apple-health`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, ...extra }),
  });
  return res.json();
}

async function load() {
  const res = await fetch(`${API}/api/apple-health`, { cache: "no-store" });
  const data = await res.json();
  if (!data.ok) throw new Error(data.error || "load failed");
  data.standalone = true;
  renderGoals(data.goals || []);
  renderPlans(data.parallel_plans || []);
  renderSleep(data);
  renderStatus(data);
  return data;
}

document.getElementById("btn-refresh")?.addEventListener("click", () => load().catch(() => {}));
document.getElementById("btn-open-health")?.addEventListener("click", async () => {
  await postAction("open_health");
});
document.getElementById("btn-sleep-start")?.addEventListener("click", async () => {
  await postAction("sleep_start", { source: "founder_tap" });
  load();
});
document.getElementById("btn-sleep-end")?.addEventListener("click", async () => {
  await postAction("sleep_end", { source: "founder_tap" });
  load();
});
document.getElementById("btn-auto-arm")?.addEventListener("click", async () => {
  const res = await fetch(`${API}/api/apple-health`, { cache: "no-store" });
  const data = await res.json();
  await postAction(data.auto_arm_sleep ? "disable_auto_arm" : "enable_auto_arm");
  load();
});
document.getElementById("goal-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = document.getElementById("goal-title").value.trim();
  const target = document.getElementById("goal-target").value.trim();
  if (!title) return;
  await postAction("add_goal", { title, target });
  document.getElementById("goal-title").value = "";
  document.getElementById("goal-target").value = "";
  load();
});

load().catch(() => {
  const el = document.getElementById("status-line");
  if (el) el.textContent = "Could not load — double-click Apple Health again.";
});
setInterval(() => {
  if (!document.hidden) load().catch(() => {});
}, POLL_MS);
