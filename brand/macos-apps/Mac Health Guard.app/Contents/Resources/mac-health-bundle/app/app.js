(function () {
  "use strict";

  const API = `${window.location.protocol}//${window.location.host}`;
  const $ = (id) => document.getElementById(id);
  let lastReport = null;
  let lastAction = "report";
  let activeTab = "rhythm";
  let lastRamSnapshot = null;
  let liveTimer = null;
  let livePollBooted = false;
  let lastLiveTickMs = 0;
  let liveFetchInFlight = false;
  let userPickedTab = false;

  const SEV_CLASS = {
    critical: "critical",
    high: "high",
    medium: "medium",
    low: "info",
    info: "info",
    pass: "pass",
  };

  const SEV_WORDS = {
    critical: "Urgent",
    high: "Important",
    medium: "Note",
    low: "Minor",
    info: "Info",
    pass: "Clear",
  };

  const DOMAIN_ORDER = [
    "os",
    "sip",
    "gatekeeper",
    "firewall",
    "filevault",
    "updates",
    "xprotect",
    "listeners",
    "launch_items",
    "remote_access",
    "disk",
  ];

  const DOMAIN_STORY = {
    os: "Which macOS your body runs on",
    sip: "The seal that keeps the system root untouchable",
    gatekeeper: "Which apps are allowed through the door",
    firewall: "The perimeter valve — who may knock from outside",
    filevault: "Whether your files sleep encrypted",
    updates: "Whether security patches are waiting",
    listeners: "Which network doors are open",
    launch_items: "What wakes when you log in",
    remote_access: "Whether remote login is exposed",
    disk: "How full the body's storage is",
    xprotect: "Apple's built-in malware watch",
  };

  const AGENT_STATUS = {
    pass: "All clear",
    info: "All clear",
    low: "Minor note",
    medium: "Worth a look",
    high: "Needs you",
    critical: "Urgent",
  };

  const GRADE_WORDS = {
    excellent: "The heart sings",
    good: "A strong beat",
    fair: "Worth a calm tune-up",
    "at-risk": "Needs attention",
  };

  const RING_MOOD = {
    excellent: "Heart sings",
    good: "Strong beat",
    fair: "Tune-up",
    "at-risk": "Needs care",
  };

  function paintScoreRing(score, gradeLabel, securityScore, opts) {
    opts = opts || {};
    const ringKey = scoreRingClass(score);
    const moodEl = $("score-mood");
    const gradeEl = $("score-grade");
    const ring = $("score-ring");
    const sec = securityScore != null ? securityScore : score;
    const modes = opts.preventionModes || [];
    const cursorHot = opts.cursorEmergency || modes.includes("cursor_hot");
    let displayRing = ringKey;
    let mood = RING_MOOD[ringKey] || "";
    if (cursorHot) {
      displayRing = "at-risk";
      mood = "Cursor hot";
    }
    $("score-value").textContent = String(score);
    if (moodEl) moodEl.textContent = mood;
    if (gradeEl) {
      if (sec !== score || cursorHot) {
        const extra = cursorHot ? " · IDE emergency" : gradeLabel ? ` · ${gradeLabel}` : "";
        gradeEl.textContent = `Body ${score} · Security ${sec}${extra}`;
      } else {
        gradeEl.textContent = gradeLabel || "";
      }
    }
    if (ring) {
      ring.className = "mhg-score-ring " + displayRing + (cursorHot ? " mhg-score-cursor-hot" : "");
      ring.setAttribute(
        "aria-label",
        cursorHot
          ? `Body ${score}, security ${sec}, Cursor emergency — not strong beat`
          : `Body score ${score}, security ${sec}, ${gradeLabel || ""}`
      );
    }
  }

  const RHYTHM_POLL_MS = 12000;
  const RAM_POLL_MS = 6000;
  const FULL_POLL_MS = 90000;
  const LIVE_MIN_GAP_MS = 4000;

  const hasNative = () =>
    !!(window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.mhgNative);

  function nativeAction(action) {
    if (!hasNative()) return false;
    window.webkit.messageHandlers.mhgNative.postMessage(action);
    return true;
  }

  window.__mhgNativeDone = function (msg) {
    const flash = document.getElementById("panic-flash");
    const msgEl = $("heal-msg");
    const resultEl = $("cooldown-result");
    const line = String(msg || "").replace(/\\n/g, "\n");
    const isZeroKill = /Agents killed: 0|Would kill: 0|0 agents/i.test(line);
    const flashCls = isZeroKill ? "warn" : "done";
    if (flash) {
      flash.textContent = line;
      flash.className = "mhg-panic-flash " + flashCls;
      flash.hidden = false;
      setTimeout(() => { flash.hidden = true; }, 8000);
    }
    if (msgEl) {
      msgEl.hidden = false;
      msgEl.textContent = line;
      msgEl.className = isZeroKill ? "mhg-heal-msg warn" : "mhg-heal-msg";
    }
    if (resultEl) {
      resultEl.hidden = false;
      resultEl.textContent = line;
      resultEl.className = isZeroKill ? "mhg-cooldown-result warn" : "mhg-cooldown-result";
    }
  };

  function runTapAction(action) {
    if (!action) return;
    if (action === "firewall") {
      window.open("x-apple.systempreferences:com.apple.Network-Settings.extension?Firewall", "_self");
      return;
    }
    if (action.startsWith("cpu_") || action === "cool_down" || action === "wake_cool_down") {
      setActiveTab("cooldown");
      if (action === "cpu_restart_cursor" && nativeAction("restart_cursor")) {
        const msgEl = $("heal-msg");
        if (msgEl) {
          msgEl.hidden = false;
          msgEl.textContent = "Restarting Cursor — save files, window closes in 1 second…";
        }
        return;
      }
      if (nativeAction(action)) return;
      return runCpuRelief(action);
    }
    if (action === "emergency_stop") {
      if (nativeAction("emergency_stop")) return;
      return runPanicStop();
    }
    if (action === "scan") return load("scan");
    return load(action);
  }

  function cursorHotThresholds() {
    const s = (lastReport && lastReport.settings && lastReport.settings.cursor) || {};
    return {
      peak: Number(s.ui_hot_banner_peak_pct) || 280,
      sum: Number(s.ui_hot_banner_sum_pct) || 350,
    };
  }

  function paintCursorHotBanner(liveOrReport) {
    const banner = $("cursor-hot-banner");
    const line = $("cursor-hot-line");
    const btnPanic = $("btn-panic-header");
    const btnRestart = $("btn-restart-cursor");
    if (!banner || !line) return;
    const prev = (liveOrReport && liveOrReport.prevention) || {};
    const modes = prev.modes || [];
    const mp = (liveOrReport && liveOrReport.machine_pressure) || {};
    const cur = mp.cursor || prev.cursor || {};
    const peak = cur.renderer_peak || cur.peak_cpu || 0;
    const cpuSum = cur.cpu_sum || 0;
    // Trust backend cursor_hot / cursor_emergency — not raw instant peak alone.
    const emergency =
      Boolean(liveOrReport && liveOrReport.cursor_emergency) ||
      modes.includes("cursor_hot");
    banner.hidden = true;
    if (btnRestart) btnRestart.hidden = true;
    if (btnPanic) btnPanic.textContent = "Stop background agents";
    if (!emergency) return;
    banner.hidden = false;
    if (btnRestart) btnRestart.hidden = false;
    line.textContent = `Cursor very hot (${peak.toFixed(0)}% peak · ${cpuSum.toFixed(0)}% sum) — optional Restart in Cool Down if frozen. Auto-stop never closes Cursor.`;
    if (btnRestart) {
      btnRestart.textContent = "Emergency: Restart Cursor";
      btnRestart.onclick = () => {
        if (!window.confirm("Only if Mac is frozen — save files first. Restart Cursor?")) return;
        if (nativeAction("restart_cursor")) return;
        runCpuRelief("cpu_restart_cursor");
      };
    }
  }

  function paintPlaywrightBanner(liveOrReport) {
    const banner = $("playwright-banner");
    const line = $("playwright-line");
    const btn = $("btn-kill-playwright");
    if (!banner || !line) return;
    const prev = (liveOrReport && liveOrReport.prevention) || {};
    const modes = prev.modes || [];
    const pw = prev.playwright || {};
    if (!modes.includes("playwright_stuck") || !pw.stuck) {
      banner.hidden = true;
      return;
    }
    banner.hidden = false;
    line.textContent =
      prev.founder_line ||
      `Stuck agent browser (${pw.cpu_sum || "?"}% CPU) — kills headless Chrome only, not Cursor.`;
    if (btn) {
      btn.onclick = () => {
        if (!window.confirm("Kill stuck headless Chrome from agent browser tools?")) return;
        runCpuRelief("cpu_kill_playwright");
      };
    }
  }

  function paintLogShield(live) {
    const mp = (live && live.machine_pressure) || {};
    const grid = $("log-shield-grid");
    const badge = $("hub-truth-badge");
    const bombBanner = $("log-bomb-banner");
    const bombLine = $("log-bomb-line");
    if (!grid) return;
    const bomb = mp.sina_log_bomb || {};
    const hubBadge = mp.hub_truth_badge || "Down";
    if (badge) {
      badge.textContent = "Hub · " + hubBadge;
      badge.className =
        "mhg-badge mhg-hub-truth-badge " +
        (hubBadge === "Healthy" ? "ok" : hubBadge === "Port-only" ? "warn" : "bad");
    }
    const rows = [];
    rows.push(["Hub log", bomb.human || "—"]);
    if (mp.log_growth_mb_per_min != null) {
      rows.push(["Log growth", mp.log_growth_mb_per_min + " MB/min"]);
    }
    rows.push(["Stuck readers", String(mp.stuck_log_reader_count || 0)]);
    const storm = (mp.factory_storm || {}).factory_storm;
    rows.push(["Factory storm", storm ? "Yes — hub sick" : "No"]);
    const logs = mp.largest_sina_logs || [];
    logs.slice(0, 4).forEach((row) => {
      rows.push([row.name || "log", row.human || "—"]);
    });
    grid.innerHTML = rows
      .map(
        ([label, val]) =>
          `<div class="mhg-log-shield-row"><span>${esc(label)}</span><strong>${esc(val)}</strong></div>`
      )
      .join("");
    if (bombBanner && bombLine) {
      if (bomb.critical || bomb.level === "warn") {
        bombBanner.hidden = false;
        bombLine.textContent = bomb.critical
          ? `Log bomb: hub log is ${bomb.human}. Relieve disk to free space and stop I/O pressure.`
          : `Large hub log (${bomb.human}). Relieve before it becomes a bomb.`;
      } else {
        bombBanner.hidden = true;
      }
    }
  }

  async function runLogShieldAction(action) {
    try {
      const res = await fetch(`${API}/api/mac-health`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, standalone: true }),
      });
      const data = await res.json();
      const msg = $("heal-msg");
      if (msg) {
        msg.hidden = false;
        msg.className = "mhg-heal-msg ok";
        msg.textContent =
          action === "truncate_runaway_logs"
            ? `Relieved disk — truncated ${data.count || 0} log(s).`
            : `Killed ${data.count || 0} stuck reader(s).`;
      }
      await tickLive();
      await load("report");
    } catch (e) {
      const msg = $("heal-msg");
      if (msg) {
        msg.hidden = false;
        msg.className = "mhg-heal-msg err";
        msg.textContent = e.message || "Log Shield action failed";
      }
    }
  }

  function paintPreventionBanner(live) {
    const banner = $("prevention-banner");
    const line = $("prevention-line");
    const tap = $("prevention-tap");
    if (!banner || !line) return;
    const prev = (live && live.prevention) || {};
    const health = prev.health || "healthy";
    const modes = prev.modes || [];
    if (!prev.founder_line) {
      banner.hidden = true;
      if (tap) tap.hidden = true;
      return;
    }
    // cursor_busy = normal — never nag.
    if (modes.includes("playwright_stuck")) {
      banner.hidden = false;
      line.textContent = prev.founder_line;
      banner.className = "mhg-prevention-banner watch";
      if (tap) tap.hidden = true;
      return;
    }
    if (modes.includes("cursor_busy") && !modes.includes("cursor_hot") && health !== "unhealthy") {
      banner.hidden = true;
      if (tap) tap.hidden = true;
      const nextTap = $("next-tap");
      if (nextTap) nextTap.hidden = true;
      return;
    }
    const cpu = (live && live.machine_pressure && live.machine_pressure.cpu_pct) || 0;
    const score = live && live.score;
    if (health === "healthy" || (health === "watch" && cpu < 50 && (score == null || score >= 80))) {
      banner.hidden = true;
      if (tap) tap.hidden = true;
      return;
    }
    banner.hidden = false;
    line.textContent = prev.founder_line;
    banner.className =
      "mhg-prevention-banner" +
      (health === "unhealthy" ? " hot" : health === "watch" ? " watch" : "");
    if (tap && prev.next_tap_action) {
      if (prev.next_tap_action === "cpu_restart_cursor") {
        tap.hidden = true;
      } else {
        tap.hidden = false;
        tap.textContent =
          prev.next_tap_action === "cpu_wake_cool_down" ? "Wake Cool Down" : "Cool Down";
        tap.onclick = () => runTapAction(prev.next_tap_action);
      }
    } else if (tap) {
      tap.hidden = true;
    }
    const nextTap = $("next-tap");
    if (nextTap) {
      if (prev.next_tap_action === "cpu_restart_cursor") {
        nextTap.hidden = true;
      } else if (prev.founder_line && !modes.includes("cursor_busy")) {
        nextTap.textContent = prev.founder_line;
        nextTap.hidden = false;
      } else {
        nextTap.hidden = true;
      }
    }
  }

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function liveBadgeClass(status) {
    const s = String(status || "").toUpperCase();
    if (s === "LIVE") return "mhg-badge-live";
    if (s === "STALE") return "mhg-badge-stale";
    return "mhg-badge-sick";
  }

  function paintCpuLadder(live) {
    const el = $("cpu-ladder");
    if (!el) return;
    const cws =
      (live && live.cpu_warn_state) ||
      (lastReport && lastReport.cpu_warn_state) ||
      null;
    if (!cws || !cws.founder_line) {
      el.hidden = true;
      return;
    }
    const st = cws.status || "calm";
    el.textContent = cws.founder_line;
    el.className = "mhg-cpu-ladder status-" + String(st).replace(/[^a-z0-9_-]/gi, "");
    el.hidden = false;
  }

  function rhythmPanelVisible() {
    return Boolean($("pressure-grid"));
  }

  function paintLiveNarrative(live) {
    const gradeEl = $("grade-story");
    if (!gradeEl || !live) return;
    const prev = live.prevention || {};
    const cws = live.cpu_warn_state || {};
    const line = prev.founder_line || cws.founder_line;
    if (line) gradeEl.textContent = line;
  }

  function paintLivePulse(live) {
    if (!live || !live.ok) return;
    const pulse = $("heart-pulse");
    const st = live.live_status || "STALE";
    const score = live.score ?? null;
    const wired = live.wired || {};
    if (pulse) {
      pulse.textContent = st === "LIVE" ? "LIVE" : `${st} · ${score ?? "—"}`;
      pulse.className = "mhg-badge " + liveBadgeClass(st) + (st === "LIVE" ? " mhg-badge-green mhg-badge-pulse" : "");
    }
    if (score != null) {
      paintScoreRing(score, live.grade || "", live.security_score, {
        cursorEmergency: live.cursor_emergency,
        preventionModes: (live.prevention && live.prevention.modes) || [],
      });
    }
    paintLiveNarrative(live);
    const h1 = live.h1_sync || {};
    const h1el = $("h1-status");
    if (h1el) {
      const stLive = live.live_status || "LIVE";
      if (h1.ok && stLive === "LIVE") {
        h1el.hidden = true;
      } else if (h1.ok) {
        h1el.hidden = false;
        h1el.textContent = `Hub · Valid ${h1.valid_yes ?? "—"}/1000`;
        h1el.className = "mhg-meta mhg-h1-sync-line stale";
      } else {
        h1el.hidden = false;
        h1el.textContent = "Hub offline — auto heal still runs here";
        h1el.className = "mhg-meta mhg-h1-sync-line offline";
      }
    }
    if (live.machine_pressure) {
      if (lastReport) lastReport.machine_pressure = live.machine_pressure;
      if (rhythmPanelVisible()) {
        renderPressure(live.machine_pressure, null, {
          ageSec: wired.pressure_age_sec ?? wired.live_age_sec,
          liveStatus: st,
          pulseSec: wired.pulse_interval_sec || 8,
          at: live.at,
        });
      }
    }
    paintPreventionBanner(live);
    paintCursorHotBanner(live);
    paintPlaywrightBanner(live);
    paintLogShield(live);
    if (activeTab === "ram" && live.machine_pressure && live.machine_pressure.ram_truth) {
      const wired = live.wired || {};
      const age = wired.pressure_age_sec ?? wired.live_age_sec ?? 0;
      renderRamTruth(live.machine_pressure.ram_truth, {
        ageSec: age,
        liveStatus: live.live_status || "LIVE",
        securityScore: live.security_score,
        bodyScore: live.score,
      });
    }
    if (live.history && live.history.length && activeTab === "rhythm") {
      renderHistory(live.history);
    }
    paintStrangerAgentTile(live);
    paintCpuLadder(live);
    const meta = $("scan-meta");
    if (meta && wired.live_age_sec != null) {
      const fw = live.firewall_enabled ? "Firewall ON" : "Firewall OFF";
      const mp = live.machine_pressure || {};
      const cpu =
        mp.system_cpu_busy_pct != null
          ? `CPU ${Number(mp.system_cpu_busy_pct).toFixed(1)}%`
          : mp.cpu_pct != null
            ? `CPU ${mp.cpu_pct}%`
            : "";
      const ram = mp.ram_used_pct != null ? `RAM ${mp.ram_used_pct}%` : "";
      const rhythm = [cpu, ram].filter(Boolean).join(" · ");
      const cur = mp.cursor || {};
      const liveModes = (live.prevention && live.prevention.modes) || [];
      const curBit =
        liveModes.includes("cursor_hot")
          ? `Cursor hot ${cur.cpu_sum || "?"}%`
          : cur.cpu_sum >= 120
            ? `Cursor ${cur.cpu_sum}%`
            : "";
      meta.textContent = `LIVE ${Math.round(wired.live_age_sec)}s ago · ${rhythm || "pulse"}${curBit ? " · " + curBit : ""} · ${fw}`;
    }
  }

  async function fetchLive() {
    const res = await fetch(`${API}/api/mac-health/live`, { cache: "no-store" });
    const json = await res.json();
    if (!json.ok) throw new Error("live failed");
    return json;
  }

  function paintStrangerAgentTile(live) {
    const wrap = $("stranger-agent-tile");
    if (!wrap) return;
    const sa = (live && live.stranger_agent) || {};
    const tile = sa.hub_tile || {};
    const badge = tile.badge || (sa.stranger_active_count > 0 ? "QUARANTINE" : "ADMIT");
    const risk = sa.risk_score != null ? sa.risk_score : "?";
    const level =
      sa.risk_level ||
      (typeof risk === "number" && risk <= 40 ? "low" : typeof risk === "number" && risk <= 70 ? "medium" : "high");
    const tier = sa.trust_tier || (tile.subtitle || "").split("·").pop()?.trim() || "unknown";
    const oneLine = sa.one_line || tile.subtitle || "sascip · monitor · idle";
    const st = badge === "ADMIT" ? "pass" : badge === "QUARANTINE" ? "critical" : "medium";
    wrap.innerHTML = `<article class="mhg-feature-card mhg-sascip-card status-${esc(st)}">
      <div class="mhg-feature-top">
        <div class="mhg-feature-icon" aria-hidden="true">SA</div>
        <div class="mhg-feature-meta">
          <div class="mhg-feature-eyebrow">SASCIP · Agent admission</div>
          <div class="mhg-feature-title">${esc(tile.title || "Stranger Agent Safety")}</div>
        </div>
        <span class="mhg-feature-badge ${esc(st)}">${esc(badge)}</span>
      </div>
      <div class="mhg-feature-stats">
        <div><span class="lbl">Trust tier</span><span class="val">${esc(tier)}</span></div>
        <div><span class="lbl">Risk</span><span class="val">${esc(String(risk))} · ${esc(level)}</span></div>
        <div><span class="lbl">Active strangers</span><span class="val">${esc(String(sa.stranger_active_count ?? 0))}</span></div>
      </div>
      <p class="mhg-feature-line">${esc(oneLine)}</p>
    </article>`;
  }

  function scoreRingClass(score) {
    if (score >= 90) return "excellent";
    if (score >= 75) return "good";
    if (score >= 55) return "fair";
    return "at-risk";
  }

  function parseLoadTriplet(raw) {
    if (!raw) return null;
    const m = String(raw).match(/([\d.]+)\s+([\d.]+)\s+([\d.]+)/);
    if (!m) return null;
    return { m1: parseFloat(m[1]), m5: parseFloat(m[2]), m15: parseFloat(m[3]) };
  }

  function loadNarrative(loadRaw, cores) {
    const t = parseLoadTriplet(loadRaw);
    if (!t || !cores) {
      return { value: "—", sub: "", story: "How many CPU lanes are busy right now.", cls: "ok" };
    }
    const busy = t.m1;
    const pct = Math.round((busy / cores) * 100);
    let cls = "ok";
    let story = `${busy.toFixed(1)} of ${cores} CPU lanes busy (${pct}%) — a light, healthy shift.`;
    if (busy >= cores) {
      cls = "bad";
      story = `All ${cores} lanes busy with a queue forming. Close heavy apps if this persists.`;
    } else if (busy >= cores * 0.6) {
      cls = "warn";
      story = `${busy.toFixed(1)} of ${cores} lanes busy — fine for now; watch if it stays high.`;
    }
    return {
      value: `${busy.toFixed(1)} / ${cores}`,
      sub: `1 min ${t.m1.toFixed(1)} · 5 min ${t.m5.toFixed(1)} · 15 min ${t.m15.toFixed(1)}`,
      story,
      cls,
    };
  }

  function humanizeDetail(text) {
    if (!text) return "";
    const t = String(text).trim();
    if (/state\s*=\s*0/i.test(t) || /firewall is disabled/i.test(t)) {
      return "Your Mac is not filtering incoming network connections.";
    }
    if (/filevault is off/i.test(t)) return "Your files are not encrypted at rest on this disk.";
    if (/disk live wire|validate-disk-live-wire|mirror inject/i.test(t)) {
      if (/FAIL:/i.test(t)) return t.split("\n").find((l) => /FAIL:/i.test(l)) || "Disk live wire needs a sync — tap Brain heal.";
      if (/OK:/i.test(t)) return "Disk truth bundle is synced — factory queue and mirror inject are healthy.";
      return "Disk live wire — tap Brain heal to refresh truth bundle and queue.";
    }
    if (t.length > 120 && t.includes("\n")) return t.split("\n")[0].slice(0, 120);
    return t;
  }

  function formatHistoryWhen(iso) {
    if (!iso) return "";
    try {
      return new Date(iso).toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    } catch {
      return iso.slice(0, 16).replace("T", " ");
    }
  }

  function domainLabel(key) {
    const map = {
      os: "macOS",
      sip: "System Integrity (SIP)",
      gatekeeper: "Gatekeeper",
      firewall: "Firewall",
      filevault: "FileVault",
      updates: "Software updates",
      listeners: "Network listeners",
      launch_items: "Launch agents",
      remote_access: "Remote login",
      disk: "Disk space",
      xprotect: "XProtect",
    };
    return map[key] || key;
  }

  function domainDetail(key, d) {
    if (!d) return "";
    if (key === "os") return d.version ? `v${d.version}` : "";
    if (key === "updates") return d.pending_count ? `${d.pending_count} pending` : "Current";
    if (key === "listeners") return `${d.count || 0} open`;
    if (key === "disk") return d.root_pct_used != null ? `${d.root_pct_used}% used` : "";
    if (key === "firewall") return d.enabled ? (d.stealth ? "On · sealed" : "On · stealth off") : "Off · open valve";
    if (key === "filevault") return d.enabled ? "On" : "Off";
    if (key === "sip") return d.enabled ? "Enabled" : "Disabled";
    if (key === "gatekeeper") return d.enabled ? "Enabled" : "Disabled";
    if (key === "remote_access") return d.ssh_enabled ? "SSH on" : "SSH off";
    if (key === "launch_items") return `${d.user_launch_agents || 0} user agents`;
    return d.ok === false ? "Review" : "Well";
  }

  function formatScanWhen(iso) {
    if (!iso) return "";
    try {
      const d = new Date(iso);
      return d.toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return iso.slice(0, 19).replace("T", " ");
    }
  }

  function ramDelta(cur, prev) {
    if (prev == null || cur == null) return "";
    const d = Number(cur) - Number(prev);
    if (Math.abs(d) < 0.05) return "";
    const arrow = d > 0 ? "↑" : "↓";
    const cls = d > 0 ? "up" : "down";
    return `<span class="mhg-ram-delta ${cls}">${arrow}${Math.abs(d).toFixed(1)} GB</span>`;
  }

  function renderRamTruth(rt, liveMeta) {
    const totalEl = $("ram-truth-total");
    const explainEl = $("ram-truth-explain");
    const summary = $("ram-truth-summary");
    const list = $("ram-truth-list");
    const liveEl = $("ram-truth-live");
    if (!list) return;
    if (liveEl) {
      if (liveMeta && liveMeta.ageSec != null) {
        const st = liveMeta.liveStatus || "LIVE";
        const sec = liveMeta.securityScore;
        const body = liveMeta.bodyScore;
        const dual =
          sec != null && body != null && sec !== body ? ` · Body ${body} · Security ${sec}` : "";
        liveEl.textContent = `${st} · updated ${Math.round(liveMeta.ageSec)}s ago · real process sample${dual}`;
        liveEl.className = "mhg-ram-truth-live " + (st === "LIVE" ? "live" : "stale");
      } else {
        liveEl.textContent = "Waiting for live pulse…";
        liveEl.className = "mhg-ram-truth-live";
      }
    }
    if (!rt || !rt.ok || !Array.isArray(rt.hogs) || !rt.hogs.length) {
      if (totalEl) totalEl.textContent = "Tap Refresh sample or open this tab after report loads.";
      if (explainEl) explainEl.textContent = "";
      if (summary) summary.textContent = "";
      list.innerHTML = "";
      return;
    }
    if (totalEl) {
      const totalLine = rt.total_line || `${rt.ram_used_gb ?? "?"} GB TOTAL in use`;
      const prevTotal = lastRamSnapshot && lastRamSnapshot.ram_used_gb;
      totalEl.innerHTML = esc(totalLine) + ramDelta(rt.ram_used_gb, prevTotal);
    }
    if (explainEl) {
      explainEl.textContent =
        rt.explain_line ||
        "Top rows are slices of the total — not a second total.";
    }
    if (summary) {
      const b = rt.breakdown || {};
      summary.textContent =
        rt.founder_line ||
        `Cursor ${b.cursor_gb ?? "?"} GB + hub ${b.hub_gb ?? 0} GB + other ${b.other_gb ?? "?"} GB = ${rt.ram_used_gb ?? "?"} GB total`;
    }
    const prevHogs = (lastRamSnapshot && lastRamSnapshot.hogs) || {};
    list.innerHTML = rt.hogs
      .map((h) => {
        const gb = h.gb != null ? `${h.gb} GB` : h.mb != null ? `${h.mb} MB` : "—";
        const share = h.share_label ? ` · ${h.share_label}` : "";
        const hogKey = h.id || h.label;
        const prevGb = prevHogs[hogKey];
        const delta =
          h.gb != null ? ramDelta(h.gb, prevGb) : h.mb != null ? ramDelta(h.mb / 1024, prevGb) : "";
        const tap = h.tap_action
          ? `<button type="button" class="mhg-ram-tap" data-tap="${esc(h.tap_action)}">${esc(h.tap_label || "Fix")}</button>`
          : h.tap_label
            ? `<span class="mhg-ram-hint">${esc(h.tap_label)}</span>`
            : "";
        return `<li class="mhg-ram-hog mhg-ram-${esc(h.cls || "ok")}">
          <span class="mhg-ram-rank">#${h.rank}</span>
          <div class="mhg-ram-body">
            <div class="mhg-ram-row">
              <strong class="mhg-ram-label">${esc(h.label)}</strong>
              <span class="mhg-ram-mb">${esc(gb)}${esc(share)}${delta}</span>
            </div>
            <p class="mhg-ram-detail">${esc(h.detail || "")}</p>
            ${tap}
          </div>
        </li>`;
      })
      .join("");
    const hogMap = {};
    rt.hogs.forEach((h) => {
      const key = h.id || h.label;
      hogMap[key] = h.gb != null ? h.gb : h.mb != null ? h.mb / 1024 : null;
    });
    lastRamSnapshot = {
      ram_used_gb: rt.ram_used_gb,
      hogs: hogMap,
      at: Date.now(),
    };
    list.querySelectorAll(".mhg-ram-tap").forEach((btn) => {
      btn.addEventListener("click", () => runTapAction(btn.getAttribute("data-tap")));
    });
  }

  function renderPressure(mp, pressureLine, liveMeta) {
    const grid = $("pressure-grid");
    const lead = $("pressure-lead");
    const liveStamp = $("pressure-live");
    if (!grid || !mp) return;
    grid.setAttribute("aria-busy", "false");
    if (liveStamp && liveMeta) {
      const age =
        liveMeta.ageSec != null && !Number.isNaN(Number(liveMeta.ageSec))
          ? Math.max(0, Math.round(Number(liveMeta.ageSec)))
          : null;
      const st = liveMeta.liveStatus || "LIVE";
      liveStamp.textContent = age != null ? `Updated ${age}s ago · ${st}` : st;
      liveStamp.className =
        "mhg-meta mhg-stats-updated " +
        (st === "LIVE" ? "live" : st === "OFFLINE" ? "offline" : "stale");
    }
    const ghost = mp.ghost_terminals ?? 0;
    const qz = mp.queue_zombies ?? 0;
    const disk = mp.disk_root_pct;
    const cores = mp.cpu_cores || 18;
    const load = loadNarrative(mp.loadavg, cores);

    if (lead) {
      lead.hidden = true;
      if (pressureLine) {
        lead.textContent = pressureLine;
        lead.hidden = false;
      }
    }

    const bgIssues = qz + ghost;
    const cpuVal =
      mp.system_cpu_busy_pct != null
        ? `${Number(mp.system_cpu_busy_pct).toFixed(0)}%`
        : mp.cpu_pct != null
          ? `${mp.cpu_pct}%`
          : "—";
    const cpuCls =
      (mp.system_cpu_busy_pct != null ? mp.system_cpu_busy_pct : mp.cpu_pct) >= 85
        ? "bad"
        : (mp.system_cpu_busy_pct != null ? mp.system_cpu_busy_pct : mp.cpu_pct) >= 70
          ? "warn"
          : "ok";

    const cards = [
      {
        label: "Memory",
        value: mp.ram_used_pct != null ? `${mp.ram_used_pct}%` : "—",
        sub: mp.ram_used_gb != null && mp.ram_gb ? `${mp.ram_used_gb} / ${mp.ram_gb} GB` : "",
        cls: qz >= 20 ? "bad" : qz >= 8 ? "warn" : mp.ram_used_pct >= 90 ? "bad" : mp.ram_used_pct >= 80 ? "warn" : "ok",
        tap: qz > 0 ? "pipeline" : null,
      },
      {
        label: "CPU",
        value: cpuVal,
        sub: mp.cursor && mp.cursor.cpu_sum != null ? `Cursor ${mp.cursor.cpu_sum}%` : "",
        cls: cpuCls,
        tap: cpuCls !== "ok" ? "cpu_cool_down" : null,
      },
      {
        label: "Disk",
        value: disk != null ? `${disk}%` : "—",
        sub: disk != null && disk < 75 ? "Room to spare" : disk != null && disk >= 90 ? "Very full" : "",
        cls: disk >= 90 ? "bad" : disk >= 75 ? "warn" : "ok",
      },
      {
        label: "Background",
        value: bgIssues === 0 ? "Clear" : String(bgIssues),
        sub: bgIssues === 0 ? "No leaks" : `${qz} pipeline · ${ghost} ghosts`,
        cls: bgIssues >= 3 ? "bad" : bgIssues > 0 ? "warn" : "ok",
        tap: bgIssues > 0 ? "heal" : null,
      },
    ];

    grid.innerHTML = cards
      .map(
        (c) => `<article class="mhg-stat${c.tap ? " mhg-stat-tap" : ""}"${c.tap ? ` data-tap="${esc(c.tap)}" role="button" tabindex="0"` : ""}>
          <span class="mhg-stat-label">${esc(c.label)}</span>
          <span class="mhg-stat-value ${esc(c.cls)}">${esc(c.value)}</span>
          ${c.sub ? `<span class="mhg-stat-sub">${esc(c.sub)}</span>` : ""}
        </article>`
      )
      .join("");
    if (activeTab === "ram") renderRamTruth(mp.ram_truth);
    grid.querySelectorAll("[data-tap]").forEach((el) => {
      el.addEventListener("click", () => runTapAction(el.getAttribute("data-tap")));
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          runTapAction(el.getAttribute("data-tap"));
        }
      });
    });
  }

  function renderAgents(agents) {
    const grid = $("agents-grid");
    if (!grid) return;
    grid.innerHTML = (agents || [])
      .map((a) => {
        const st = SEV_CLASS[a.status] || "info";
        const statusWord = AGENT_STATUS[st] || a.status;
        const initials = String(a.name || "?")
          .split(/\s+/)
          .map((w) => w[0])
          .join("")
          .slice(0, 2)
          .toUpperCase();
        return `<article class="mhg-agent-card status-${esc(st)}">
          <div class="mhg-agent-head">
            <span class="mhg-agent-avatar" aria-hidden="true">${esc(initials)}</span>
            <div>
              <div class="mhg-agent-name">${esc(a.name)}</div>
              <div class="mhg-agent-role">${esc(a.role)}</div>
            </div>
          </div>
          <p class="mhg-agent-mission">${esc(a.mission)}</p>
          <p class="mhg-agent-finding">${esc(a.top_finding)}</p>
          <div class="mhg-agent-status-row">
            <span class="mhg-pill ${esc(st)}">${esc(statusWord)}</span>
            <span class="mhg-agent-hint">Lane monitor</span>
          </div>
        </article>`;
      })
      .join("");
  }

  function findingNarrative(f) {
    return f.title || "";
  }

  function renderFindings(findings) {
    const list = $("findings-list");
    if (!list) return;
    const notable = (findings || []).filter((f) => f.severity !== "info");
    const section = $("findings-section");
    if (section) section.hidden = notable.length === 0;
    if (!notable.length) {
      list.innerHTML = `<li class="mhg-finding mhg-finding-clear">
        <div class="mhg-finding-title">All clear on every security lane</div>
        <p>No urgent rhythms. Listen again after travel, new apps, or permission changes.</p>
      </li>`;
      return;
    }
    list.innerHTML = notable
      .map((f) => {
        const tap = f.tap_action || "";
        const btn = tap
          ? `<button type="button" class="mhg-finding-btn" data-tap="${esc(tap)}">${esc(f.action || "Fix now")}</button>`
          : `<div class="mhg-finding-action">Manual → ${esc(f.action)}</div>`;
        return `<li class="mhg-finding">
          <span class="mhg-pill ${esc(SEV_CLASS[f.severity] || "info")}">${esc(SEV_WORDS[f.severity] || f.severity)}</span>
          <div class="mhg-finding-title">${esc(findingNarrative(f))}</div>
          ${f.detail ? `<p class="mhg-finding-detail">${esc(humanizeDetail(f.detail))}</p>` : ""}
          ${btn}
        </li>`;
      })
      .join("");
    list.querySelectorAll(".mhg-finding-btn[data-tap]").forEach((btn) => {
      btn.addEventListener("click", () => runTapAction(btn.getAttribute("data-tap")));
    });
  }

  function renderDomains(domains) {
    const grid = $("domains-grid");
    if (!grid || !domains) return;
    const keys = DOMAIN_ORDER.filter((k) => k in domains);
    grid.innerHTML = keys
      .map((key) => {
        const d = domains[key];
        const detail = domainDetail(key, d);
        const ok = d && d.ok !== false;
        const cls = ok ? "mhg-domain-ok" : "mhg-domain-bad";
        const icon = ok ? "✓" : "!";
        return `<div class="mhg-domain">
          <div class="mhg-domain-main">
            <span class="mhg-domain-name">${esc(domainLabel(key))}</span>
            <span class="mhg-domain-story">${esc(DOMAIN_STORY[key] || "")}</span>
          </div>
          <span class="mhg-domain-detail">${esc(detail)} <span class="${cls}">${icon}</span></span>
        </div>`;
      })
      .join("");
  }

  function renderSources(knowledge) {
    const grid = $("sources-grid");
    const sources = (knowledge && knowledge.sources) || [];
    grid.innerHTML = sources
      .map(
        (s) => `<div class="mhg-source">
          <a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)}</a>
          <p>${esc(s.focus)}</p>
        </div>`
      )
      .join("");
  }

  function renderHistory(history) {
    const chart = $("history-chart");
    const rows = history || [];
    if (!rows.length) {
      chart.innerHTML = `<p class="mhg-meta">No history yet — live pulses begin logging after the first minute.</p>`;
      return;
    }
    const max = Math.max(...rows.map((r) => r.score || 0), 1);
    const min = Math.min(...rows.map((r) => r.score || 0), max);
    chart.innerHTML = rows
      .map((r) => {
        const h = Math.round(((r.score || 0) / max) * 72) + 8;
        const when = formatHistoryWhen(r.at);
        const grade = r.grade || "";
        const cpu = r.cpu_pct != null ? `CPU ${r.cpu_pct}%` : "";
        const ram = r.ram_used_pct != null ? `RAM ${r.ram_used_pct}%` : "";
        const rhythm = [cpu, ram].filter(Boolean).join(" · ");
        const cls = scoreRingClass(r.score || 0);
        return `<div class="mhg-bar ${cls}" style="height:${h}px" title="Score ${r.score}${grade ? " · " + esc(grade) : ""}${rhythm ? " · " + esc(rhythm) : ""} · ${esc(when)}"></div>`;
      })
      .join("");
    const latest = rows[rows.length - 1];
    const lead = $("history-lead");
    if (lead) {
      const spread = max - min;
      lead.textContent =
        spread >= 3
          ? `Live pulses — score moved ${min}→${max} with CPU and RAM pressure.`
          : `Live pulses — score ${latest.score ?? "—"} · ${latest.grade ?? ""} · bars update every ~2 min or when pressure shifts.`;
    }
  }

  function renderImportantNote(note) {
    const n = note || {};
    if ($("important-privacy") && n.privacy) {
      $("important-privacy").textContent = n.privacy;
    }
    if ($("important-scan") && n.when_to_scan) {
      $("important-scan").textContent = n.when_to_scan;
    }
    if ($("important-firewall") && n.firewall_hint) {
      $("important-firewall").textContent = n.firewall_hint;
    }
  }

  function paintNarrative(data) {
    const fn = data.founder_narrative || {};
    const gradeEl = $("grade-story");
    const nextEl = $("next-tap");
    const poem = $("founder-poem");

    if (gradeEl) gradeEl.textContent = fn.grade_story || "";
    if (nextEl) {
      const urgent = fn.urgent_blocker_count ?? 0;
      const cpu = (data.machine_pressure && data.machine_pressure.cpu_pct) || 0;
      const isRestartCursor = String(fn.next_tap || "").toLowerCase().includes("restart cursor");
      const show =
        fn.next_tap &&
        !isRestartCursor &&
        (data.score < 65 || urgent > 0 || (cpu >= 85 && fn.next_tap_action));
      if (show && fn.next_tap_action) {
        const act = fn.next_tap_action;
        nextEl.innerHTML = `<strong>Your next tap</strong> <button type="button" class="mhg-next-tap-btn" data-tap="${esc(act)}">${esc(fn.next_tap)}</button>`;
        nextEl.hidden = false;
        const btn = nextEl.querySelector(".mhg-next-tap-btn");
        if (btn) btn.addEventListener("click", () => runTapAction(btn.getAttribute("data-tap")));
      } else {
        nextEl.hidden = true;
      }
    }
    const setPoemLine = (id, label, text) => {
      const el = $(id);
      if (el && text) el.innerHTML = `<em>${label}</em> — ${esc(text)}`;
    };
    if (poem) {
      setPoemLine("poem-body", "Body", fn.body);
      setPoemLine("poem-heart", "Heart", fn.heart);
      setPoemLine("poem-brain", "Brain", fn.brain);
      const safety = $("poem-safety");
      if (safety && fn.safety_line) {
        safety.textContent = fn.safety_line;
      }
    }
  }

  function paintActionReceipt(data) {
    const el = $("heal-msg");
    if (!el) return;
    const r = data.action_receipt;
    if (!r || r.action !== lastAction) return;
    el.textContent = r.summary || `${r.action} complete`;
    el.className = "mhg-heal-msg" + (r.ran_ok !== false ? "" : " warn");
    if (Array.isArray(r.steps) && r.steps.length) {
      el.title = r.steps.join("\n");
    }
    el.hidden = false;
  }

  function paintHeal(heal) {
    const el = $("heal-msg");
    if (!el) return;
    if (lastAction === "scan") {
      return;
    }
    if (lastAction === "ram_purge") {
      return;
    }
    if (!heal || (lastAction !== "heal" && lastAction !== "pipeline" && !lastAction.startsWith("cpu_"))) {
      if (lastAction !== "scan") el.hidden = true;
      return;
    }
    if (heal.cpu_relief_only || lastAction.startsWith("cpu_")) {
      const summary = heal.summary || "Cool Down complete";
      const cpuB = heal.cpu_before;
      const cpuA = heal.cpu_after;
      el.textContent =
        cpuB != null && cpuA != null
          ? `Cool Down · ${summary} · CPU ${cpuB}% → ${cpuA}%`
          : `Cool Down · ${summary}`;
      el.className = "mhg-heal-msg" + (heal.improved || heal.ran_ok ? "" : " warn");
      el.hidden = false;
      return;
    }
    const fw = heal.firewall || {};
    const pipe = heal.pipeline || {};
    const parts = [];
    if (lastAction === "pipeline" || heal.pipeline_only) {
      const k = pipe.killed ?? 0;
      const before = pipe.before ?? 0;
      const after = pipe.after ?? 0;
      parts.push(`killed ${k} queue zombie${k === 1 ? "" : "s"} (${before} → ${after})`);
      if (heal.after_score != null) {
        parts.push(`score ${heal.before_score} → ${heal.after_score}`);
      }
      el.textContent = `Pipeline clear · ${parts.join(" · ")}.`;
      el.className = "mhg-heal-msg" + (k > 0 || after < 8 || heal.ran_ok ? "" : " warn");
      el.hidden = false;
      return;
    }
    parts.push(`Score ${heal.before_score} → ${heal.after_score} (${heal.after_grade})`);
    if (heal.cart && heal.cart.patched) {
      parts.push(`cleared ${heal.cart.patched} ghost shell${heal.cart.patched === 1 ? "" : "s"}`);
    }
    if (pipe.killed) {
      parts.push(`killed ${pipe.killed} queue zombie${pipe.killed === 1 ? "" : "s"}`);
    }
    if (fw.enabled) parts.push("Firewall is ON");
    else if (fw.founder_tap) parts.push(fw.founder_tap);
    el.textContent = `Brain heal complete · ${parts.join(" · ")}.`;
    el.className = "mhg-heal-msg" + (heal.improved || heal.ran_ok || fw.enabled ? "" : " warn");
    el.hidden = false;
  }

  function paintCooldownLive(live) {
    const el = $("cooldown-live");
    if (!el) return;
    const mp = (live && live.machine_pressure) || (lastReport && lastReport.machine_pressure) || {};
    const prev = (live && live.prevention) || (lastReport && lastReport.prevention) || {};
    const cpu = mp.cpu_pct ?? live?.cpu_pct;
    const load = mp.load_1min ?? live?.load_1min;
    const cores = mp.cpu_cores ?? 18;
    const cursor = prev.cursor || {};
    if (cpu == null) {
      el.textContent = "CPU reading…";
      return;
    }
    const wakeStorm = (prev.modes || []).includes("wake_storm");
    const wakeBtn = $("btn-wake-cool-down");
    if (wakeBtn) {
      wakeBtn.hidden = !wakeStorm;
      wakeBtn.classList.toggle("mhg-cooldown-wake-active", wakeStorm);
    }
    let text = `CPU ${cpu}% · load ${load ?? "?"}/${cores} lanes`;
    if (wakeStorm) {
      text += ` · Wake storm (${Math.round(prev.uptime_min || 0)} min) — tap Wake Cool Down`;
      el.className = "mhg-cooldown-live hot";
    } else if ((prev.modes || []).includes("cursor_busy")) {
      const rss = cursor.rss_mb ? (cursor.rss_mb / 1024).toFixed(1) : "?";
      text += ` · Cursor busy (${cursor.cpu_sum ?? "?"}% · ${rss} GB) — normal while you work`;
      el.className = "mhg-cooldown-live ok";
    } else if ((prev.modes || []).includes("cursor_hot")) {
      text += ` · Cursor emergency ${cursor.cpu_sum ?? "?"}% — optional restart in Cool Down only`;
      el.className = "mhg-cooldown-live hot";
    } else {
      el.className = "mhg-cooldown-live" + (cpu >= 90 ? " hot" : cpu < 60 ? " ok" : "");
    }
    if (prev.factory_frozen) text += " · auto-run OFF";
    el.textContent = text;
  }

  function renderSettingsExplainer(explainer) {
    const el = $("settings-explainer");
    if (!el || !explainer) return;
    const steps = explainer.steps || [];
    el.innerHTML =
      `<p><strong>${esc(explainer.summary || "")}</strong></p>` +
      `<ol>${steps
        .map(
          (s) =>
            `<li><strong>${esc(s.title)}</strong> — ${esc(s.detail)}</li>`
        )
        .join("")}</ol>`;
  }

  function renderSettingsForm(schema, values) {
    const form = $("settings-form");
    if (!form || !schema) return;
    form.innerHTML = (schema || [])
      .map((group) => {
        const gv = (values && values[group.group]) || {};
        const fields = (group.fields || [])
          .map((f) => {
            const id = `setting-${group.group}-${f.key}`;
            const val = gv[f.key];
            if (f.type === "bool") {
              return `<div class="mhg-settings-field">
                <label for="${id}">${esc(f.label)}</label>
                <input type="checkbox" id="${id}" data-group="${esc(group.group)}" data-key="${esc(f.key)}" ${val ? "checked" : ""} />
                ${f.help ? `<p class="mhg-settings-field-help">${esc(f.help)}</p>` : ""}
              </div>`;
            }
            if (f.type === "select") {
              const opts = (f.options || [])
                .map(
                  (o) =>
                    `<option value="${esc(o.value)}"${String(val) === String(o.value) ? " selected" : ""}>${esc(o.label)}</option>`
                )
                .join("");
              return `<div class="mhg-settings-field">
                <label for="${id}">${esc(f.label)}</label>
                <select id="${id}" data-group="${esc(group.group)}" data-key="${esc(f.key)}" data-type="select">${opts}</select>
                ${f.help ? `<p class="mhg-settings-field-help">${esc(f.help)}</p>` : ""}
              </div>`;
            }
            return `<div class="mhg-settings-field">
              <label for="${id}">${esc(f.label)}</label>
              <input type="number" id="${id}" data-group="${esc(group.group)}" data-key="${esc(f.key)}"
                min="${f.min != null ? f.min : ""}" max="${f.max != null ? f.max : ""}" step="${f.step || 1}"
                value="${val != null ? esc(String(val)) : ""}" />
              ${f.help ? `<p class="mhg-settings-field-help">${esc(f.help)}</p>` : ""}
            </div>`;
          })
          .join("");
        return `<fieldset class="mhg-settings-group">
          <h3>${esc(group.title)}</h3>
          ${group.help ? `<p class="mhg-settings-group-help">${esc(group.help)}</p>` : ""}
          ${fields}
        </fieldset>`;
      })
      .join("");
  }

  function collectSettingsFromForm() {
    const form = $("settings-form");
    const patch = {};
    if (!form) return patch;
    form.querySelectorAll("[data-group][data-key]").forEach((el) => {
      const g = el.getAttribute("data-group");
      const k = el.getAttribute("data-key");
      if (!g || !k) return;
      if (!patch[g]) patch[g] = {};
      if (el.type === "checkbox") patch[g][k] = el.checked;
      else if (el.tagName === "SELECT" || el.getAttribute("data-type") === "select") patch[g][k] = el.value;
      else patch[g][k] = Number(el.value);
    });
    return patch;
  }

  function paintSettings(data) {
    const summary = $("settings-summary");
    const paths = $("settings-paths");
    if (summary && data.auto_guard_explainer) {
      summary.textContent = data.auto_guard_explainer.summary || summary.textContent;
    }
    renderSettingsExplainer(data.auto_guard_explainer);
    renderSettingsForm(data.settings_schema || data.schema, data.settings || data.values);
    if (paths && data.auto_guard_explainer && data.auto_guard_explainer.config_paths) {
      const p = data.auto_guard_explainer.config_paths;
      paths.textContent = `Saved to: ${p.panic} · ${p.prevention}`;
    }
  }

  async function fetchSettings(action, patch) {
    const res = await fetch(`${API}/api/mac-health`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, standalone: true, settings: patch || undefined }),
    });
    const json = await res.json();
    if (!json.ok) throw new Error(json.error || "settings failed");
    return json;
  }

  async function saveSettings() {
    const msg = $("settings-msg");
    const btn = $("btn-settings-save");
    try {
      if (btn) btn.disabled = true;
      if (msg) {
        msg.hidden = false;
        msg.textContent = "Saving…";
        msg.className = "mhg-settings-msg";
      }
      const patch = collectSettingsFromForm();
      const data = await fetchSettings("settings_save", patch);
      if (lastReport) {
        lastReport.settings = data.values;
        lastReport.auto_guard_explainer = data.explainer;
        lastReport.settings_schema = data.schema;
      }
      paintSettings({
        settings: data.values,
        settings_schema: data.schema,
        auto_guard_explainer: data.explainer,
      });
      if (msg) {
        msg.hidden = false;
        msg.textContent = "Settings saved — auto guard updated on disk.";
        msg.className = "mhg-settings-msg ok";
      }
    } catch (e) {
      if (msg) {
        msg.textContent = e.message;
        msg.className = "mhg-settings-msg warn";
        msg.hidden = false;
      }
    } finally {
      if (btn) btn.disabled = false;
    }
  }

  async function resetSettings() {
    if (!window.confirm("Reset all auto-guard settings to defaults?")) return;
    const msg = $("settings-msg");
    try {
      const data = await fetchSettings("settings_reset");
      if (lastReport) {
        lastReport.settings = data.values;
        lastReport.auto_guard_explainer = data.explainer;
        lastReport.settings_schema = data.schema;
      }
      paintSettings({
        settings: data.values,
        settings_schema: data.schema,
        auto_guard_explainer: data.explainer,
      });
      if (msg) {
        msg.hidden = false;
        msg.textContent = "Reset to defaults.";
        msg.className = "mhg-settings-msg";
      }
    } catch (e) {
      if (msg) {
        msg.textContent = e.message;
        msg.className = "mhg-settings-msg warn";
        msg.hidden = false;
      }
    }
  }

  function setActiveTab(tab) {
    activeTab = "rhythm";
    scheduleLivePoll();
    if (Date.now() - lastLiveTickMs > LIVE_MIN_GAP_MS) {
      tickLive();
    }
    if (tab === "settings" && lastReport) {
      paintSettings({
        settings: lastReport.settings,
        settings_schema: lastReport.settings_schema,
        auto_guard_explainer: lastReport.auto_guard_explainer,
      });
    }
  }

  function scheduleLivePoll() {
    if (liveTimer) clearInterval(liveTimer);
    const ms = activeTab === "ram" ? RAM_POLL_MS : RHYTHM_POLL_MS;
    if (!livePollBooted) {
      livePollBooted = true;
      tickLive();
    }
    liveTimer = setInterval(tickLive, ms);
  }

  function paintRamPurge(data) {
    const el = $("ram-purge-result");
    const rp = data.ram_purge || {};
    const receipt = data.action_receipt || {};
    const summary = receipt.summary || rp.detail || "Done";
    if (el) {
      el.textContent = summary;
      el.className = "mhg-ram-purge-result" + (rp.ok ? "" : " warn");
      el.hidden = false;
    }
    const cooldownEl = $("cooldown-result");
    if (cooldownEl && lastAction === "ram_purge" && activeTab === "cooldown") {
      cooldownEl.textContent = summary;
      cooldownEl.className = "mhg-cooldown-result" + (rp.ok ? "" : " warn");
      cooldownEl.hidden = false;
    }
    const msg = $("heal-msg");
    if (msg && lastAction === "ram_purge") {
      msg.textContent = summary;
      msg.className = "mhg-heal-msg" + (rp.ok ? "" : " warn");
      msg.hidden = false;
    }
    if (data.machine_pressure && data.machine_pressure.ram_truth) {
      renderRamTruth(data.machine_pressure.ram_truth);
    }
  }

  function setRamBusy(busy) {
    const purge = $("btn-ram-purge");
    const purgeCd = $("btn-cooldown-ram-purge");
    const refresh = $("btn-ram-refresh");
    if (purge) purge.disabled = busy;
    if (purgeCd) purgeCd.disabled = busy;
    if (refresh) refresh.disabled = busy;
    if (busy) setCooldownBusy(true);
  }

  async function runRamPurge() {
    lastAction = "ram_purge";
    const resultEl = $("ram-purge-result");
    if (resultEl) {
      resultEl.hidden = false;
      resultEl.className = "mhg-ram-purge-result";
      resultEl.textContent = "macOS will ask for your password…";
    }
    setRamBusy(true);
    try {
      const data = await fetchReport("ram_purge");
      lastReport = data;
      paintReport(data);
      paintRamPurge(data);
    } catch (e) {
      if (resultEl) {
        resultEl.textContent = e.message;
        resultEl.className = "mhg-ram-purge-result warn";
      }
      const cooldownEl = $("cooldown-result");
      if (cooldownEl && activeTab === "cooldown") {
        cooldownEl.textContent = e.message;
        cooldownEl.className = "mhg-cooldown-result warn";
        cooldownEl.hidden = false;
      }
    } finally {
      setRamBusy(false);
      setCooldownBusy(false);
    }
  }

  async function refreshRamTruth() {
    setRamBusy(true);
    try {
      const data = await fetchReport("report");
      lastReport = data;
      paintReport(data);
      renderRamTruth((data.machine_pressure || {}).ram_truth);
    } finally {
      setRamBusy(false);
    }
  }

  function paintCpuRelief(data) {
    const el = $("cooldown-result");
    const relief = data.cpu_relief || {};
    const heal = data.heal || {};
    const receipt = data.action_receipt || {};
    if (!el) return;
    const lines = relief.step_lines || heal.step_lines || receipt.steps || [];
    const summary = relief.summary || heal.summary || receipt.summary || "Done";
    const line = relief.founder_line || "";
    const cpuB = relief.before && relief.before.cpu_pct;
    const cpuA = relief.after && relief.after.cpu_pct;
    const cpuLine =
      cpuB != null && cpuA != null ? `CPU ${cpuB}% → ${cpuA}%` : line;
    const body = lines.length
      ? `${summary}\n${lines.map((s) => `• ${s}`).join("\n")}${cpuLine ? `\n${cpuLine}` : ""}`
      : `${summary}${cpuLine ? " · " + cpuLine : ""}`;
    el.textContent = body;
    const ranOk = Boolean(relief.ok || heal.ran_ok || receipt.ran_ok);
    const cursorStillHot = relief.cursor_still_hot;
    el.className =
      "mhg-cooldown-result" +
      (cursorStillHot || !(ranOk || heal.improved || relief.improved) ? " warn" : "");
    el.hidden = false;
    const msg = $("heal-msg");
    if (msg) {
      msg.textContent = `Cool Down · ${summary}`;
      msg.className = "mhg-heal-msg" + (ranOk || heal.improved ? "" : " warn");
      msg.hidden = false;
    }
    paintCooldownLive(data.live || { machine_pressure: data.machine_pressure });
  }

  function setCooldownBusy(busy) {
    document.querySelectorAll(".mhg-cooldown-btn").forEach((b) => {
      b.disabled = busy;
    });
  }

  async function paintPanicReceipt(rec, opts = {}) {
    const { fullStop = false } = opts;
    const msg = $("heal-msg");
    const resultEl = $("cooldown-result");
    const flash = document.getElementById("panic-flash");
    const showFlash = (text, cls) => {
      if (!flash) return;
      flash.textContent = text;
      flash.className = "mhg-panic-flash " + (cls || "active");
      flash.hidden = false;
      setTimeout(() => {
        flash.hidden = true;
      }, 8000);
    };
    const killCount = Number(rec.kill_count ?? (rec.killed_pids || rec.kills || []).length ?? 0);
    const still = rec.still_running || [];
    const coolSteps = ((rec.relief || {}).wake_cool_down || {}).step_lines || [];
    const coolDone = coolSteps.filter(
      (ln) => !/: none$|: clear$|: was off$|: none running$/.test(String(ln))
    );
    const line = rec.founder_line || rec.summary || "Factory frozen";
    const flashCls = killCount > 0 || coolDone.length ? "done" : "warn";
    const headline = fullStop
      ? killCount > 0
        ? `⛔ Full stop — killed ${killCount} process(es) incl. tunnel`
        : "⛔ Full stop — tunnel may already be off"
      : killCount > 0
        ? `⛔ Killed ${killCount} background process(es)`
        : "⛔ Paused factory — Cursor still open";
    showFlash(headline, flashCls);
    if (msg) {
      msg.textContent =
        line +
        (fullStop
          ? " · Republish landing from Hub or publish script."
          : " · NOT stopped: Cursor, Terminal, Claude. For IDE lag → Cool Down → Restart Cursor.");
      msg.className = killCount > 0 || coolDone.length ? "mhg-heal-msg" : "mhg-heal-msg warn";
    }
    if (resultEl) {
      resultEl.textContent = line;
      resultEl.className = flashCls === "done" ? "mhg-cooldown-result" : "mhg-cooldown-result warn";
    }
    if (killCount === 0 && still.length) {
      const top = still
        .slice(0, 3)
        .map((r) => `${(r.comm || "?").slice(0, 24)} ${r.cpu_pct || 0}%`)
        .join(" · ");
      if (resultEl) resultEl.textContent += ` · Still heavy: ${top}`;
    }
    tickLive();
  }

  async function runPanicStop() {
    if (nativeAction("emergency_stop")) return;
    lastAction = "emergency_stop";
    const msg = $("heal-msg");
    const resultEl = $("cooldown-result");
    const flash = document.getElementById("panic-flash");
    if (flash) {
      flash.textContent = "⛔ STOPPING BACKGROUND AGENTS…";
      flash.className = "mhg-panic-flash active";
      flash.hidden = false;
    }
    if (msg) {
      msg.hidden = false;
      msg.className = "mhg-heal-msg warn";
      msg.textContent = "⛔ STOPPING BACKGROUND AGENTS…";
    }
    if (resultEl) {
      resultEl.hidden = false;
      resultEl.className = "mhg-cooldown-result warn";
      resultEl.textContent = "⛔ STOPPING BACKGROUND AGENTS…";
    }
    try {
      const res = await fetch(`${API}/api/mac-health/panic`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
      });
      const data = await res.json();
      const rec = data.emergency_stop || data;
      await paintPanicReceipt(rec, { fullStop: false });
    } catch (e) {
      const err = "STOP failed — double-click ⛔ STOP AGENTS on Desktop";
      if (flash) {
        flash.textContent = err;
        flash.className = "mhg-panic-flash fail";
        flash.hidden = false;
      }
      if (msg) msg.textContent = err;
      if (resultEl) resultEl.textContent = String(e.message || e);
    }
  }

  async function runFullStop() {
    const ok = window.confirm(
      "Full stop kills the landing tunnel (cloudflared :8190) and all background agents.\n\nRepublish landing after. Continue?"
    );
    if (!ok) return;
    lastAction = "full_stop";
    setCooldownBusy(true);
    const msg = $("heal-msg");
    const resultEl = $("cooldown-result");
    const flash = document.getElementById("panic-flash");
    if (flash) {
      flash.textContent = "⛔ FULL STOP — killing tunnel + agents…";
      flash.className = "mhg-panic-flash active";
      flash.hidden = false;
    }
    if (msg) {
      msg.hidden = false;
      msg.className = "mhg-heal-msg warn";
      msg.textContent = "⛔ FULL STOP — killing tunnel + agents…";
    }
    if (resultEl) {
      resultEl.hidden = false;
      resultEl.className = "mhg-cooldown-result warn";
      resultEl.textContent = "⛔ FULL STOP — killing tunnel + agents…";
    }
    try {
      const res = await fetch(`${API}/api/mac-health/panic/full`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
      });
      const data = await res.json();
      const rec = data.emergency_stop || data;
      await paintPanicReceipt(rec, { fullStop: true });
    } catch (e) {
      const err = "Full stop failed — try Desktop STOP AGENTS or touch ~/.sina/PANIC.now";
      if (flash) {
        flash.textContent = err;
        flash.className = "mhg-panic-flash fail";
      }
      if (msg) msg.textContent = err;
      if (resultEl) resultEl.textContent = String(e.message || e);
    } finally {
      setCooldownBusy(false);
    }
  }

  async function runCpuRelief(action) {
    lastAction = action;
    if (action === "cpu_restart_cursor") {
      const ok = window.confirm(
        "Restart Cursor? Save open files first. This fixes a hot agent chat but closes all Cursor windows briefly."
      );
      if (!ok) return;
    }
    setCooldownBusy(true);
    const resultEl = $("cooldown-result");
    if (resultEl) {
      resultEl.hidden = false;
      resultEl.className = "mhg-cooldown-result";
      resultEl.textContent = "Working…";
    }
    try {
      const data = await fetchReport(action);
      lastReport = data;
      paintReport(data);
      paintCpuRelief(data);
      tickLive();
    } catch (e) {
      if (resultEl) {
        resultEl.textContent = e.message;
        resultEl.className = "mhg-cooldown-result warn";
      }
    } finally {
      setCooldownBusy(false);
    }
  }

  function paintReport(data) {
    lastReport = data;
    renderImportantNote(data.important_note);
    paintNarrative(data);
    const fn = data.founder_narrative || {};
    renderPressure(data.machine_pressure, fn.pressure_line);
    const score = data.score ?? 0;
    const gradeLabel = data.grade || "";
    paintScoreRing(score, gradeLabel, data.security_score, {
      cursorEmergency:
        data.cursor_emergency ||
        ((data.prevention && data.prevention.modes) || []).includes("cursor_hot"),
      preventionModes: (data.prevention && data.prevention.modes) || [],
    });
    const scan = data.scan || {};
    const wired = data.wired || {};
    const when = formatScanWhen(scan.scanned_at);
    const live = formatScanWhen(wired.live_refreshed_at || scan.live_refreshed_at);
    const fw = wired.firewall_enabled ? "Firewall ON" : "Firewall OFF";
    const anti = wired.anti_stale || {};
    const liveSt = (data.live && data.live.status) || (anti.live_ok !== false ? "LIVE" : "STALE");
    const fresh = liveSt === "LIVE" ? "LIVE" : liveSt;
    const parts = [];
    if (fresh !== "LIVE") parts.push(fresh);
    parts.push(fw);
    if (when) parts.push(`scan ${when}`);
    $("scan-meta").textContent = parts.join(" · ");
    renderAgents(data.agents);
    renderFindings(data.findings);
    renderDomains(scan.domains);
    renderSources(data.knowledge);
    renderHistory(data.history);
    paintHeal(data.heal);
    paintActionReceipt(data);
    paintPreventionBanner(data);
    paintCursorHotBanner(data);
    paintPlaywrightBanner(data);
    paintCpuLadder(data);
    paintCooldownLive(data);
    if (data.settings || data.auto_guard_explainer) {
      lastReport.settings = data.settings;
      lastReport.settings_schema = data.settings_schema || data.schema;
      lastReport.auto_guard_explainer = data.auto_guard_explainer;
      if (activeTab === "settings") paintSettings(data);
    }
  }

  async function pingHeart() {
    const pulse = $("heart-pulse");
    try {
      const res = await fetch(`${API}/health`);
      const j = await res.json();
      if (pulse && j.ok) {
        pulse.textContent = "LIVE";
        pulse.className = "mhg-badge mhg-badge-green mhg-badge-pulse";
      }
    } catch {
      if (pulse) {
        pulse.textContent = "Offline";
        pulse.className = "mhg-badge mhg-badge-sick";
      }
    }
  }

  async function fetchReport(action) {
    const res = await fetch(`${API}/api/mac-health`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, standalone: true }),
    });
    const json = await res.json();
    if (json.cpu_relief || json.ram_purge || json.heal) return json;
    if (json.ok === false) throw new Error(json.error || "action failed");
    return json;
  }

  async function tickLive() {
    if (document.hidden || liveFetchInFlight) return;
    const nowMs = Date.now();
    if (nowMs - lastLiveTickMs < LIVE_MIN_GAP_MS) return;
    liveFetchInFlight = true;
    lastLiveTickMs = nowMs;
    try {
      const live = await fetchLive();
      if (lastReport && live.prevention) lastReport.prevention = live.prevention;
      paintLivePulse(live);
      paintCooldownLive(live);
    } catch {
      const pulse = $("heart-pulse");
      if (pulse) {
        pulse.textContent = "OFFLINE";
        pulse.className = "mhg-badge mhg-badge-sick";
      }
      const liveStamp = $("pressure-live");
      if (liveStamp && rhythmPanelVisible()) {
        liveStamp.textContent = "OFFLINE — heart not reachable on :13024";
        liveStamp.className = "mhg-pressure-live offline";
      }
    } finally {
      liveFetchInFlight = false;
    }
  }

  async function silentRefresh() {
    if (document.hidden) return;
    if ($("btn-heal")?.disabled || $("btn-rescan")?.disabled) return;
    if ($("btn-pipeline")?.disabled) return;
    try {
      const data = await fetchReport("report");
      paintReport(data);
      tickLive();
    } catch {
      tickLive();
    }
  }

  async function load(action) {
    lastAction = action;
    const btnScan = $("btn-rescan");
    const btnRef = $("btn-refresh");
    const btnHeal = $("btn-heal");
    const btnPipeline = $("btn-pipeline");
    btnScan.disabled = true;
    btnRef.disabled = true;
    if (btnHeal) btnHeal.disabled = true;
    if (btnPipeline) btnPipeline.disabled = true;
    $("score-mood").textContent =
      action === "pipeline"
        ? "Clearing pipeline…"
        : action === "heal"
          ? "Healing…"
          : action === "scan"
            ? "Listening…"
            : "Reading…";
    $("score-grade").textContent = "";
    const msgEl = $("heal-msg");
    if (msgEl && (action === "scan" || action === "heal" || action === "pipeline")) {
      msgEl.hidden = false;
      msgEl.className = "mhg-heal-msg";
      msgEl.textContent =
        action === "scan"
          ? "Listen again — running full macOS security scan…"
          : action === "heal"
            ? "Brain heal — ghosts · pipeline · firewall · rescan…"
            : "Clearing leaked pipeline processes…";
    }
    try {
      const data = await fetchReport(action);
      lastReport = data;
      paintReport(data);
      if (action.startsWith("cpu_")) paintCpuRelief(data);
    } catch (e) {
      $("score-value").textContent = "!";
      $("score-mood").textContent = "";
      $("score-grade").textContent = "Offline";
      $("scan-meta").textContent = e.message;
    } finally {
      btnScan.disabled = false;
      btnRef.disabled = false;
      if (btnHeal) btnHeal.disabled = false;
      if (btnPipeline) btnPipeline.disabled = false;
    }
  }

  $("btn-panic-header")?.addEventListener("click", () => runPanicStop());
  $("btn-full-stop")?.addEventListener("click", () => runFullStop());
  $("btn-restart-cursor-banner")?.addEventListener("click", () => runCpuRelief("cpu_restart_cursor"));
  $("btn-restart-cursor")?.addEventListener("click", () => runCpuRelief("cpu_restart_cursor"));
  $("btn-pipeline")?.addEventListener("click", () => load("pipeline"));
  $("btn-heal")?.addEventListener("click", () => load("heal"));
  $("btn-rescan")?.addEventListener("click", () => load("scan"));
  $("btn-firewall")?.addEventListener("click", () => {
    window.open("x-apple.systempreferences:com.apple.Network-Settings.extension?Firewall", "_self");
  });
  $("btn-refresh")?.addEventListener("click", () => load("report"));
  $("btn-export")?.addEventListener("click", () => {
    if (!lastReport) return;
    const blob = new Blob([JSON.stringify(lastReport, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `mac-heartbeat-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  });

  $("tab-rhythm-btn")?.addEventListener("click", () => setActiveTab("rhythm"));
  $("tab-ram-truth-btn")?.addEventListener("click", () => setActiveTab("ram"));
  $("tab-cooldown-btn")?.addEventListener("click", () => setActiveTab("cooldown"));
  $("tab-settings-btn")?.addEventListener("click", () => setActiveTab("settings"));
  $("panel-more")?.addEventListener("toggle", (ev) => {
    if (ev.target.open && lastReport) {
      paintSettings({
        settings: lastReport.settings,
        settings_schema: lastReport.settings_schema,
        auto_guard_explainer: lastReport.auto_guard_explainer,
      });
    }
  });
  $("btn-settings-save")?.addEventListener("click", () => saveSettings());
  $("btn-settings-reset")?.addEventListener("click", () => resetSettings());
  $("btn-ram-purge")?.addEventListener("click", () => runRamPurge());
  $("btn-cooldown-ram-purge")?.addEventListener("click", () => runRamPurge());
  $("btn-ram-refresh")?.addEventListener("click", () => refreshRamTruth());
  document.querySelectorAll("[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const act = btn.getAttribute("data-action");
      if (act === "emergency_stop") runPanicStop();
      else runCpuRelief(act);
    });
  });
  $("btn-panic-strip")?.addEventListener("click", () => runPanicStop());
  $("btn-log-shield-relieve")?.addEventListener("click", () => runLogShieldAction("truncate_runaway_logs"));
  $("btn-log-shield-relieve-panel")?.addEventListener("click", () => runLogShieldAction("truncate_runaway_logs"));
  $("btn-log-shield-kill-readers")?.addEventListener("click", () => runLogShieldAction("kill_stuck_log_readers"));

  pingHeart();
  scheduleLivePoll();
  setInterval(pingHeart, 15000);
  setInterval(silentRefresh, FULL_POLL_MS);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible" && Date.now() - lastLiveTickMs > LIVE_MIN_GAP_MS) {
      tickLive();
    }
    if (document.visibilityState === "visible") {
      silentRefresh();
    }
  });
  load("report").then(() => {
    if (lastReport && lastReport.machine_pressure && rhythmPanelVisible()) {
      const wired = lastReport.wired || {};
      renderPressure(lastReport.machine_pressure, (lastReport.founder_narrative || {}).pressure_line, {
        ageSec: wired.pressure_age_sec ?? wired.live_age_sec,
        liveStatus: (lastReport.live && lastReport.live.status) || "LIVE",
        pulseSec: 8,
      });
    }
  });
})();
