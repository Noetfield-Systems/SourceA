/**
 * SourceA nerve probes — nf_intake_e2e · greeting · drift · uptime
 */
import { supabaseInsert, supabaseSelectOne, supabasePatch } from "./supabase.js";
import { sendIntakeTelegram } from "./telegram.js";

const LOOP_HEALTH =
  "https://sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev/health";
const AUTO_RUNTIME_HEALTH =
  "https://sourcea-cloud-auto-runtime-tick-v1.sina-kazemnezhad-ca.workers.dev/health";

const SSOT = {
  nf_intake_e2e: {
    probe_id: "nf_intake_e2e",
    probe_payload: {
      company: "NF E2E Probe Co",
      contact_name: "Nerve Probe",
      email: "nerve-probe@noetfield.invalid",
      vertical: "diagnostic_sprint",
      message: "Automated nf_intake_e2e probe — safe to delete",
      probe: true,
    },
  },
  greeting_probe: {
    probe_id: "greeting",
    url: "https://www.noetfield.com/",
    needles: ["Noetfield", "Intelligence"],
  },
  uptime_probe: {
    probe_id: "uptime",
    base_url: "https://www.noetfield.com",
    paths: ["/", "/intelligence/intake/", "/governance/", "/copilot/pilot/"],
  },
  drift_probe: {
    probe_id: "drift",
    expected_cron_workers: [
      {
        id: "sourcea-loop-specialist-tick-v1",
        health_url: LOOP_HEALTH,
        cron: "*/15 * * * *",
        require_nerve_probe: true,
      },
      {
        id: "sourcea-cloud-auto-runtime-tick-v1",
        health_url: AUTO_RUNTIME_HEALTH,
        cron: "*/10 * * * *",
      },
    ],
  },
};

export function probeSsot() {
  return SSOT;
}

export async function handleIntakePost(env, body, { origin }) {
  const b = body && typeof body === "object" ? body : {};
  const errors = [];
  const company = String(b.company || "").trim();
  const email = String(b.email || "").trim().toLowerCase();
  if (!company) errors.push("company_required");
  if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) errors.push("email_invalid");
  if (errors.length) {
    return { ok: false, schema: "nf-intake-receipt-v1", errors, status: 400 };
  }
  const probe = Boolean(b.probe);
  const intakeId = probe
    ? `nf-probe-${crypto.randomUUID().replace(/-/g, "").slice(0, 12)}`
    : `nf-${crypto.randomUUID().replace(/-/g, "").slice(0, 12)}`;
  const payload = {
    company,
    contact_name: b.contact_name || null,
    email,
    vertical: b.vertical || null,
    message: b.message || null,
    probe,
  };
  const insert = await supabaseInsert(env, "nf_intake_submissions", {
    intake_id: intakeId,
    channel: origin || "sourcea_loop_specialist",
    probe,
    payload,
    telegram_notified: false,
  });
  if (!insert.ok) {
    return {
      ok: false,
      schema: "nf-intake-receipt-v1",
      intake_id: intakeId,
      error: "supabase_insert_failed",
      detail: insert.error,
      status: 503,
    };
  }
  const tg = await sendIntakeTelegram(env, { intakeId, probe, company, email });
  if (tg.ok && tg.message_id) {
    await supabasePatch(env, "nf_intake_submissions", { intake_id: intakeId }, {
      telegram_notified: true,
      telegram_message_id: String(tg.message_id),
    });
  }
  return {
    ok: true,
    schema: "nf-intake-receipt-v1",
    intake_id: intakeId,
    probe,
    supabase: { ok: true, id: insert.row?.id || null },
    telegram: tg,
    pass_definition: {
      requires: ["post_ok", "supabase_read_back", "telegram_notified"],
    },
    status: 200,
  };
}

