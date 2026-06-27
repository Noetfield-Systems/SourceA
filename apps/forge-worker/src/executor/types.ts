export interface ExecutionResult {
  ok: boolean;
  provider: string;
  model?: string;
  text?: string;
  error?: string;
  usage?: Record<string, unknown>;
  fallback_from?: string;
}
