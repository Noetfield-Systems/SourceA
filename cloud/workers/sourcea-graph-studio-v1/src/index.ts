/**
 * sourcea-graph-studio-v1 — validate / publish / run over Executive Mesh
 * Canvas ≠ Brain: never execute React Flow JSON; only pinned plan_hash.
 */

import { DurableObject } from "cloudflare:workers";
import {
  SLICE1_MANIFESTS,
  WEBPAGE_REPAIR_L0_BLUEPRINT,
  compileBlueprint,
  projectRunGraph,
  stripLayout,
  type BlueprintGraph,
  type CompiledExecutionPlan,
} from "./lib/kernel.ts";

export interface Env {
  GRAPH_STUDIO: DurableObjectNamespace;
  EXECUTIVE_MESH: Fetcher;
  ASSETS: Fetcher;
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
}

type RunRecord = {
  run_id: string;
  plan_hash: string;
  mesh_run_id: string | null;
  status: string;
  terminal: string | null;
  run_graph: ReturnType<typeof projectRunGraph>;
  created_at: string;
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
    `${env.SUPABASE_URL.replace(/\/$/, "")}/rest/v1/${table}?on_conflict=${encodeURIComponent(onConflict)}`,
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

function cors(res: Response): Response {
  const headers = new Headers(res.headers);
  headers.set("access-control-allow-origin", "*");
  headers.set("access-control-allow-methods", "GET,POST,OPTIONS");
  headers.set("access-control-allow-headers", "content-type");
  return new Response(res.body, { status: res.status, headers });
}

export class GraphStudioCoordinatorDO extends DurableObject<Env> {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    if (request.method === "GET" && path === "/health") {
      return Response.json({
        ok: true,
        worker: "sourcea-graph-studio-v1",
        decision_id: "NF-GRAPH-STUDIO-V1",
      });
    }

    if (request.method === "GET" && path === "/v1/registry") {
      return Response.json({
        schema: "graph_studio_registry_v1",
        manifests: SLICE1_MANIFESTS,
        golden_blueprint_id: WEBPAGE_REPAIR_L0_BLUEPRINT.blueprint_id,
      });
    }

    if (request.method === "GET" && path === "/v1/blueprints/golden") {
      return Response.json({
        graph: WEBPAGE_REPAIR_L0_BLUEPRINT,
        layout: {
          blueprint_id: WEBPAGE_REPAIR_L0_BLUEPRINT.blueprint_id,
          version: WEBPAGE_REPAIR_L0_BLUEPRINT.version,
          positions: Object.fromEntries(
            WEBPAGE_REPAIR_L0_BLUEPRINT.nodes.map((n, i) => [
              n.id,
              { x: (i % 5) * 220, y: Math.floor(i / 5) * 140 },
            ]),
          ),
        },
      });
    }

    if (request.method === "POST" && path === "/v1/blueprints/validate") {
      const body = (await request.json()) as { graph?: BlueprintGraph };
      if (!body.graph) return Response.json({ ok: false, error: "graph_required" }, { status: 400 });
      const result = await compileBlueprint(body.graph);
      return Response.json(result, { status: result.ok ? 200 : 422 });
    }

    if (request.method === "POST" && path === "/v1/blueprints/publish") {
      const body = (await request.json()) as {
        graph?: BlueprintGraph;
        layout?: Record<string, unknown>;
        org?: string;
      };
      if (!body.graph) return Response.json({ ok: false, error: "graph_required" }, { status: 400 });
      const semantic = stripLayout(body.graph);
      const result = await compileBlueprint(semantic);
      if (!result.ok) return Response.json(result, { status: 422 });

      const plan: CompiledExecutionPlan = {
        ...result.plan,
        frozen_at: new Date().toISOString(),
      };
      await this.ctx.storage.put(`plan:${plan.plan_hash}`, plan);

      const org = body.org ?? "sourcea";
      const bp = await supabaseUpsert(
        this.env,
        "graph_blueprints",
        {
          org,
          blueprint_id: semantic.blueprint_id,
          version: semantic.version,
          title: semantic.title,
          graph_json: semantic,
          layout_json: body.layout ?? null,
          updated_at: new Date().toISOString(),
        },
        "org,blueprint_id,version",
      );
      const pl = await supabaseUpsert(
        this.env,
        "graph_compiled_plans",
        {
          plan_hash: plan.plan_hash,
          blueprint_id: plan.blueprint_id,
          blueprint_version: plan.blueprint_version,
          plan_json: plan,
          frozen_at: plan.frozen_at,
          immutable: true,
        },
        "plan_hash",
      );

      return Response.json({
        ok: true,
        plan_hash: plan.plan_hash,
        plan,
        supabase: { blueprint: bp, plan: pl },
      });
    }

    if (request.method === "POST" && path === "/v1/runs") {
      const body = (await request.json()) as {
        plan_hash?: string;
        event?: Record<string, unknown>;
        org?: string;
      };
      const planHash = String(body.plan_hash ?? "");
      if (!planHash) return Response.json({ ok: false, error: "plan_hash_required" }, { status: 400 });

      let plan = await this.ctx.storage.get<CompiledExecutionPlan>(`plan:${planHash}`);
      if (!plan && this.env.SUPABASE_URL && this.env.SUPABASE_SERVICE_ROLE_KEY) {
        const res = await fetch(
          `${this.env.SUPABASE_URL.replace(/\/$/, "")}/rest/v1/graph_compiled_plans?plan_hash=eq.${encodeURIComponent(planHash)}&select=plan_json&limit=1`,
          {
            headers: {
              apikey: this.env.SUPABASE_SERVICE_ROLE_KEY,
              Authorization: `Bearer ${this.env.SUPABASE_SERVICE_ROLE_KEY}`,
            },
          },
        );
        if (res.ok) {
          const rows = (await res.json()) as Array<{ plan_json: CompiledExecutionPlan }>;
          if (rows[0]?.plan_json) {
            plan = rows[0].plan_json;
            await this.ctx.storage.put(`plan:${planHash}`, plan);
          }
        }
      }
      if (!plan || plan.plan_hash !== planHash) {
        return Response.json({ ok: false, error: "PLAN_NOT_FOUND" }, { status: 404 });
      }
      if (plan.topology !== "webpage_repair_l0_v1") {
        return Response.json({ ok: false, error: "TOPOLOGY_NOT_SUPPORTED" }, { status: 422 });
      }

      const evt = body.event ?? {};
      const eventId = String(evt.event_id ?? crypto.randomUUID());
      const idem = String(evt.idempotency_key ?? `gs_${eventId}`);
      const targetUrl = String(
        (evt.payload as Record<string, unknown> | undefined)?.target_url ??
          evt.target_url ??
          "https://sourcea.app/operating-brain-install",
      );

      // Omit canonical_state_version — sending a fixed 1 causes false BOUNDED_FAILURE on reused tenant DOs
      const meshBody = {
        event_id: eventId,
        event_type: "webpage.repair.requested",
        schema_version: "1",
        organization_id: body.org ?? "sourcea",
        correlation_id: String(evt.correlation_id ?? eventId),
        causation_id: evt.causation_id ?? null,
        idempotency_key: idem,
        producer: "sourcea-graph-studio-v1",
        produced_at: new Date().toISOString(),
        payload: {
          task_type: "webpage_repair",
          target_url: targetUrl,
          ...(typeof evt.payload === "object" && evt.payload ? (evt.payload as object) : {}),
        },
      };

      const meshRes = await this.env.EXECUTIVE_MESH.fetch(
        "https://executive-mesh/v1/executive/runs",
        {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify(meshBody),
        },
      );
      const meshText = await meshRes.text();
      let meshJson: Record<string, unknown> = {};
      try {
        meshJson = JSON.parse(meshText) as Record<string, unknown>;
      } catch {
        meshJson = { raw: meshText.slice(0, 300) };
      }

      const meshRunId = String(meshJson.run_id ?? meshJson.mesh_run_id ?? "");
      const status = String(meshJson.status ?? (meshRes.ok ? "UNKNOWN" : "BOUNDED_FAILURE"));
      const terminal = (meshJson.terminal as string | null) ?? null;
      const runId = `grun_${eventId}`;
      const runGraph = projectRunGraph(
        plan,
        meshRunId
          ? { run_id: meshRunId, status, terminal }
          : { run_id: "none", status, terminal },
        runId,
      );

      const record: RunRecord = {
        run_id: runId,
        plan_hash: planHash,
        mesh_run_id: meshRunId || null,
        status,
        terminal,
        run_graph: runGraph,
        created_at: new Date().toISOString(),
      };
      await this.ctx.storage.put(`run:${runId}`, record);

      await supabaseUpsert(
        this.env,
        "graph_runs",
        {
          run_id: runId,
          org: body.org ?? "sourcea",
          plan_hash: planHash,
          mesh_run_id: meshRunId || null,
          status,
          terminal,
          run_graph_json: runGraph,
          event_json: meshBody,
          updated_at: new Date().toISOString(),
        },
        "run_id",
      );

      return Response.json({
        ok: meshRes.ok && terminal === "ACCEPTED",
        ...record,
        mesh_http_status: meshRes.ok,
        mesh: meshJson,
      });
    }

    if (request.method === "GET" && path.startsWith("/v1/runs/")) {
      const runId = path.slice("/v1/runs/".length);
      const record = await this.ctx.storage.get<RunRecord>(`run:${runId}`);
      if (!record) return Response.json({ error: "not_found" }, { status: 404 });
      return Response.json(record);
    }

    return Response.json({ error: "not_found" }, { status: 404 });
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method === "OPTIONS") {
      return cors(new Response(null, { status: 204 }));
    }
    const url = new URL(request.url);
    const apiPath =
      url.pathname === "/health" ||
      url.pathname.startsWith("/v1/");
    if (!apiPath) {
      return env.ASSETS.fetch(request);
    }
    const id = env.GRAPH_STUDIO.idFromName("graph-studio-v1");
    const stub = env.GRAPH_STUDIO.get(id);
    const res = await stub.fetch(request);
    return cors(res);
  },
};
