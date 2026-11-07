import { WorkflowEntrypoint, type WorkflowEvent, type WorkflowStep } from "cloudflare:workers";

type FollowupEnv = {
  EXECUTIVE_GOVERNOR: DurableObjectNamespace;
  EXECUTIVE_INTERNAL_TOKEN?: string;
};

export interface ExecutiveFollowupInput {
  run_id: string;
  organization_id: string;
}

type RunRecord = {
  run_id: string;
  status: string;
  terminal: string | null;
  digest?: Record<string, unknown> | null;
};

async function reconcile(
  env: FollowupEnv,
  input: ExecutiveFollowupInput,
  flags: { force_timeout?: boolean; force_incident?: boolean } = {},
): Promise<RunRecord> {
  const token = env.EXECUTIVE_INTERNAL_TOKEN;
  if (!token) throw new Error("EXECUTIVE_INTERNAL_TOKEN_MISSING");
  const objectId = env.EXECUTIVE_GOVERNOR.idFromName("governor:" + input.organization_id);
  const stub = env.EXECUTIVE_GOVERNOR.get(objectId);
  const url =
    "https://executive.internal/internal/executive/runs/" +
    encodeURIComponent(input.run_id) +
    "/reconcile";
  const response = await stub.fetch(
    new Request(url, {
      method: "POST",
      headers: {
        authorization: "Bearer " + token,
        "content-type": "application/json",
      },
      body: JSON.stringify(flags),
    }),
  );
  const body = await response.text();
  if (!response.ok) {
    throw new Error("EXECUTIVE_RECONCILE_HTTP_" + response.status + ":" + body.slice(0, 200));
  }
  return JSON.parse(body) as RunRecord;
}

/**
 * Durable completion monitor for the existing Runway Goal Kernel.
 * It observes and reconciles; it never builds, deploys, approves, or executes
 * the Goal itself. The Runway Goal Pursuit Workflow remains the only executor.
 */
export class ExecutiveFollowupWorkflow extends WorkflowEntrypoint<FollowupEnv, ExecutiveFollowupInput> {
  async run(event: WorkflowEvent<ExecutiveFollowupInput>, step: WorkflowStep): Promise<RunRecord> {
    const input = event.payload;
    if (!input.run_id || !input.organization_id) {
      throw new Error("EXECUTIVE_FOLLOWUP_INPUT_INVALID");
    }
    if (!this.env.EXECUTIVE_INTERNAL_TOKEN) {
      throw new Error("EXECUTIVE_INTERNAL_TOKEN_MISSING");
    }

    let consecutiveErrors = 0;
    for (let poll = 0; poll < 160; poll += 1) {
      const attempt = await step.do("reconcile-" + poll, async () => {
        try {
          const row = await reconcile(this.env, input);
          return { ok: true as const, row };
        } catch (error) {
          return { ok: false as const, error: String(error).slice(0, 240) };
        }
      });

      if (!attempt.ok) {
        consecutiveErrors += 1;
        if (consecutiveErrors >= 5) {
          return step.do("reconcile-transport-incident", () =>
            reconcile(this.env, input, { force_incident: true }),
          );
        }
      } else {
        consecutiveErrors = 0;
        if (attempt.row.terminal) return attempt.row;
      }

      await step.sleep("wait-" + poll, "3 minutes");
    }

    return step.do("bounded-followup-timeout", () =>
      reconcile(this.env, input, { force_timeout: true }),
    );
  }
}
