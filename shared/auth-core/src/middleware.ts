import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import type { AuthEnv, GatedRouteOptions } from "./types.js";

const NO_STORE = "private, no-store, max-age=0";

export function authMiddleware(
  request: NextRequest,
  env: AuthEnv,
  opts: GatedRouteOptions,
) {
  const signIn = opts.signInPath || "/auth/sign-in";
  const path = request.nextUrl.pathname;
  const isProtected = opts.protectedPrefixes.some(
    (prefix) => path === prefix || path.startsWith(`${prefix}/`),
  );
  const isAuthRoute =
    path.startsWith("/auth/") || path.includes("/auth/callback");

  let response = NextResponse.next({ request });

  if (isAuthRoute) {
    response.headers.set("Cache-Control", NO_STORE);
  }

  const supabase = createServerClient(env.supabaseUrl, env.supabaseAnonKey, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
        response = NextResponse.next({ request });
        cookiesToSet.forEach(({ name, value, options }) =>
          response.cookies.set(name, value, options),
        );
      },
    },
  });

  return supabase.auth.getClaims().then(({ data, error }) => {
    const claims = data?.claims;
    if (isProtected && (error || !claims?.sub)) {
      const url = request.nextUrl.clone();
      url.pathname = signIn;
      url.searchParams.set("next", path);
      const redirect = NextResponse.redirect(url);
      redirect.headers.set("Cache-Control", NO_STORE);
      return redirect;
    }
    if (isAuthRoute) {
      response.headers.set("Cache-Control", NO_STORE);
    }
    return response;
  });
}
