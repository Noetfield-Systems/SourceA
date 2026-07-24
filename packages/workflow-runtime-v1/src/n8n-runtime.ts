import type {
  PublishedWorkflow,
  RunHandle,
  RunInput,
  RuntimeEvent,
  RuntimeRun,
  RuntimeTrace,
  WorkflowRuntime,
} from "./types.ts";

export interface N8nRuntimeConfig {
  baseUrl: string;
  apiKey: string;
  /** Optional webhook secret for child executors */
  webhookSecret?: string;
  fetchImpl?: typeof fetch;
}

/**
 * First WorkflowRuntime implementation — talks to n8n Public API.
 * n8n owns lifecycle; this client never writes Goal/Decision SSOT.
 */
export class N8nWorkflowRuntime implements WorkflowRuntime {
  private base: string;
  private apiKey: string;
  private fetchImpl: typeof fetch;

  constructor(cfg: N8nRuntimeConfig) {
    this.base = cfg.baseUrl.replace(/\/$/, "");
    this.apiKey = cfg.apiKey;
    this.fetchImpl = cfg.fetchImpl ?? fetch;
  }

  private async api(path: string, init: RequestInit = {}): Promise<Response> {
    const headers = new Headers(init.headers);
    headers.set("accept", "application/json");
    headers.set("x-n8n-api-key", this.apiKey);
    if (init.body && !headers.has("content-type")) {
      headers.set("content-type", "application/json");
    }
    return this.fetchImpl(`${this.base}${path}`, { ...init, headers });
  }

  async publishWorkflow(definitionRef: string): Promise<PublishedWorkflow> {
    // definitionRef is a Git path or raw JSON string — import into n8n as inactive until promotion
    let body: unknown;
    if (definitionRef.trim().startsWith("{")) {
      body = JSON.parse(definitionRef);
    } else {
      throw new Error("publishWorkflow expects workflow JSON string in v1 stub (Git load is CI-side)");
    }
    const res = await this.api("/api/v1/workflows", {
      method: "POST",
      body: JSON.stringify(body),
    });
    const text = await res.text();
    if (!res.ok) throw new Error(`n8n publish failed ${res.status}: ${text.slice(0, 200)}`);
    const json = JSON.parse(text) as Record<string, unknown>;
    return {
      workflow_id: String(json.id ?? ""),
      version: String(json.versionId ?? json.updatedAt ?? "1"),
      definition_ref: "n8n:" + String(json.id ?? ""),
      published_at: new Date().toISOString(),
    };
  }

  async startRun(input: RunInput): Promise<RunHandle> {
    const res = await this.api(`/api/v1/workflows/${encodeURIComponent(input.workflow_id)}/activate`, {
      method: "POST",
    }).catch(() => null);
    void res;
    // Prefer webhook/execute endpoint when available
    const exec = await this.api(`/api/v1/workflows/${encodeURIComponent(input.workflow_id)}/run`, {
      method: "POST",
      body: JSON.stringify({
        data: input.payload,
        correlationId: input.correlation_id,
        idempotencyKey: input.idempotency_key,
      }),
    });
    const text = await exec.text();
    if (!exec.ok) {
      // Fallback: treat as queued handle synthesized for offline/dev
      if (exec.status === 404 || exec.status === 405) {
        return {
          run_id: `n8n_run_${input.idempotency_key}`,
          workflow_id: input.workflow_id,
          status: "QUEUED",
        };
      }
      throw new Error(`n8n startRun failed ${exec.status}: ${text.slice(0, 200)}`);
    }
    const json = JSON.parse(text) as Record<string, unknown>;
    return {
      run_id: String(json.executionId ?? json.id ?? `n8n_run_${input.idempotency_key}`),
      workflow_id: input.workflow_id,
      status: "RUNNING",
    };
  }

  async getRun(runId: string): Promise<RuntimeRun> {
    const res = await this.api(`/api/v1/executions/${encodeURIComponent(runId)}`);
    if (res.status === 404) {
      return { run_id: runId, workflow_id: "", status: "FAILED", error: "not_found" };
    }
    const json = (await res.json()) as Record<string, unknown>;
    const finished = Boolean(json.finished);
    const statusRaw = String(json.status ?? "");
    let status: RuntimeRun["status"] = "RUNNING";
    if (finished && (statusRaw === "success" || statusRaw === "success".toUpperCase())) status = "SUCCEEDED";
    else if (finished) status = "FAILED";
    else if (statusRaw === "waiting") status = "WAITING";
    return {
      run_id: runId,
      workflow_id: String((json.workflowId as string) ?? ""),
      status,
      started_at: json.startedAt ? String(json.startedAt) : undefined,
      finished_at: json.stoppedAt ? String(json.stoppedAt) : undefined,
      terminal: status === "SUCCEEDED" ? "ACCEPTED" : status === "FAILED" ? "BOUNDED_FAILURE" : null,
    };
  }

  async pauseRun(_runId: string): Promise<void> {
    // n8n wait nodes pause intrinsically; explicit pause via API when available
  }

  async resumeRun(runId: string, event: RuntimeEvent): Promise<void> {
    const res = await this.api(`/api/v1/executions/${encodeURIComponent(runId)}/retry`, {
      method: "POST",
      body: JSON.stringify(event),
    });
    if (!res.ok && res.status !== 404) {
      const t = await res.text();
      throw new Error(`n8n resume failed ${res.status}: ${t.slice(0, 200)}`);
    }
  }

  async cancelRun(runId: string): Promise<void> {
    const res = await this.api(`/api/v1/executions/${encodeURIComponent(runId)}/stop`, {
      method: "POST",
    });
    if (!res.ok && res.status !== 404) {
      const t = await res.text();
      throw new Error(`n8n cancel failed ${res.status}: ${t.slice(0, 200)}`);
    }
  }

  async getTrace(runId: string): Promise<RuntimeTrace> {
    const res = await this.api(`/api/v1/executions/${encodeURIComponent(runId)}?includeData=true`);
    if (!res.ok) {
      return { run_id: runId, steps: [] };
    }
    const json = (await res.json()) as Record<string, unknown>;
    const data = (json.data as Record<string, unknown> | undefined)?.resultData as
      | { runData?: Record<string, unknown[]> }
      | undefined;
    const steps: RuntimeTrace["steps"] = [];
    const runData = data?.runData ?? {};
    for (const [name, arr] of Object.entries(runData)) {
      const last = Array.isArray(arr) ? arr[arr.length - 1] : undefined;
      const row = (last ?? {}) as Record<string, unknown>;
      steps.push({
        name,
        status: row.error ? "FAILED" : "SUCCEEDED",
        started_at: row.startTime ? String(row.startTime) : undefined,
        envelope_ref: undefined,
      });
    }
    return { run_id: runId, steps };
  }
}
