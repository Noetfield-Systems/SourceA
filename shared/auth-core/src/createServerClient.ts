import { createServerClient as createSupabaseServerClient } from "@supabase/ssr";
import type { cookies } from "next/headers";
import type { AuthEnv } from "./types.js";

type CookieStore = Awaited<ReturnType<typeof cookies>>;

export function createServerClient(env: AuthEnv, cookieStore: CookieStore) {
  return createSupabaseServerClient(env.supabaseUrl, env.supabaseAnonKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookieStore.set(name, value, options);
          });
        } catch {
          /* set from Server Component — middleware refresh handles tokens */
        }
      },
    },
  });
}
