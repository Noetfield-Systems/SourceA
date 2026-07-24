/**
 * sourcea-executive-governor-v1 — production E2E path
 * Durable Object serializes runs; admits via live Runway Goal API; writes Supabase SSOT.
 */

import { DurableObject } from "cloudflare:workers";

export interface Env {
  EXECUTIVE_GOVERNOR: DurableObjectNamespace;
  RUNWAY_GOAL_BASE_URL?: string;
  MESH_SIMULATE?: string;
  RUNWAY_TENANT_ID?: string;
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
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

async function supabaseUpsert(
  env: Env,
  table: string,
  row: Record<string, unknown>,
  onConflict: string,
): Promise<{ ok: boolean; detail: string }> {
  if (!env.SUPABASE_URL || !env.SUPABASE_SERVICE_ROLE_KEY) {
    return { ok: false, detail: "supabase_secrets_missing" };
  }
  const res = await fetch(
    `${env.SUPABASE_URL.replace(/\/$/, "")}/rest/v1/${table}?on_conflict=${onConflict}`,
    {
      method: "POST",
      headers: {
        apikey: env.SUPABASE_SERVICE_ROLE_KEY,
        Authorization: `Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`,
        "content-type": "application/json",
        Prefer: "resolution=merge-duplicates,return=minimal",
      },
      body: JSON.stringify(row),
    },
  );
  const body = await res.text().catch(() => "");
  return { ok: res.ok, detail: res.ok ? "ok" : `${res.status}:${body.slice(0, 200)}` };
}

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
      return Response.json({
        ok: true,
        version: this.version,
        worker: "sourcea-executive-governor-v1",
        mesh_simulate: this.env.MESH_SIMULATE !== "0",
        runway_configured: Boolean(this.env.RUNWAY_GOAL_BASE_URL),
        supabase_configured: Boolean(this.env.SUPABASE_URL && this.env.SUPABASE_SERVICE_ROLE_KEY),
      });
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
    const targetUrl = String(
      (raw.payload as Record<string, unknown> | undefined)?.target_url ?? raw.target_url ?? "",
    );
    const runId = `run_${eventId}`;
    const tenantId = this.env.RUNWAY_TENANT_ID ?? "tenant-runway-staging";

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

    const taskType = String(
      (raw.payload as Record<string, unknown> | undefined)?.task_type ?? raw.event_type ?? "",
    );
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

    const contextHash = await hashText(JSON.stringify({ v: this.version, url: targetUrl }));
    const decisionHash = await hashText(
      JSON.stringify({ runId, policy: WEBPAGE_REPAIR_POLICY.policy_version }),
    );

    const simulate = this.env.MESH_SIMULATE === "1";
    let admitted = false;
    let goalRef = "";
    let goalStatus = "";
    let admitDetail = "";

    if (simulate) {
      admitted = true;
      goalRef = `sim://${runId}`;
      goalStatus = "SIMULATED";
      admitDetail = "mesh_simulate";
    } else {
      const base = (this.env.RUNWAY_GOAL_BASE_URL ?? "").replace(/\/$/, "");
      if (!base) {
        return this.terminal(runId, idempotencyKey, "INCIDENT", {
          reason: "RUNWAY_GOAL_BASE_URL_MISSING",
          decision_hash: decisionHash,
        });
      }
      try {
        const body = {
          title: "Executive Mesh WEBPAGE_REPAIR",
          objective: `Repair webpage ${targetUrl} under WEBPAGE_REPAIR policy ${WEBPAGE_REPAIR_POLICY.policy_version}; acceptance: ${WEBPAGE_REPAIR_POLICY.verify.join(", ")}`,
          project_id: `mesh_${eventId}`.replace(/[^a-zA-Z0-9_]/g, "_").slice(0, 40),
          force_repair_once: true,
          approved_for_runtime: false,
          sleep_seconds: 30,
          priority: 50,
        };
        const res = await fetch(`${base}/v1/goals`, {
          method: "POST",
          headers: { "content-type": "application/json", "x-tenant-id": tenantId },
          body: JSON.stringify(body),
        });
        const text = await res.text();
        if (!res.ok) {
          return this.terminal(runId, idempotencyKey, "INCIDENT", {
            reason: "EXECUTOR_REJECT",
            detail: `http_${res.status}:${text.slice(0, 200)}`,
            decision_hash: decisionHash,
          });
        }
        const json = JSON.parse(text) as Record<string, unknown>;
        goalRef = String(json.goal_id ?? "");
        admitted = Boolean(goalRef);

        // Independent verify: GET goal (producer cannot sole-verify)
        const verifyRes = await fetch(`${base}/v1/goals/${encodeURIComponent(goalRef)}`, {
          headers: { "x-tenant-id": tenantId },
        });
        if (!verifyRes.ok) {
          return this.terminal(runId, idempotencyKey, "INCIDENT", {
            reason: "VERIFY_FAIL",
            detail: `live_get_http_${verifyRes.status}`,
            goal_ref: goalRef,
          });
        }
        const snap = (await verifyRes.json()) as Record<string, unknown>;
        goalStatus = String(snap.status ?? "");
        const hasCriteria =
          Array.isArray(snap.acceptance_criteria) && snap.acceptance_criteria.length > 0;
        if (!hasCriteria || !goalStatus) {
          return this.terminal(runId, idempotencyKey, "INCIDENT", {
            reason: "VERIFY_FAIL",
            detail: "missing_acceptance_criteria_or_status",
            goal_ref: goalRef,
          });
        }
        admitDetail = "runway_goal_api+live_get";
      } catch (e) {
        return this.terminal(runId, idempotencyKey, "INCIDENT", {
          reason: "EXECUTOR_ERROR",
          detail: String(e).slice(0, 200),
        });
      }
    }

