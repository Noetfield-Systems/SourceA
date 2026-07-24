import { hashObject } from "./hash.ts";
import { compileNextAction, governorCommit } from "./governor.ts";
import {
  runCriticPod,
  runMemorySteward,
  runPlannerPod,
  runSgPod,
} from "./pods.ts";
import { createRunwayGoalKernelRouter, independentVerifyLive, type RunwayRouter } from "./runway.ts";
import type { CanonicalStore } from "./store.ts";
import { commitExecutiveRunToSupabase, type SupabaseCanonicalConfig } from "./supabase.ts";
import type { EventEnvelope, ExecutiveRun, Terminal } from "./types.ts";

const TERMINALS: ReadonlySet<string> = new Set([
  "ACCEPTED",
  "BOUNDED_FAILURE",
  "INCIDENT",
  "DEFERRED_BY_POLICY",
  "FOUNDER_DECISION_REQUIRED",
]);

export function isTerminal(status: string): status is Terminal {
  return TERMINALS.has(status);
}

function audit(run: ExecutiveRun, kind: string, detail: Record<string, unknown> = {}): void {
  run.audit.push({ at: new Date().toISOString(), kind, detail });
}

function sealEvent(partial: Omit<EventEnvelope, "payload_hash"> & { payload_hash?: string }): EventEnvelope {
  const { payload_hash: _ph, ...rest } = partial as EventEnvelope;
  return { ...rest, payload_hash: hashObject(rest.payload) };
}

export interface MeshPipelineOptions {
  store: CanonicalStore;
  org?: string;
  runwayRouter?: RunwayRouter;
  producerModelId?: string;
  /** When true, treat execution admit failure as INCIDENT */
  failClosed?: boolean;
  /** Live Goal API base for independent GET verify */
  runwayBaseUrl?: string;
  /** When set, ACCEPTED/terminal runs are written to portfolio-spine */
  supabase?: SupabaseCanonicalConfig;
}

export class ExecutiveMeshPipeline {
  private store: CanonicalStore;
  private org: string;
  private runway: RunwayRouter;
  private producerModelId: string;
  private failClosed: boolean;
  private runwayBaseUrl: string;
  private supabase: SupabaseCanonicalConfig | null;

  constructor(opts: MeshPipelineOptions) {
    this.store = opts.store;
    this.org = opts.org ?? "sourcea";
    this.runway = opts.runwayRouter ?? createRunwayGoalKernelRouter({ simulate: true });
    this.producerModelId = opts.producerModelId ?? "planner.L0.deterministic";
    this.failClosed = opts.failClosed ?? true;
    this.runwayBaseUrl = opts.runwayBaseUrl ?? process.env.RUNWAY_GOAL_BASE_URL ?? "";
    this.supabase = opts.supabase ?? null;
  }

