import { clock, ids } from "./providers.ts";
import type { AuditEvent, CanonicalState } from "./types.ts";

export function pushAudit(state: CanonicalState, kind: string, detail: Record<string, unknown>): void {
  const ev: AuditEvent = {
    schema: "noetfield.executive.audit_event.v0",
    audit_id: ids.next("aud"),
    at: clock.now(),
    kind,
    detail,
  };
  state.audit.push(ev);
  state.updated_at = clock.now();
}
