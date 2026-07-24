/** In-memory canonical store with optimistic concurrency (slice-1). */

import { hashObject } from "./hash.ts";
import type { ExecutiveRun } from "./types.ts";

export interface CanonicalStore {
  getVersion(org?: string): number;
  getHash(org?: string): string;
  commit(
    org: string,
    expectedVersion: number,
    mutator: (nextVersion: number) => ExecutiveRun,
  ): { ok: true; run: ExecutiveRun; version: number } | { ok: false; reason: "STALE_VERSION"; current: number };
  getRunByIdempotency(org: string, key: string): ExecutiveRun | null;
  listRuns(): ExecutiveRun[];
}

export class MemoryCanonicalStore implements CanonicalStore {
  private version = 1;
  private hash = "sha256:init";
  private runs = new Map<string, ExecutiveRun>();
  private byIdempotency = new Map<string, string>();

  getVersion(_org = "sourcea"): number {
    return this.version;
  }

  getHash(_org = "sourcea"): string {
    return this.hash;
  }

  getRunByIdempotency(org: string, key: string): ExecutiveRun | null {
    const id = this.byIdempotency.get(`${org}:${key}`);
    return id ? this.runs.get(id) ?? null : null;
  }

  listRuns(): ExecutiveRun[] {
    return [...this.runs.values()];
  }

  commit(
    org: string,
    expectedVersion: number,
    mutator: (nextVersion: number) => ExecutiveRun,
  ): { ok: true; run: ExecutiveRun; version: number } | { ok: false; reason: "STALE_VERSION"; current: number } {
    if (expectedVersion !== this.version) {
      return { ok: false, reason: "STALE_VERSION", current: this.version };
    }
    const nextVersion = this.version + 1;
    const run = mutator(nextVersion);
    this.runs.set(run.run_id, run);
    this.byIdempotency.set(`${org}:${run.idempotency_key}`, run.run_id);
    this.version = nextVersion;
    this.hash = `sha256:${hashObject({ version: nextVersion, run_id: run.run_id, status: run.status })}`;
    return { ok: true, run, version: nextVersion };
  }
}