    if (!admitted) {
      return this.terminal(runId, idempotencyKey, "INCIDENT", {
        reason: "EXECUTOR_REJECT",
        decision_hash: decisionHash,
      });
    }

    this.version += 1;
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
        goal_status: goalStatus,
        commitment_status: "CLOSED",
        pods: ["SG", "MEMORY_STEWARD", "STRATEGIC_PLANNER", "CRITIC"],
        ecp_wrap: "executive-control-plane-v0",
        admit_detail: admitDetail,
        runway_live: !simulate,
      },
      stale_rejected: false,
    };
    await this.persist(accepted);

    const ssotRun = await supabaseUpsert(
      this.env,
      "executive_runs",
      {
        run_id: runId,
        organization_id: "sourcea",
        correlation_id: eventId,
        causation_id: null,
        idempotency_key: idempotencyKey,
        snapshot_version: this.version,
        status: "ACCEPTED",
        event_type: "webpage.repair.requested",
        decision_class: "WEBPAGE_REPAIR",
        goal_id: goalRef,
        terminal: "ACCEPTED",
        digest_json: accepted.digest,
        updated_at: new Date().toISOString(),
      },
      "run_id",
    );
    await supabaseUpsert(
      this.env,
      "canonical_state_versions",
      {
        organization_id: "sourcea",
        state_version: this.version,
        state_hash: `sha256:${decisionHash}`,
        updated_at: new Date().toISOString(),
      },
      "organization_id",
    );
    if (accepted.digest) accepted.digest.supabase = ssotRun;
    await this.ctx.storage.put(`run:${runId}`, accepted);
    return accepted;
  }

  private async terminal(
    runId: string,
    idempotencyKey: string,
    terminal: "INCIDENT" | "BOUNDED_FAILURE" | "DEFERRED_BY_POLICY",
    digest: Record<string, unknown>,
  ): Promise<RunRecord> {
    this.version += 1;
    const row: RunRecord = {
      run_id: runId,
      status: terminal,
      terminal,
      idempotency_key: idempotencyKey,
      snapshot_version: this.version,
      digest,
      stale_rejected: Boolean(digest.reason === "STALE_EVENT_VERSION"),
    };
    await this.persist(row);
    return row;
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
      return Response.json({
        ok: true,
        service: "sourcea-executive-governor-v1",
        mesh_simulate: env.MESH_SIMULATE === "1",
        runway_configured: Boolean(env.RUNWAY_GOAL_BASE_URL),
        supabase_configured: Boolean(env.SUPABASE_URL && env.SUPABASE_SERVICE_ROLE_KEY),
      });
    }
    const org = url.searchParams.get("org") ?? "sourcea";
    const id = env.EXECUTIVE_GOVERNOR.idFromName(`governor:${org}`);
    const stub = env.EXECUTIVE_GOVERNOR.get(id);
    return stub.fetch(request);
  },
};
