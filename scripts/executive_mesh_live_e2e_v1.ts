/**
 * Full live E2E: mesh → real Runway /v1/goals → live GET verify → Supabase → receipt.
 * Run: node --experimental-strip-types scripts/executive_mesh_live_e2e_v1.ts
 */
import { mkdirSync, writeFileSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import {
  buildWebpageRepairEvent,
  createRunwayGoalKernelRouter,
  ExecutiveMeshPipeline,
  MemoryCanonicalStore,
} from "../packages/executive-mesh-v1/src/index.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");

function loadEnvFile(path: string): void {
  try {
    for (const line of readFileSync(path, "utf8").split("\n")) {
      const t = line.trim();
      if (!t || t.startsWith("#") || !t.includes("=")) continue;
      const i = t.indexOf("=");
      const k = t.slice(0, i).trim();
      let v = t.slice(i + 1).trim();
      if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
        v = v.slice(1, -1);
      }
      if (!process.env[k]) process.env[k] = v;
    }
  } catch {
    /* optional */
  }
}

loadEnvFile(join(homedir(), ".sourcea-secrets/portfolio-spine.env"));

const RUNWAY = "https://noetfield-runway-live-staging.sina-kazemnezhad-ca.workers.dev";
const eventId = `evt_live_e2e_${Date.now()}`;
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!supabaseUrl || !supabaseKey) {
  console.error("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY required");
  process.exit(2);
}

const store = new MemoryCanonicalStore();
const pipeline = new ExecutiveMeshPipeline({
  store,
  runwayRouter: createRunwayGoalKernelRouter({ baseUrl: RUNWAY, simulate: false }),
  runwayBaseUrl: RUNWAY,
  supabase: { url: supabaseUrl, serviceRoleKey: supabaseKey },
});

const run = await pipeline.ingest(
  buildWebpageRepairEvent({
    event_id: eventId,
    target_url: "https://sourcea.app/operating-brain-install",
    canonical_state_version: store.getVersion(),
  }),
);

const ssot = run.digest?.supabase as { ok?: boolean } | undefined;
const receipt = {
  schema: "sourcea.executive_mesh.webpage_repair_live_e2e_receipt.v1",
  decision_id: "NF-EXECUTIVE-MESH-V1",
  generated_at: new Date().toISOString(),
  verdict:
    run.terminal === "ACCEPTED" && run.digest?.runway_live && ssot?.ok ? "PASS" : "FAIL",
  terminal: run.terminal,
  run_id: run.run_id,
  goal_ref: run.digest?.goal_ref ?? null,
  goal_status: run.digest?.goal_status ?? null,
  runway_live: run.digest?.runway_live ?? false,
  supabase: run.digest?.supabase ?? null,
  evidence: run.evidence,
  commitment_status: run.commitment_status,
  max_fanout: run.work_packet?.budget.max_fanout ?? null,
  digest: run.digest,
  checklist: {
    real_runway_admit: Boolean(run.digest?.runway_live),
    live_independent_verify: run.evidence.some(
      (e) => e.valid && String(e.evidence_id).startsWith("ev_live_"),
    ),
    supabase_canonical: Boolean(ssot?.ok),
    no_active_forever: run.status !== "ACTIVE_FOREVER",
    commitment_closed: run.commitment_status === "CLOSED",
  },
};

const outDir = join(ROOT, "receipts/executive");
mkdirSync(outDir, { recursive: true });
const out = join(outDir, `executive-mesh-v1-webpage-repair-live-${eventId}.json`);
writeFileSync(out, JSON.stringify(receipt, null, 2) + "\n");
console.log(JSON.stringify({ path: out, verdict: receipt.verdict, goal_ref: receipt.goal_ref }, null, 2));
process.exit(receipt.verdict === "PASS" ? 0 : 1);
