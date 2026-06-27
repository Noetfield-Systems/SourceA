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
        a.href = "mailto:" + config.contact_email;
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
    if (el) el.textContent = msg || "We'll respond in 2 hours with a plan.";
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function readForm(form) {
    const fd = new FormData(form);
    const building = String(fd.get("building") || "").trim();
    const deadline = String(fd.get("deadline") || "").trim();
    const budget = String(fd.get("budget") || "").trim();
    const email = String(fd.get("email") || "").trim().toLowerCase();
    const building_type = String(fd.get("building_type") || "").trim();
    const  = String(fd.get("") || "").trim();
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
        :  || undefined,
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
      if (!r.ok || !data.ok) {
        showError(
          (data.errors || []).join(", ") ||
            "Submit failed — email " + (config.contact_email || CONTACT) + " and we'll still respond in 2 hours."
        );
        if (btn) {
          btn.disabled = false;
          btn.textContent = "Submit →";
        }
        return;
      }
      showDone(data.end_screen || config.end_screen);
    } catch (err) {
      showError("Network error — email " + (config.contact_email || CONTACT) + " and we'll still respond in 2 hours.");
      if (btn) {
        btn.disabled = false;
        btn.textContent = "Submit →";
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
