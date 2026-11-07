/**
 * sourcea-executive-governor-v1 — production E2E path
 * Durable Object serializes runs; admits via live Runway Goal API; writes Supabase SSOT.
 */

import { DurableObject } from "cloudflare:workers";
import { classifyGoalOutcome } from "./goal-outcome.ts";
import { validateExecutiveTargetUrl } from "./target-policy.ts";
export { ExecutiveFollowupWorkflow } from "./followup-workflow.ts";

export interface Env {
  EXECUTIVE_GOVERNOR: DurableObjectNamespace;
  RUNWAY_GOAL_BASE_URL?: string;
  MESH_SIMULATE?: string;
  RUNWAY_TENANT_ID?: string;
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
  EXECUTIVE_INGRESS_TOKEN?: string;
  EXECUTIVE_ALLOWED_HOSTS?: string;
  EXECUTIVE_INTERNAL_TOKEN?: string;
  EXECUTIVE_FOLLOWUP?: {
    create: (input: { id: string; params: { run_id: string; organization_id: string } }) => Promise<{ id: string }>;
  };
}

type RunRecord = {
  run_id: string;
  status: string;
  terminal: string | null;
  idempotency_key: string;
  snapshot_version: number;
  digest: Record<string, unknown> | null;
  stale_rejected: boolean;
  organization_id?: string;
  correlation_id?: string;
  event_type?: string;
  decision_class?: string;
  goal_ref?: string;
  tenant_id?: string;
  goal_status?: string;
  commitment_status?: "OPEN" | "CLOSED";
  followup_workflow_id?: string | null;
  last_checked_at?: string | null;
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
      const ingressToken = this.env.EXECUTIVE_INGRESS_TOKEN;
      if (!ingressToken) {
        return Response.json({ error: "ingress_not_configured" }, { status: 503 });
      }
      if (request.headers.get("authorization") !== "Bearer " + ingressToken) {
        return Response.json({ error: "unauthorized" }, { status: 401 });
      }
      const body = (await request.json()) as Record<string, unknown>;
      const result = await this.ingest(body);
      return Response.json(result, { status: result.terminal ? 200 : 202 });
    }
    if (request.method === "POST" && url.pathname.startsWith("/internal/executive/runs/") && url.pathname.endsWith("/reconcile")) {
      const token = this.env.EXECUTIVE_INTERNAL_TOKEN;
      if (!token || request.headers.get("authorization") !== "Bearer " + token) {
        return Response.json({ error: "forbidden" }, { status: 403 });
      }
      const match = url.pathname.match(new RegExp("^/internal/executive/runs/([^/]+)/reconcile$"));
      if (!match || !match[1]) return Response.json({ error: "not_found" }, { status: 404 });
      const flags = (await request.json().catch(() => ({}))) as { force_timeout?: boolean; force_incident?: boolean };
      const result = await this.reconcile(decodeURIComponent(match[1]), flags);
      return Response.json(result);
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

    const targetPolicy = validateExecutiveTargetUrl(targetUrl, this.env.EXECUTIVE_ALLOWED_HOSTS);
    if (!targetPolicy.ok) {
      return this.terminal(runId, idempotencyKey, "DEFERRED_BY_POLICY", {
        reason: targetPolicy.reason,
        target_url_host: null,
      });
    }
    const canonicalTargetUrl = targetPolicy.url;
    const contextHash = await hashText(JSON.stringify({ v: this.version, url: canonicalTargetUrl }));
    const decisionHash = await hashText(
      JSON.stringify({ runId, policy: WEBPAGE_REPAIR_POLICY.policy_version }),
    );

    if (this.env.MESH_SIMULATE !== "0") {
      return this.terminal(runId, idempotencyKey, "DEFERRED_BY_POLICY", {
        reason: "SIMULATION_CANNOT_PROVE_COMPLETION",
        decision_hash: decisionHash,
      });
    }

    const base = (this.env.RUNWAY_GOAL_BASE_URL ?? "").replace(/\/$/, "");
    if (!base) {
      return this.terminal(runId, idempotencyKey, "INCIDENT", {
        reason: "RUNWAY_GOAL_BASE_URL_MISSING",
        decision_hash: decisionHash,
      });
    }
    if (!this.env.EXECUTIVE_FOLLOWUP || !this.env.EXECUTIVE_INTERNAL_TOKEN) {
      return this.terminal(runId, idempotencyKey, "INCIDENT", {
        reason: "DURABLE_FOLLOWUP_NOT_CONFIGURED",
        detail: "EXECUTIVE_FOLLOWUP binding and EXECUTIVE_INTERNAL_TOKEN are required",
        decision_hash: decisionHash,
      });
    }

    let goalRef = "";
    let goalStatus = "UNKNOWN";
    try {
      const body = {
        title: "Executive Mesh WEBPAGE_REPAIR",
        objective:
          "Repair webpage " + canonicalTargetUrl + " under WEBPAGE_REPAIR policy " +
          WEBPAGE_REPAIR_POLICY.policy_version + "; acceptance: " + WEBPAGE_REPAIR_POLICY.verify.join(", "),
        project_id: ("mesh_" + eventId).replace(/[^a-zA-Z0-9_]/g, "_").slice(0, 40),
        force_repair_once: true,
        approved_for_runtime: false,
        sleep_seconds: 30,
        priority: 50,
      };
      const createRes = await fetch(base + "/v1/goals", {
        method: "POST",
        headers: { "content-type": "application/json", "x-tenant-id": tenantId },
        body: JSON.stringify(body),
      });
      const createText = await createRes.text();
      if (!createRes.ok) {
        return this.terminal(runId, idempotencyKey, "INCIDENT", {
          reason: "EXECUTOR_REJECT",
          detail: "http_" + createRes.status + ":" + createText.slice(0, 200),
          decision_hash: decisionHash,
        });
      }
      const created = JSON.parse(createText) as Record<string, unknown>;
      goalRef = String(created.goal_id ?? "");
      if (!goalRef) {
        return this.terminal(runId, idempotencyKey, "INCIDENT", {
          reason: "GOAL_ID_MISSING",
          decision_hash: decisionHash,
        });
      }

      const verifyRes = await fetch(base + "/v1/goals/" + encodeURIComponent(goalRef), {
        headers: { "x-tenant-id": tenantId },
      });
      if (!verifyRes.ok) {
        return this.terminal(runId, idempotencyKey, "INCIDENT", {
          reason: "GOAL_ADMISSION_VERIFY_FAILED",
          detail: "live_get_http_" + verifyRes.status,
          goal_ref: goalRef,
        });
      }
      const initialSnapshot = (await verifyRes.json()) as Record<string, unknown>;
      goalStatus = String(initialSnapshot.status ?? "UNKNOWN");
      if (initialSnapshot.goal_id !== goalRef || !Array.isArray(initialSnapshot.acceptance_criteria)) {
        return this.terminal(runId, idempotencyKey, "INCIDENT", {
          reason: "GOAL_ADMISSION_CONTRACT_INVALID",
          goal_ref: goalRef,
        });
      }

      // Persist the open commitment before starting either workflow. The
      // completion monitor starts first; the Runway Goal workflow is the sole
      // executor and keeps its own staging approval gate.
      this.version += 1;
      const pending: RunRecord = {
        run_id: runId,
        status: "AWAITING_EXECUTION",
        terminal: null,
        idempotency_key: idempotencyKey,
        snapshot_version: this.version,
        organization_id: "sourcea",
        correlation_id: eventId,
        event_type: "webpage.repair.requested",
        decision_class: "WEBPAGE_REPAIR",
        goal_ref: goalRef,
        tenant_id: tenantId,
        goal_status: goalStatus,
        commitment_status: "OPEN",
        followup_workflow_id: null,
        last_checked_at: new Date().toISOString(),
        digest: {
          terminal: null,
          context_hash: contextHash,
          decision_hash: decisionHash,
          work_packet_id: "wp_" + runId,
          executor_class: "RUNWAY_GOAL_KERNEL",
          max_fanout: 0,
          goal_ref: goalRef,
          goal_status: goalStatus,
          commitment_status: "OPEN",
          pods: ["SG", "MEMORY_STEWARD", "STRATEGIC_PLANNER", "CRITIC"],
          ecp_wrap: "executive-control-plane-v0",
          admit_detail: "runway_goal_api+live_get",
          runway_live: true,
          followup_status: "MONITOR_STARTING",
        },
        stale_rejected: false,
      };
      await this.persist(pending);

      const pendingSsot = await supabaseUpsert(
        this.env,
        "executive_runs",
        {
          run_id: runId,
          organization_id: "sourcea",
          correlation_id: eventId,
          causation_id: null,
          idempotency_key: idempotencyKey,
          snapshot_version: this.version,
          status: "AWAITING_EXECUTION",
          event_type: "webpage.repair.requested",
          decision_class: "WEBPAGE_REPAIR",
          goal_id: goalRef,
          terminal: null,
          digest_json: pending.digest,
          updated_at: new Date().toISOString(),
        },
        "run_id",
      );
      const versionSsot = await supabaseUpsert(
        this.env,
        "canonical_state_versions",
        {
          organization_id: "sourcea",
          state_version: this.version,
          state_hash: "sha256:" + decisionHash,
          updated_at: new Date().toISOString(),
        },
        "organization_id",
      );
      if (!pendingSsot.ok || !versionSsot.ok) {
        return this.closeRun(pending, "INCIDENT", "INCIDENT", {
          reason: "INITIAL_CANONICAL_SINK_FAILED",
          executive_runs: pendingSsot,
          canonical_state_versions: versionSsot,
        });
      }

      const followupId = "executive-followup-" + runId;
      const followup = await this.env.EXECUTIVE_FOLLOWUP.create({
        id: followupId,
        params: { run_id: runId, organization_id: "sourcea" },
      });
      pending.followup_workflow_id = followup.id;
      pending.digest = {
        ...pending.digest,
        followup_workflow_id: followup.id,
        followup_status: "MONITORING",
      };
      await this.ctx.storage.put("run:" + runId, pending);

      const startRes = await fetch(base + "/v1/goals/" + encodeURIComponent(goalRef) + "/start", {
        method: "POST",
        headers: { "content-type": "application/json", "x-tenant-id": tenantId },
      });
      const startText = await startRes.text();
      if (!startRes.ok) {
        try {
          await fetch(base + "/v1/goals/" + encodeURIComponent(goalRef) + "/kill", {
            method: "POST",
            headers: { "x-tenant-id": tenantId },
          });
        } catch {
          // The Executive run remains an explicit incident if the Goal cannot be stopped.
        }
        return this.closeRun(pending, "INCIDENT", "INCIDENT", {
          reason: "RUNWAY_GOAL_START_FAILED",
          detail: "http_" + startRes.status + ":" + startText.slice(0, 200),
        });
      }
      let started: Record<string, unknown> = {};
      try {
        started = JSON.parse(startText) as Record<string, unknown>;
      } catch {
        // HTTP success is enough to persist the workflow reference by subsequent GET.
      }
      pending.goal_status = String(started.status ?? goalStatus);
      pending.digest = {
        ...pending.digest,
        goal_status: pending.goal_status,
        runway_workflow_instance_id: started.workflow_instance_id ?? null,
        followup_status: "MONITORING",
      };
      await this.ctx.storage.put("run:" + runId, pending);
      return pending;
    } catch (error) {
      if (goalRef) {
        try {
          await fetch(base + "/v1/goals/" + encodeURIComponent(goalRef) + "/kill", {
            method: "POST",
            headers: { "x-tenant-id": tenantId },
          });
        } catch {
          // Preserve the initiating exception; the incident record remains authoritative.
        }
      }
      return this.terminal(runId, idempotencyKey, "INCIDENT", {
        reason: "EXECUTOR_OR_FOLLOWUP_START_FAILED",
        detail: String(error).slice(0, 240),
        goal_ref: goalRef || null,
        decision_hash: decisionHash,
      });
    }
  }

  private async reconcile(
    runId: string,
    flags: { force_timeout?: boolean; force_incident?: boolean },
  ): Promise<RunRecord> {
    const row = await this.ctx.storage.get<RunRecord>("run:" + runId);
    if (!row) throw new Error("EXECUTIVE_RUN_NOT_FOUND");
    if (row.terminal) return row;
    if (row.status !== "AWAITING_EXECUTION" || !row.goal_ref || !row.tenant_id) return row;

    if (flags.force_timeout) {
      return this.closeRun(row, "BOUNDED_FAILURE", "BOUNDED_FAILURE", {
        reason: "FOLLOWUP_WINDOW_EXHAUSTED",
        goal_ref: row.goal_ref,
        goal_status: row.goal_status ?? "UNKNOWN",
      });
    }
    if (flags.force_incident) {
      return this.closeRun(row, "INCIDENT", "INCIDENT", {
        reason: "FOLLOWUP_RECONCILIATION_UNAVAILABLE",
        goal_ref: row.goal_ref,
      });
    }

    const base = (this.env.RUNWAY_GOAL_BASE_URL ?? "").replace(/\/$/, "");
    try {
      const response = await fetch(base + "/v1/goals/" + encodeURIComponent(row.goal_ref), {
        headers: { "x-tenant-id": row.tenant_id },
      });
      if (!response.ok) throw new Error("goal_get_http_" + response.status);
      const snapshot = await response.json();
      const outcome = classifyGoalOutcome(snapshot, row.goal_ref);
      row.goal_status = outcome.goal_status;
      row.last_checked_at = new Date().toISOString();
      row.digest = {
        ...row.digest,
        goal_status: outcome.goal_status,
        followup_last_checked_at: row.last_checked_at,
        followup_error: false,
        followup_outcome: outcome.kind,
        followup_detail: outcome.kind === "PENDING" ? outcome.detail : ("reason" in outcome ? outcome.reason : null),
      };

      if (outcome.kind === "PENDING") {
        await this.ctx.storage.put("run:" + runId, row);
        return row;
      }

      if (outcome.kind === "ACCEPTED_ARTIFACT") {
        const receiptVerify = await fetch(
          base + "/v1/goals/" + encodeURIComponent(row.goal_ref) + "/verify",
          { method: "POST", headers: { "x-tenant-id": row.tenant_id } },
        );
        if (!receiptVerify.ok) {
          return this.closeRun(row, "INCIDENT", "INCIDENT", {
            reason: "RUNWAY_RECEIPT_VERIFY_HTTP_FAILED",
            detail: "http_" + receiptVerify.status,
            receipt_id: outcome.receipt_id,
          });
        }
        const verification = (await receiptVerify.json()) as Record<string, unknown>;
        if (verification.passed !== true || verification.receipt_id !== outcome.receipt_id) {
          return this.closeRun(row, "INCIDENT", "INCIDENT", {
            reason: "RUNWAY_RECEIPT_VERIFY_FAILED",
            receipt_id: outcome.receipt_id,
            verification,
          });
        }
        return this.closeRun(row, "ACCEPTED", "ACCEPTED_ARTIFACT", {
          reason: "RUNWAY_GOAL_ACCEPTED_ARTIFACT",
          goal_ref: row.goal_ref,
          goal_status: outcome.goal_status,
          receipt_id: outcome.receipt_id,
          receipt_hash: outcome.receipt_hash,
          passed_criteria: outcome.passed_criteria,
          independent_verification: verification,
        });
      }

      if (outcome.kind === "FOUNDER_DECISION_REQUIRED") {
        return this.closeRun(row, "FOUNDER_DECISION_REQUIRED", "RED_ZONE_DECISION_PACKET", {
          reason: outcome.reason,
          goal_ref: row.goal_ref,
          goal_status: outcome.goal_status,
        });
      }

      return this.closeRun(row, outcome.kind === "BOUNDED_FAILURE" ? "BOUNDED_FAILURE" : "INCIDENT",
        outcome.kind === "BOUNDED_FAILURE" ? "BOUNDED_FAILURE" : "INCIDENT", {
          reason: outcome.reason,
          goal_ref: row.goal_ref,
          goal_status: outcome.goal_status,
        });
    } catch (error) {
      row.last_checked_at = new Date().toISOString();
      row.digest = {
        ...row.digest,
        followup_last_checked_at: row.last_checked_at,
        followup_error: true,
        followup_error_detail: String(error).slice(0, 240),
      };
      await this.ctx.storage.put("run:" + runId, row);
      return row;
    }
  }

  private async closeRun(
    original: RunRecord,
    status: string,
    terminal: string,
    digestExtra: Record<string, unknown>,
  ): Promise<RunRecord> {
    this.version += 1;
    const closed: RunRecord = {
      ...original,
      status,
      terminal,
      snapshot_version: this.version,
      commitment_status: "CLOSED",
      last_checked_at: new Date().toISOString(),
      digest: {
        ...original.digest,
        ...digestExtra,
        terminal,
        commitment_status: "CLOSED",
        closed_at: new Date().toISOString(),
      },
    };

    const ssot = await supabaseUpsert(
      this.env,
      "executive_runs",
      {
        run_id: closed.run_id,
        organization_id: closed.organization_id ?? "sourcea",
        correlation_id: closed.correlation_id ?? closed.run_id,
        causation_id: null,
        idempotency_key: closed.idempotency_key,
        snapshot_version: this.version,
        status: closed.status,
        event_type: closed.event_type ?? "webpage.repair.requested",
        decision_class: closed.decision_class ?? "WEBPAGE_REPAIR",
        goal_id: closed.goal_ref ?? null,
        terminal: closed.terminal,
        digest_json: closed.digest,
        updated_at: new Date().toISOString(),
      },
      "run_id",
    );
    if (!ssot.ok) {
      closed.status = "INCIDENT";
      closed.terminal = "INCIDENT";
      closed.digest = {
        ...closed.digest,
        attempted_terminal: terminal,
        reason: "EXECUTIVE_CANONICAL_SINK_FAILED",
        executive_runs: ssot,
      };
    } else if (closed.digest) {
      closed.digest.supabase = ssot;
    }

    const versionSink = await supabaseUpsert(
      this.env,
      "canonical_state_versions",
      {
        organization_id: closed.organization_id ?? "sourcea",
        state_version: this.version,
        state_hash: "sha256:" + await hashText(JSON.stringify(closed.digest)),
        updated_at: new Date().toISOString(),
      },
      "organization_id",
    );
    if (!versionSink.ok) {
      closed.status = "INCIDENT";
      closed.terminal = "INCIDENT";
      closed.digest = {
        ...closed.digest,
        attempted_terminal: terminal,
        reason: "CANONICAL_VERSION_SINK_FAILED",
        canonical_state_versions: versionSink,
      };
      await supabaseUpsert(
        this.env,
        "executive_runs",
        {
          run_id: closed.run_id,
          organization_id: closed.organization_id ?? "sourcea",
          correlation_id: closed.correlation_id ?? closed.run_id,
          causation_id: null,
          idempotency_key: closed.idempotency_key,
          snapshot_version: this.version,
          status: "INCIDENT",
          event_type: closed.event_type ?? "webpage.repair.requested",
          decision_class: closed.decision_class ?? "WEBPAGE_REPAIR",
          goal_id: closed.goal_ref ?? null,
          terminal: "INCIDENT",
          digest_json: closed.digest,
          updated_at: new Date().toISOString(),
        },
        "run_id",
      );
    }
    await this.persist(closed);
    return closed;
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
      commitment_status: "CLOSED",
      last_checked_at: new Date().toISOString(),
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
        ingress_configured: Boolean(env.EXECUTIVE_INGRESS_TOKEN),
        followup_configured: Boolean(env.EXECUTIVE_FOLLOWUP && env.EXECUTIVE_INTERNAL_TOKEN),
      });
    }
    const org = url.searchParams.get("org") ?? "sourcea";
    const id = env.EXECUTIVE_GOVERNOR.idFromName(`governor:${org}`);
    const stub = env.EXECUTIVE_GOVERNOR.get(id);
    return stub.fetch(request);
  },
};
