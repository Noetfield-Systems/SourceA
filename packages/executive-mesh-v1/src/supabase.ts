/** Canonical commit helpers — portfolio-spine Supabase (executive SSOT). */

import type { ExecutiveRun } from "./types.ts";

export interface SupabaseCanonicalConfig {
  url: string;
  serviceRoleKey: string;
  fetchImpl?: typeof fetch;
}

async function rest(
  cfg: SupabaseCanonicalConfig,
  path: string,
  init: RequestInit,
): Promise<{ ok: boolean; status: number; body: string }> {
  const fetchImpl = cfg.fetchImpl ?? fetch;
  const res = await fetchImpl(`${cfg.url.replace(/\/$/, "")}/rest/v1/${path}`, {
    ...init,
    headers: {
      apikey: cfg.serviceRoleKey,
      Authorization: `Bearer ${cfg.serviceRoleKey}`,
      "content-type": "application/json",
      Prefer: "return=minimal",
      ...(init.headers ?? {}),
    },
  });
  const body = await res.text().catch(() => "");
  return { ok: res.ok, status: res.status, body: body.slice(0, 400) };
}

export async function commitExecutiveRunToSupabase(
  cfg: SupabaseCanonicalConfig,
  run: ExecutiveRun,
): Promise<{ ok: boolean; detail: string }> {
  const versionRow = {
    organization_id: run.event.organization_id || "sourcea",
    state_version: run.snapshot_version,
    state_hash: `sha256:${run.decision_hash ?? run.run_id}`,
    updated_at: new Date().toISOString(),
  };
  const upsertVersion = await rest(
    cfg,
    "canonical_state_versions?on_conflict=organization_id",
    {
      method: "POST",
      headers: { Prefer: "resolution=merge-duplicates,return=minimal" },
      body: JSON.stringify(versionRow),
    },
  );
  if (!upsertVersion.ok) {
    return { ok: false, detail: `canonical_state_versions:${upsertVersion.status}:${upsertVersion.body}` };
  }

  const runRow = {
    run_id: run.run_id,
    organization_id: run.event.organization_id || "sourcea",
    correlation_id: run.correlation_id,
    causation_id: run.event.causation_id,
    idempotency_key: run.idempotency_key,
    snapshot_version: run.snapshot_version,
    status: run.status,
    event_type: run.event.event_type,
    decision_class: "WEBPAGE_REPAIR",
    goal_id: run.work_packet?.goal_id ?? null,
    terminal: run.terminal,
    digest_json: run.digest,
    updated_at: new Date().toISOString(),
  };
  const upsertRun = await rest(cfg, "executive_runs?on_conflict=run_id", {
    method: "POST",
    headers: { Prefer: "resolution=merge-duplicates,return=minimal" },
    body: JSON.stringify(runRow),
  });
  if (!upsertRun.ok) {
    return { ok: false, detail: `executive_runs:${upsertRun.status}:${upsertRun.body}` };
  }

  if (run.decision_id && run.decision_hash) {
    await rest(cfg, "mesh_decisions?on_conflict=decision_id", {
      method: "POST",
      headers: { Prefer: "resolution=merge-duplicates,return=minimal" },
      body: JSON.stringify({
        decision_id: run.decision_id,
        executive_run_id: run.run_id,
        zone: run.terminal === "ACCEPTED" ? "GREEN" : "RED",
        status: run.terminal === "ACCEPTED" ? "COMMITTED" : "REJECTED",
        policy_version: "webpage_repair.v1.live.185ec3865a14",
        decision_hash: run.decision_hash,
        body_json: { digest: run.digest },
      }),
    });
  }

  if (run.work_packet) {
    await rest(cfg, "mesh_work_packets?on_conflict=action_id", {
      method: "POST",
      headers: { Prefer: "resolution=merge-duplicates,return=minimal" },
      body: JSON.stringify({
        action_id: run.work_packet.action_id,
        executive_run_id: run.run_id,
        decision_id: run.decision_id,
        executor_class: run.work_packet.executor_class,
        status: run.terminal,
        body_json: run.work_packet,
      }),
    });
  }

  for (const ev of run.evidence) {
    await rest(cfg, "mesh_evidence_receipts?on_conflict=evidence_id", {
      method: "POST",
      headers: { Prefer: "resolution=merge-duplicates,return=minimal" },
      body: JSON.stringify({
        evidence_id: ev.evidence_id,
        executive_run_id: run.run_id,
        work_packet_id: run.work_packet?.action_id ?? "none",
        kind: ev.kind,
        valid: ev.valid,
        detail: ev.detail,
      }),
    });
  }

  if (run.commitment_id) {
    await rest(cfg, "mesh_commitments?on_conflict=commitment_id", {
      method: "POST",
      headers: { Prefer: "resolution=merge-duplicates,return=minimal" },
      body: JSON.stringify({
        commitment_id: run.commitment_id,
        executive_run_id: run.run_id,
        decision_id: run.decision_id,
        required_artifact: "EvidenceReceipt",
        status: run.commitment_status ?? "OPEN",
        updated_at: new Date().toISOString(),
      }),
    });
  }

  return { ok: true, detail: "canonical_commit_ok" };
}
