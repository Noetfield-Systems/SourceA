/** Map /unify/api/* subpath → Chat Unify Railway origin path */
export function chatUnifyUpstreamPath(sub) {
  const clean = (sub || "").replace(/^\//, "");
  if (!clean || clean === "health") return "/health";
  if (clean.startsWith("form")) return `/${clean}`;
  if (clean.startsWith("terminal/")) return `/${clean}`;
  return `/api/${clean}`;
}

export function chatUnifyCors(request) {
  const origin = request.headers.get("Origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    Vary: "Origin",
  };
}

export function chatUnifyJson(request, body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...chatUnifyCors(request), "Content-Type": "application/json" },
  });
}

export async function chatUnifyProxyRequest(context, { apiPrefix, shellHealth, shellError }) {
  const { request, env } = context;
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: chatUnifyCors(request) });
  }

  const url = new URL(request.url);
  const sub = url.pathname.replace(new RegExp(`^${apiPrefix}/?`), "") || "";
  const upstreamBase = (env.CHAT_UNIFY_UPSTREAM_URL || "").replace(/\/$/, "");

  if (!upstreamBase) {
    if (sub === "health" || sub === "") {
      return chatUnifyJson(request, shellHealth, shellHealth.ok === false ? 503 : 200);
    }
    return chatUnifyJson(request, { ...shellError, path: sub }, 503);
  }

  const target = `${upstreamBase}${chatUnifyUpstreamPath(sub)}${url.search}`;
  const init = {
    method: request.method,
    headers: {
      Accept: request.headers.get("Accept") || "application/json",
    },
  };
  const ct = request.headers.get("Content-Type");
  if (ct) init.headers["Content-Type"] = ct;
  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = await request.arrayBuffer();
  }

  const resp = await fetch(target, init);
  const headers = new Headers(resp.headers);
  Object.entries(chatUnifyCors(request)).forEach(([k, v]) => headers.set(k, v));
  return new Response(resp.body, { status: resp.status, headers });
}