  /** Idempotent ingest + full vertical slice for webpage repair. */
  async ingest(raw: Omit<EventEnvelope, "payload_hash" | "canonical_state_version"> & {
    payload_hash?: string;
    canonical_state_version?: number;
  }): Promise<ExecutiveRun> {
    const existing = this.store.getRunByIdempotency(this.org, raw.idempotency_key);
    if (existing) {
      return existing;
    }

    const snapshot = this.store.getVersion(this.org);
    const event = sealEvent({
      ...raw,
      canonical_state_version: raw.canonical_state_version ?? snapshot,
    });

    // Stale event relative to current canonical version → reject without mutating forever-active state
    if (event.canonical_state_version < snapshot) {
      const rejected: ExecutiveRun = {
        run_id: `run_stale_${event.event_id}`,
        status: "BOUNDED_FAILURE",
        terminal: "BOUNDED_FAILURE",
        snapshot_version: snapshot,
        correlation_id: event.correlation_id,
        idempotency_key: event.idempotency_key,
        event,
        context_pack: null,
        role_packets: [],
        plan: null,
        decision_id: null,
        decision_hash: null,
        work_packet: null,
        evidence: [],
        commitment_id: null,
        commitment_status: null,
        digest: { stale: true, reason: "STALE_EVENT_VERSION" },
        audit: [],
        stale_rejected: true,
      };
      audit(rejected, "STALE_PACKET_REJECT", { offered: event.canonical_state_version, current: snapshot });
      const commit = this.store.commit(this.org, snapshot, () => rejected);
      if (!commit.ok) {
        // concurrent bump — return bounded failure without ACTIVE_FOREVER
        rejected.status = "BOUNDED_FAILURE";
        rejected.terminal = "BOUNDED_FAILURE";
        return rejected;
      }
      return commit.run;
    }

    const runId = `run_${event.event_id}`;
    let run: ExecutiveRun = {
      run_id: runId,
      status: "RECEIVED",
      terminal: null,
      snapshot_version: snapshot,
      correlation_id: event.correlation_id,
      idempotency_key: event.idempotency_key,
      event,
      context_pack: null,
      role_packets: [],
      plan: null,
      decision_id: null,
      decision_hash: null,
      work_packet: null,
      evidence: [],
      commitment_id: null,
      commitment_status: null,
      digest: null,
      audit: [],
      stale_rejected: false,
    };
    audit(run, "RECEIVED", { event_id: event.event_id });

    run.status = "SNAPSHOT_LOCKED";
    audit(run, "SNAPSHOT_LOCKED", { snapshot_version: snapshot });

    const sg = runSgPod(event, runId, snapshot);
    run.role_packets.push(sg);
    run.status = "ROLE_DELIBERATION";

    if (sg.conclusion !== "RECOMMEND") {
      return this.finalize(run, "DEFERRED_BY_POLICY", { reason: "MISSING_DECISION_CAPACITY" });
    }

    const mem = runMemorySteward(event, runId, snapshot, sg);
    run.role_packets.push(mem.packet);
    run.context_pack = mem.context;
    run.status = "CONTEXT_READY";
    audit(run, "CONTEXT_PACK", { context_hash: mem.context.context_hash });

    const planner = runPlannerPod(event, runId, snapshot, mem.context);
    run.role_packets.push(planner.packet);
    run.plan = planner.plan;

    const critic = runCriticPod(runId, snapshot, planner.plan, planner.packet);
    run.role_packets.push(critic.packet);
    run.plan = critic.plan;
    run.status = "COUNCIL_REVIEW";

    // Reject any role packet with mismatched snapshot (stale packet test)
    for (const p of run.role_packets) {
      if (p.snapshot_version !== snapshot) {
        run.stale_rejected = true;
        return this.finalize(run, "BOUNDED_FAILURE", { reason: "STALE_PACKET" });
      }
    }

    const gov = governorCommit(run, run.role_packets, run.plan, snapshot);
    run.decision_id = gov.decision_id;
    run.decision_hash = gov.decision_hash;
    run.status = "GOVERNOR_DECIDED";
    audit(run, "GOVERNOR", { verdict: gov.verdict, reasons: gov.reason_codes });

    if (gov.verdict !== "GREEN") {
      return this.finalize(run, "INCIDENT", { reason: "GOVERNOR_RED", codes: gov.reason_codes });
    }

    const commitmentId = `cmt_${runId}`;
    run.commitment_id = commitmentId;
    run.commitment_status = "OPEN";
    run.work_packet = compileNextAction(runId, gov.decision_id, commitmentId, event.payload, run.plan!);
    run.status = "ACTION_COMPILED";
    audit(run, "WORK_PACKET", {
      action_id: run.work_packet.action_id,
      max_fanout: run.work_packet.budget.max_fanout,
      executor: run.work_packet.executor_class,
    });

    if (run.work_packet.budget.max_fanout !== 0) {
      return this.finalize(run, "INCIDENT", { reason: "ILLEGAL_FANOUT" });
    }

    run.status = "EXECUTING";
    const admit = await this.runway(run.work_packet);
    audit(run, "RUNWAY_ADMIT", admit as unknown as Record<string, unknown>);

    if (!admit.admitted) {
      if (this.failClosed) {
        return this.finalize(run, "INCIDENT", { reason: "EXECUTOR_REJECT", detail: admit.detail });
      }
      return this.finalize(run, "BOUNDED_FAILURE", { reason: "EXECUTOR_REJECT", detail: admit.detail });
    }

    run.status = "VERIFYING";
    const evidence = await independentVerifyLive(run.work_packet, admit, this.producerModelId, {
      baseUrl: this.runwayBaseUrl,
    });
    run.evidence.push({
      evidence_id: evidence.evidence_id,
      kind: "independent_verify",
      valid: evidence.valid,
      detail: evidence.detail,
    });
    audit(run, "VERIFY", evidence as unknown as Record<string, unknown>);

    if (!evidence.valid) {
      return this.finalize(run, "INCIDENT", { reason: "VERIFY_FAIL", detail: evidence.detail });
    }

    // Commitment closes only after EvidenceReceipt
    run.commitment_status = "CLOSED";
    return this.finalize(run, "ACCEPTED", {
      decision_id: run.decision_id,
      work_packet: run.work_packet.action_id,
      evidence_id: evidence.evidence_id,
      goal_ref: admit.goal_ref,
      goal_status: evidence.goal_status ?? null,
      runway_live: Boolean(this.runwayBaseUrl) && !String(admit.goal_ref).startsWith("sim://"),
    });
  }

