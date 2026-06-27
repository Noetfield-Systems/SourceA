/**
 * Proof Sandbox — GTM 5-field intake (output + receipt promise).
 */
(function () {
  "use strict";

  const CONTACT = "hello@sourcea.app";

  function $(sel) {
    return document.querySelector(sel);
  }

  function showError(msg) {
    const err = $("#sa-sandbox-error");
    if (!err) return;
    err.textContent = msg;
    err.classList.remove("sa-start-hidden");
  }

  function clearError() {
    const err = $("#sa-sandbox-error");
    if (!err) return;
    err.textContent = "";
    err.classList.add("sa-start-hidden");
  }

  function showDone() {
    const formWrap = $("#sa-sandbox-form-wrap");
    const done = $("#sa-sandbox-done");
    const hero = $("#sa-sandbox-hero");
    if (formWrap) formWrap.classList.add("sa-start-hidden");
    if (hero) hero.classList.add("sa-start-hidden");
    if (done) done.classList.remove("sa-start-hidden");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function readForm(form) {
    const fd = new FormData(form);
    const job = String(fd.get("job") || "").trim();
    const inputs = String(fd.get("inputs") || "").trim();
    const output = String(fd.get("output") || "").trim();
    const never_rules = String(fd.get("never_rules") || "").trim();
    const where_pays = String(fd.get("where_pays") || "").trim();
    const email = String(fd.get("email") || "").trim().toLowerCase();
    const errors = [];
    if (!job) errors.push("job_required");
    if (!inputs) errors.push("inputs_required");
    if (!output) errors.push("output_required");
    if (!never_rules) errors.push("never_rules_required");
    if (!where_pays) errors.push("where_pays_required");
    if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) errors.push("email_invalid");
    return {
      errors: errors,
      payload: { job, inputs, output, never_rules, where_pays, email },
    };
  }

  function mailtoBody(payload) {
    return [
      "Proof Sandbox intake",
      "",
      "1. Job: " + payload.job,
      "2. Inputs: " + payload.inputs,
      "3. Output: " + payload.output,
      "4. Never-rules: " + payload.never_rules,
      "5. Where / who pays: " + payload.where_pays,
      "",
      "Contact: " + payload.email,
    ].join("\n");
  }

  async function onSubmit(e) {
    e.preventDefault();
    clearError();
    const form = e.target;
    const btn = $("#sa-sandbox-submit");
    const row = readForm(form);
    if (row.errors.length) {
      showError("Please complete all five fields and a valid email.");
      return;
    }
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Sending…";
    }
    const subject = encodeURIComponent("Proof Sandbox — " + row.payload.job.slice(0, 60));
    const body = encodeURIComponent(mailtoBody(row.payload));
    window.location.href = "mailto:" + CONTACT + "?subject=" + subject + "&body=" + body;
    showDone();
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Submit job →";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    const form = $("#sa-sandbox-intake-form");
    if (form) form.addEventListener("submit", onSubmit);
  });
})();
