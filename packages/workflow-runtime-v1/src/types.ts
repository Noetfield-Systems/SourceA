/** Replaceable workflow orchestrator contract (NF-SOURCEA-N8N-ORCHESTRATOR-V1) */

export interface PublishedWorkflow {
  workflow_id: string;
  version: string;
  definition_ref: string;
  published_at: string;
}

export interface RunInput {
  workflow_id: string;
  correlation_id: string;
  idempotency_key: string;
  payload: Record<string, unknown>;
  /** Pinned definition / plan hash when known */
  definition_hash?: string;
}

export interface RunHandle {
  run_id: string;
  workflow_id: string;
  status: "QUEUED" | "RUNNING" | "WAITING" | "SUCCEEDED" | "FAILED" | "CANCELED";
}

export interface RuntimeRun extends RunHandle {
  started_at?: string;
  finished_at?: string;
  terminal?: string | null;
  node_run_refs?: string[];
  error?: string;
}

export interface RuntimeEvent {
  event_type: string;
  payload: Record<string, unknown>;
}

export interface RuntimeTrace {
  run_id: string;
  steps: Array<{
    name: string;
    status: string;
    started_at?: string;
    finished_at?: string;
    envelope_ref?: string;
  }>;
}

export interface WorkflowRuntime {
  publishWorkflow(definitionRef: string): Promise<PublishedWorkflow>;
  startRun(input: RunInput): Promise<RunHandle>;
  getRun(runId: string): Promise<RuntimeRun>;
  pauseRun(runId: string): Promise<void>;
  resumeRun(runId: string, event: RuntimeEvent): Promise<void>;
  cancelRun(runId: string): Promise<void>;
  getTrace(runId: string): Promise<RuntimeTrace>;
}
