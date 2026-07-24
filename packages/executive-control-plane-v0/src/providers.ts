/** Deterministic clock + ID providers for tests and production injectability. */

export interface Clock {
  now(): string;
}

export interface IdProvider {
  next(prefix: string): string;
}

export class FixedClock implements Clock {
  private iso: string;
  constructor(iso: string) {
    this.iso = iso;
  }
  now(): string {
    return this.iso;
  }
  set(iso: string): void {
    this.iso = iso;
  }
}

export class SeqIdProvider implements IdProvider {
  private n = 0;
  next(prefix: string): string {
    this.n += 1;
    return `${prefix}_${String(this.n).padStart(4, "0")}`;
  }
  reset(): void {
    this.n = 0;
  }
}

export let clock: Clock = new FixedClock("2026-07-24T06:20:00Z");
export let ids: IdProvider = new SeqIdProvider();

export function setProviders(next: { clock?: Clock; ids?: IdProvider }): void {
  if (next.clock) clock = next.clock;
  if (next.ids) ids = next.ids;
}

export function resetProviders(): void {
  clock = new FixedClock("2026-07-24T06:20:00Z");
  ids = new SeqIdProvider();
}
