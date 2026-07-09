/**
 * Noetfield nerve probe worker — 15-minute cron
 * nf_intake_e2e (Telegram+DB PASS) · greeting · drift · uptime
 * Receipts → Supabase · Telegram on fail
 */
import { writeProbeReceipt, fileImprovement } from "./supabase.js";
import { sendTelegramAlert } from "./telegram.js";
import { handleIntakePost, runAllProbes, probeSsot } from "./probes.js";

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "no-store",
    },
  });
}

export default {
  async scheduled(_event, env, ctx) {
    ctx.waitUntil(runNerveCycle(env));
  },

  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return json({
        ok: true,
        schema: "noetfield-nerve-probe-health-v1",
        service: "noetfield-nerve-probe-v1",
        cron: "*/15 * * * *",
        probes: ["nf_intake_e2e", "greeting", "drift", "uptime"],
        supabase_ready: Boolean(env.SUPABASE_URL && env.SUPABASE_SERVICE_ROLE_KEY),
        telegram_ready: Boolean(
          env.TELEGRAM_BOT_TOKEN && (env.TELEGRAM_ALERT_CHAT_ID || env.TELEGRAM_ALLOWED_CHAT_ID),
        ),
      });
    }
    if (url.pathname === "/api/noetfield/intake/v1" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      const row = await handleIntakePost(env, body, { origin: "cloudflare_worker" });
      return json(row, row.status || (row.ok ? 200 : 422));
    }
    if (url.pathname === "/run" && request.method === "POST") {
      const row = await runNerveCycle(env);
      return json(row, row.ok ? 200 : 422);
    }
    if (url.pathname === "/ssot" && request.method === "GET") {
      return json({ ok: true, ssot: probeSsot() });
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};

async function runNerveCycle(env) {
  const selfUrl = (env.NERVE_PROBE_HEALTH_URL || "https://noetfield-nerve-probe-v1.sina-kazemnezhad-ca.workers.dev").replace(
    /\/health$/,
    "",
  );
  const pack = await runAllProbes(env, { intakeBaseUrl: selfUrl });
  const failLines = [];
  for (const probe of pack.probes) {
    const receipt = await writeProbeReceipt(env, {
      runId: pack.run_id,
      probeId: probe.probe_id,
      verdict: probe.verdict,
      evidence: probe.evidence || {},
      telegramSent: false,
    });
    if (!probe.ok) {
      failLines.push(`<b>${probe.probe_id}</b> FAIL · ${JSON.stringify(probe.evidence || {}).slice(0, 280)}`);
      await fileImprovement(env, {
        finding: `Nerve probe ${probe.probe_id} FAIL — ${JSON.stringify(probe.evidence || {}).slice(0, 400)}`,
        source: "noetfield-nerve-probe-v1",
        expectedRoi: 0.75,
        machineSafe: true,
      });
    }
    probe.receipt_id = receipt.row?.id || null;
    probe.receipt_ok = receipt.ok;
  }
  let telegram = { ok: true, skipped: true };
  if (!pack.ok && failLines.length) {
    telegram = await sendTelegramAlert(
      env,
      `<b>Noetfield nerve FAIL</b> · ${pack.run_id}\n\n${failLines.join("\n\n")}`,
    );
    if (telegram.ok) {
      for (const probe of pack.probes.filter((p) => !p.ok)) {
        await writeProbeReceipt(env, {
          runId: pack.run_id,
          probeId: `${probe.probe_id}_alert`,
          verdict: "FAIL",
          evidence: { alert: true, parent: probe.probe_id },
          telegramSent: true,
        });
      }
    }
  }
  return {
    ok: pack.ok,
    schema: "noetfield-nerve-probe-cycle-v1",
    at: pack.at,
    run_id: pack.run_id,
    probes: pack.probes,
    telegram,
    execution_plane: "cloudflare_cron",
  };
}
