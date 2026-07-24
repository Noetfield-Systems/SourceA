/**
 * sourcea-executive-governor-v1
 * Durable Object serializes Executive Mesh runs; wraps ECP v0 via mesh package.
 * Coordinator cache only — canonical SSOT is Supabase (see migration 015).
 */

import { DurableObject } from "cloudflare:workers";

export interface Env {
  EXECUTIVE_GOVERNOR: DurableObjectNamespace;
  RUNWAY_GOAL_BASE_URL?: string;
  MESH_SIMULATE?: string;
}

type RunRecord = {
  run_id: string;
  status: string;
  terminal: string | null;
  idempotency_key: string;
  snapshot_version: number;
  digest: Record<string, unknown> | null;
  stale_rejected: boolean;
};

async function hashText(s: string): Promise<string> {
  const data = new TextEncoder().encode(s);
  const buf = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

const WEBPAGE_REPAIR_POLICY = {
  policy_version: "webpage_repair.v1.live.185ec3865a14",
  limits: { max_files: 5, max_attempts: 2, max_fanout: 0 },
  verify: ["build_passes", "visual_diff_present", "target_issue_absent", "unrelated_pages_unchanged"],
};

export class ExecutiveGovernorDO extends DurableObject<Env> {
  private version = 1;
  private primed = false;

  private async ensureVersion(): Promise<void> {
    if (this.primed) return;
    const stored = await this.ctx.storage.get<number>("canonical_version");
    if (typeof stored === "number" && stored >= 1) this.version = stored;
    this.primed = true;
  }

  async fetch(request: Request): Promise<Response> {
    await this.ensureVersion();
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return Response.json({ ok: true, version: this.version, worker: "sourcea-executive-governor-v1" });
    }
    if (request.method === "POST" && url.pathname === "/v1/executive/runs") {
      const body = (await request.json()) as Record<string, unknown>;
      const result = await this.ingest(body);
      return Response.json(result, { status: result.terminal === "ACCEPTED" ? 200 : 422 });
    }
    if (request.method === "GET" && url.pathname.startsWith("/v1/executive/runs/")) {
      const id = url.pathname.split("/").pop()!;
      const row = await this.ctx.storage.get<RunRecord>(`run:${id}`);
      if (!row) return Response.json({ error: "not_found" }, { status: 404 });
      return Response.json(row);
    }
    return Response.json({ error: "not_found" }, { status: 404 });
  }

  private async ingest(raw: Record<string, unknown>): Promise<RunRecord> {
    const idempotencyKey = String(raw.idempotency_key ?? raw.event_id ?? "");
    const existingId = await this.ctx.storage.get<string>(`idem:${idempotencyKey}`);
    if (existingId) {
      const existing = await this.ctx.storage.get<RunRecord>(`run:${existingId}`);
      if (existing) return existing;
    }

    const offered = Number(raw.canonical_state_version ?? this.version);
    const eventId = String(raw.event_id ?? crypto.randomUUID());
    const targetUrl = String((raw.payload as Record<string, unknown> | undefined)?.target_url ?? raw.target_url ?? "");
    const runId = `run_${eventId}`;

    if (offered < this.version) {
      const rejected: RunRecord = {
        run_id: runId,
        status: "BOUNDED_FAILURE",
        terminal: "BOUNDED_FAILURE",
        idempotency_key: idempotencyKey,
        snapshot_version: this.version,
        digest: { reason: "STALE_EVENT_VERSION", offered, current: this.version },
        stale_rejected: true,
      };
      this.version += 1;
      rejected.snapshot_version = this.version;
      await this.persist(rejected);
      return rejected;
    }

    const taskType = String((raw.payload as Record<string, unknown> | undefined)?.task_type ?? raw.event_type ?? "");
    const isRepair =
      taskType === "webpage_repair" || String(raw.event_type) === "webpage.repair.requested";

    if (!isRepair) {
      const deferred: RunRecord = {
        run_id: runId,
        status: "DEFERRED_BY_POLICY",
        terminal: "DEFERRED_BY_POLICY",
        idempotency_key: idempotencyKey,
        snapshot_version: this.version,
        digest: { reason: "MISSING_DECISION_CAPACITY" },
        stale_rejected: false,
      };
      this.version += 1;
      deferred.snapshot_version = this.version;
      await this.persist(deferred);
      return deferred;
    }

    // L0 pods → Governor → WorkPacket (fanout 0) → simulate/admit Runway
    const contextHash = await hashText(JSON.stringify({ v: this.version, url: targetUrl }));
    const decisionHash = await hashText(JSON.stringify({ runId, policy: WEBPAGE_REPAIR_POLICY.policy_version }));

    const simulate = this.env.MESH_SIMULATE !== "0";
    let admitted = simulate;
    let goalRef = `sim://${runId}`;
    if (!simulate && this.env.RUNWAY_GOAL_BASE_URL) {
      try {
        const res = await fetch(`${this.env.RUNWAY_GOAL_BASE_URL.replace(/\/$/, "")}/v1/goals`, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            goal_id: `goal_${eventId}`,
            decision_class: "WEBPAGE_REPAIR",
            policy_version: WEBPAGE_REPAIR_POLICY.policy_version,
            target_url: targetUrl,
            acceptance_predicates: WEBPAGE_REPAIR_POLICY.verify,
            max_fanout: 0,
            execution_idempotency_key: `exec_${runId}`,
            work_packet_action_id: `wp_${runId}`,
          }),
        });
        admitted = res.ok;
        goalRef = admitted ? `runway://${runId}` : goalRef;
      } catch {
        admitted = false;
      }
    }

    if (!admitted) {
      const incident: RunRecord = {
        run_id: runId,
        status: "INCIDENT",
        terminal: "INCIDENT",
        idempotency_key: idempotencyKey,
        snapshot_version: this.version,
        digest: { reason: "EXECUTOR_REJECT", decision_hash: decisionHash },
        stale_rejected: false,
      };
      this.version += 1;
      incident.snapshot_version = this.version;
      await this.persist(incident);
      return incident;
    }

    const accepted: RunRecord = {
      run_id: runId,
      status: "ACCEPTED",
      terminal: "ACCEPTED",
      idempotency_key: idempotencyKey,
      snapshot_version: this.version,
      digest: {
        terminal: "ACCEPTED",
        context_hash: contextHash,
        decision_hash: decisionHash,
        work_packet_id: `wp_${runId}`,
        executor_class: "RUNWAY_GOAL_KERNEL",
        max_fanout: 0,
        goal_ref: goalRef,
        commitment_status: "CLOSED",
        pods: ["SG", "MEMORY_STEWARD", "STRATEGIC_PLANNER", "CRITIC"],
        ecp_wrap: "executive-control-plane-v0",
      },
      stale_rejected: false,
    };
    this.version += 1;
    accepted.snapshot_version = this.version;
    await this.persist(accepted);
    return accepted;
  }

  private async persist(run: RunRecord): Promise<void> {
    await this.ctx.storage.put(`run:${run.run_id}`, run);
    await this.ctx.storage.put(`idem:${run.idempotency_key}`, run.run_id);
    await this.ctx.storage.put("canonical_version", this.version);
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return Response.json({ ok: true, service: "sourcea-executive-governor-v1" });
    }
    // Single DO id per org — serializes runs
    const org = url.searchParams.get("org") ?? "sourcea";
    const id = env.EXECUTIVE_GOVERNOR.idFromName(`governor:${org}`);
    const stub = env.EXECUTIVE_GOVERNOR.get(id);
    return stub.fetch(request);
  },
};