  /** Explicit stale packet rejection helper for tests / DO. */
  rejectStalePacket(offeredVersion: number, packetRole: string): ExecutiveRun {
    const snapshot = this.store.getVersion(this.org);
    const run: ExecutiveRun = {
      run_id: `run_stale_packet_${packetRole}_${Date.now()}`,
      status: "BOUNDED_FAILURE",
      terminal: "BOUNDED_FAILURE",
      snapshot_version: snapshot,
      correlation_id: "stale",
      idempotency_key: `stale_${packetRole}_${offeredVersion}_${snapshot}`,
      event: sealEvent({
        event_id: `evt_stale_${packetRole}`,
        event_type: "mesh.stale_packet",
        schema_version: "executive_mesh.v1",
        organization_id: this.org,
        correlation_id: "stale",
        causation_id: null,
        idempotency_key: `stale_${packetRole}_${offeredVersion}_${snapshot}`,
        canonical_state_version: offeredVersion,
        producer: "test",
        produced_at: new Date().toISOString(),
        payload: { role: packetRole },
      }),
      context_pack: null,
      role_packets: [],
      plan: null,
      decision_id: null,
      decision_hash: null,
      work_packet: null,
      evidence: [],
      commitment_id: null,
      commitment_status: null,
      digest: { stale_packet: true, offered: offeredVersion, current: snapshot },
      audit: [],
      stale_rejected: true,
    };
    audit(run, "STALE_PACKET_REJECT", { offered: offeredVersion, current: snapshot, role: packetRole });
    const commit = this.store.commit(this.org, snapshot, (v) => {
      run.snapshot_version = v;
      return run;
    });
    return commit.ok ? commit.run : run;
  }

  private async finalize(
    run: ExecutiveRun,
    terminal: Terminal,
    digestExtra: Record<string, unknown>,
  ): Promise<ExecutiveRun> {
    if (!isTerminal(terminal)) {
      throw new Error("ACTIVE_FOREVER_FORBIDDEN");
    }
    run.status = terminal;
    run.terminal = terminal;
    run.digest = {
      run_id: run.run_id,
      terminal,
      snapshot_version: run.snapshot_version,
      decision_id: run.decision_id,
      commitment_status: run.commitment_status,
      role_packet_count: run.role_packets.length,
      context_hash: run.context_pack?.context_hash ?? null,
      work_packet_id: run.work_packet?.action_id ?? null,
      ...digestExtra,
    };
    audit(run, "TERMINAL", { terminal });

    const expected = this.store.getVersion(this.org);
    const commit = this.store.commit(this.org, expected, (nextVersion) => {
      run.snapshot_version = nextVersion;
      if (run.digest) run.digest.committed_version = nextVersion;
      return run;
    });
    if (!commit.ok) {
      run.status = "INCIDENT";
      run.terminal = "INCIDENT";
      run.digest = { ...run.digest, reason: "STALE_VERSION_ON_COMMIT", current: commit.current };
      return run;
    }
    if (this.supabase) {
      const ssot = await commitExecutiveRunToSupabase(this.supabase, commit.run);
      if (commit.run.digest) commit.run.digest.supabase = ssot;
      audit(commit.run, "SUPABASE_CANONICAL", ssot as unknown as Record<string, unknown>);
    }
    return commit.run;
  }

  /** Awaitable canonical SSOT write for live E2E / Worker. */
  async persistCanonical(run: ExecutiveRun): Promise<{ ok: boolean; detail: string }> {
    if (!this.supabase) return { ok: false, detail: "supabase_not_configured" };
    return commitExecutiveRunToSupabase(this.supabase, run);
  }
}

export function buildWebpageRepairEvent(opts: {
  event_id: string;
  target_url: string;
  idempotency_key?: string;
  correlation_id?: string;
  org?: string;
  canonical_state_version?: number;
}): Omit<EventEnvelope, "payload_hash"> {
  return {
    event_id: opts.event_id,
    event_type: "webpage.repair.requested",
    schema_version: "executive_mesh.v1",
    organization_id: opts.org ?? "sourcea",
    correlation_id: opts.correlation_id ?? opts.event_id,
    causation_id: null,
    idempotency_key: opts.idempotency_key ?? opts.event_id,
    canonical_state_version: opts.canonical_state_version ?? 1,
    producer: "executive_mesh_e2e",
    produced_at: new Date().toISOString(),
    payload: {
      task_type: "webpage_repair",
      target_url: opts.target_url,
      goal_id: `goal_${opts.event_id}`,
    },
  };
}
