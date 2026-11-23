/**
 * Business A — 48h MVP intake (static form + submit).
 */
(function () {
  "use strict";

  const CONTACT = "hello@sourcea.app";
  let config = {};

  function $(sel) {
    return document.querySelector(sel);
  }

  function apiUrl() {
    const host = window.location.hostname;
    if (host === "127.0.0.1" || host === "localhost") {
      return config.local_dev_api || "http://127.0.0.1:8192/api/commercial/mvp-intake/v1";
    }
    if (config.api_worker_url) {
      return config.api_worker_url;
    }
    return config.api_relative || "/api/commercial/mvp-intake/v1";
  }

  async function loadConfig() {
    try {
      const r = await fetch("/sourcea/data/mvp-intake-config.json", { cache: "no-store" });
      if (r.ok) config = await r.json();
    } catch {
      config = {};
    }
    if (config.contact_email) {
      document.querySelectorAll('a[href^="mailto:hello@"]').forEach(function (a) {
        const href = new URL(a.href);
        a.href = "mailto:" + config.contact_email + href.search;
        if (a.textContent.indexOf("hello@") >= 0) a.textContent = config.contact_email;
      });
    }
  }

  function showError(msg) {
    const err = $("#sa-start-error");
    if (!err) return;
    err.textContent = msg;
    err.classList.remove("sa-start-hidden");
  }

  function clearError() {
    const err = $("#sa-start-error");
    if (!err) return;
    err.textContent = "";
    err.classList.add("sa-start-hidden");
  }

  function showDone(msg) {
    const form = $("#sa-start-form");
    const done = $("#sa-start-done");
    const hero = $("#sa-start-hero");
    if (form) form.classList.add("sa-start-hidden");
    if (hero) hero.classList.add("sa-start-hidden");
    if (done) done.classList.remove("sa-start-hidden");
    const el = $("#sa-start-done-msg");
    if (el) el.textContent = msg || "We will follow up by email.";
    done?.querySelector("h2")?.focus();
  }

  function readForm(form) {
    const fd = new FormData(form);
    const building = String(fd.get("building") || "").trim();
    const deadline = String(fd.get("deadline") || "").trim();
    const budget = String(fd.get("budget") || "").trim();
    const email = String(fd.get("email") || "").trim().toLowerCase();
    const building_type = String(fd.get("building_type") || "").trim();
    const url = String(fd.get("url") || "").trim();
    const errors = [];
    if (!building) errors.push("building_required");
    if (!deadline) errors.push("deadline_required");
    if (!budget) errors.push("budget_required");
    if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) errors.push("email_invalid");
    return {
      errors: errors,
      payload: {
        building: building,
        building_type: building_type || undefined,
        url: url || undefined,
        deadline: deadline,
        budget: budget,
        email: email,
      },
    };
  }

  function bindOptionHighlight() {
    document.querySelectorAll(".sa-start-option input").forEach(function (inp) {
      inp.addEventListener("change", function () {
        const group = inp.closest(".sa-start-options");
        if (!group) return;
        group.querySelectorAll(".sa-start-option").forEach(function (el) {
          el.classList.remove("is-selected");
        });
        const label = inp.closest(".sa-start-option");
        if (label) label.classList.add("is-selected");
      });
    });
  }

  async function onSubmit(e) {
    e.preventDefault();
    clearError();
    const form = e.target;
    const btn = $("#sa-start-submit");
    const row = readForm(form);
    if (row.errors.length) {
      showError("Please fill in building, deadline, budget, and a valid email.");
      return;
    }
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Sending…";
    }
    try {
      const r = await fetch(apiUrl(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(row.payload),
      });
      const data = await r.json();
      const delivered = data.storage?.ok === true || data.notify?.ok === true;
      if (!r.ok || data.ok !== true || !data.intake_id || !delivered) {
        showError("Your brief could not be confirmed. Try again or use Email your brief.");
        return;
      }
      showDone(data.end_screen || config.end_screen);
      const refEl = $("#sa-start-ref-id");
      if (refEl) {
        refEl.textContent = "Confirmation reference: " + data.intake_id;
        refEl.hidden = false;
      }
      window.SourceAPulse?.track("studio_build_brief_received");
    } catch {
      showError("Your brief could not be confirmed. Try again or use Email your brief.");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = "Submit project →";
      }
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    loadConfig();
    bindOptionHighlight();
    const form = $("#sa-mvp-intake-form");
    if (form) form.addEventListener("submit", onSubmit);
  });
})();
