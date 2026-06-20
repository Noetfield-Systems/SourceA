/**
 * Cloud client factories — load from env only (.env.example)
 * No secrets in source. Implement per factory in PHASE_1.
 */

export type CloudClientConfig = {
  supabaseUrl: string;
  supabaseAnonKey: string;
};

export function loadCloudConfigFromEnv(): CloudClientConfig {
  const supabaseUrl = process.env.SUPABASE_URL ?? "";
  const supabaseAnonKey = process.env.SUPABASE_ANON_KEY ?? "";
  if (!supabaseUrl || !supabaseAnonKey) {
    throw new Error("Missing SUPABASE_URL or SUPABASE_ANON_KEY — see .env.example");
  }
  return { supabaseUrl, supabaseAnonKey };
}
