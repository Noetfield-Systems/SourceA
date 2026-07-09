import { createBrowserClient as createSupabaseBrowserClient } from "@supabase/ssr";
import type { AuthEnv } from "./types.js";

export function createBrowserClient(env: AuthEnv) {
  return createSupabaseBrowserClient(env.supabaseUrl, env.supabaseAnonKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
      flowType: "pkce",
    },
  });
}
