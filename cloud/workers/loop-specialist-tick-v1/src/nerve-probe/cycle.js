/**
 * Nerve probe cycle — receipts to Supabase · Telegram on fail.
 */
import { writeProbeReceipt, fileImprovement } from "./supabase.js";
import { sendTelegramAlert } from "./telegram.js";
import { runAllProbes } from "./probes.js";

const DEFAULT_INTAKE_BASE =
  "https://sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev";

export async function runNerveProbeCycle(env) {
  const intakeBase = (env.LOOP_SPECIALIST_PUBLIC_URL || DEFAULT_INTAKE_BASE).replace(/\/$/, "");
  const pack = await runAllProbes(env, { intakeBaseUrl: intakeBase });
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
        source: "sourcea-loop-specialist-tick-v1",
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
      `<b>SourceA nerve FAIL</b> · ${pack.run_id}\n\n${failLines.join("\n\n")}`,
    );
  }
  return {
    ok: pack.ok,
    schema: "sourcea-nerve-probe-cycle-v1",
    at: pack.at,
    run_id: pack.run_id,
    probes: pack.probes,
    telegram,
    execution_plane: "cloudflare_cron_loop_specialist",
    nerve_probe_line: pack.ok
      ? `nerve · PASS · ${pack.probes.length}/${pack.probes.length} · ${pack.run_id}`
      : `nerve · FAIL · ${pack.probes.filter((p) => p.ok).length}/${pack.probes.length} · ${pack.run_id}`,
  };
}
