/** Cross-venture auth types — SSOT: data/cross-domain-auth-surfaces-v1.json */
export type Venture = "sourcea" | "noetfield" | "trustfield";

export type IdentityRole = "member" | "partner" | "admin" | "service";

export interface IdentityProfile {
  id: string;
  venture: Venture;
  role: IdentityRole;
  display_name?: string | null;
}

export interface AuthEnv {
  supabaseUrl: string;
  supabaseAnonKey: string;
}

export interface GatedRouteOptions {
  /** Paths that require a valid JWT (Tier 2) */
  protectedPrefixes: string[];
  signInPath?: string;
}