export async function runNfIntakeE2e(env, { intakeBaseUrl }) {
  const payload = { ...SSOT.nf_intake_e2e.probe_payload };
  const base = (intakeBaseUrl || "").replace(/\/$/, "");
  let postRow;
  if (base) {
    const resp = await fetch(`${base}/api/noetfield/intake/v1`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    try {
      postRow = await resp.json();
    } catch {
      postRow = { ok: false, error: "invalid_json", status: resp.status };
    }
    postRow.http_status = resp.status;
  } else {
    postRow = await handleIntakePost(env, payload, { origin: "nerve_probe_internal" });
  }
  const intakeId = postRow.intake_id;
  const readBack = intakeId
    ? await supabaseSelectOne(env, "nf_intake_submissions", { intake_id: intakeId })
    : { ok: false, row: null };
  const row = readBack.row || {};
  const checks = {
    post_ok: Boolean(postRow.ok),
    supabase_read_back: Boolean(readBack.ok && row.intake_id === intakeId && row.probe === true),
    telegram_notified: Boolean(row.telegram_notified),
  };
  const pass = Object.values(checks).every(Boolean);
  return {
    probe_id: SSOT.nf_intake_e2e.probe_id,
    ok: pass,
    verdict: pass ? "PASS" : "FAIL",
    checks,
    intake_id: intakeId || null,
    evidence: { post: postRow, read_back: row },
  };
}

export async function runGreetingProbe() {
  const cfg = SSOT.greeting_probe;
  const resp = await fetch(cfg.url, {
    headers: { "User-Agent": "sourcea-nerve-probe/1.0" },
  });
  const text = await resp.text();
  const missing = (cfg.needles || []).filter((n) => !text.includes(n));
  const ok = resp.ok && missing.length === 0;
  return {
    probe_id: cfg.probe_id,
    ok,
    verdict: ok ? "PASS" : "FAIL",
    evidence: { url: cfg.url, status: resp.status, missing_needles: missing },
  };
}

export async function runUptimeProbe() {
  const cfg = SSOT.uptime_probe;
  const base = cfg.base_url.replace(/\/$/, "");
  const checks = [];
  let allOk = true;
  for (const path of cfg.paths || ["/"]) {
    const url = `${base}${path.startsWith("/") ? path : `/${path}`}`;
    let row = { url, ok: false, status: 0 };
    try {
      const resp = await fetch(url, {
        method: "GET",
        headers: { "User-Agent": "sourcea-nerve-probe/1.0" },
      });
      row.status = resp.status;
      row.ok = resp.status >= 200 && resp.status < 400;
      await resp.arrayBuffer();
    } catch (exc) {
      row.error = String(exc).slice(0, 120);
    }
    checks.push(row);
    if (!row.ok) allOk = false;
  }
  return {
    probe_id: cfg.probe_id,
    ok: allOk,
    verdict: allOk ? "PASS" : "FAIL",
    evidence: { checks },
  };
}

export async function runDriftProbe(env) {
  const cfg = SSOT.drift_probe;
  const mismatches = [];
  for (const worker of cfg.expected_cron_workers || []) {
    const url =
      worker.id === "sourcea-loop-specialist-tick-v1"
        ? env.LOOP_SPECIALIST_HEALTH_URL || worker.health_url
        : worker.health_url;
    let health = {};
    try {
      const resp = await fetch(url, { headers: { Accept: "application/json" } });
      health = await resp.json();
    } catch (exc) {
      mismatches.push({ id: worker.id, error: String(exc).slice(0, 120), url });
      continue;
    }
    const liveCron = health.cron || health.brain_verifier_cron || null;
    if (liveCron && worker.cron && liveCron !== worker.cron) {
      mismatches.push({ id: worker.id, expected: worker.cron, live: liveCron, url });
    }
    if (!health.ok) {
      mismatches.push({ id: worker.id, health_ok: health.ok, url });
    }
    if (worker.require_nerve_probe && !health.nerve_probe) {
      mismatches.push({ id: worker.id, nerve_probe: false, url });
    }
  }
  const ok = mismatches.length === 0;
  return {
    probe_id: cfg.probe_id,
    ok,
    verdict: ok ? "PASS" : "FAIL",
    evidence: { mismatches, checked: (cfg.expected_cron_workers || []).length },
  };
}

export async function runAllProbes(env, { intakeBaseUrl } = {}) {
  const runId = `nerve-${new Date().toISOString().replace(/[:.]/g, "").slice(0, 15)}Z`;
  const results = await Promise.all([
    runNfIntakeE2e(env, { intakeBaseUrl }),
    runGreetingProbe(),
    runDriftProbe(env),
    runUptimeProbe(),
  ]);
  return {
    run_id: runId,
    ok: results.every((r) => r.ok),
    at: new Date().toISOString(),
    probes: results,
  };
}
