/** Full Chat Unify cloud proxy — /api/chat-unify-cloud/v1/* → CHAT_UNIFY_UPSTREAM_URL */
function upstreamPath(sub) {
  const clean = (sub || "").replace(/^\//, "");
  if (!clean || clean === "health") return "/health";
  if (clean.startsWith("form")) return `/${clean}`;
  if (clean.startsWith("terminal/")) return `/${clean}`;
  return `/api/${clean}`;
}

function cors(request) {
  const origin = request.headers.get("Origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    Vary: "Origin",
  };
}

function json(request, body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...cors(request), "Content-Type": "application/json" },
  });
}

export async function onRequest(context) {
  const { request, env } = context;
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: cors(request) });
  }
  const url = new URL(request.url);
  const sub = url.pathname.replace(/^\/api\/chat-unify-cloud\/v1\/?/, "") || "";
  const upstreamBase = String(env.CHAT_UNIFY_UPSTREAM_URL || "").replace(/\/$/, "");
  if (!upstreamBase) {
    return json(
      request,
      {
        ok: false,
        mode: "web_shell",
        service: "chat-unify",
        error: "upstream_missing",
        message: "Set CHAT_UNIFY_UPSTREAM_URL on Cloudflare Pages",
      },
      503,
    );
  }
  const target = `${upstreamBase}${upstreamPath(sub)}${url.search}`;
  const init = {
    method: request.method,
    headers: { Accept: request.headers.get("Accept") || "application/json" },
  };
  const ct = request.headers.get("Content-Type");
  if (ct) init.headers["Content-Type"] = ct;
  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = await request.arrayBuffer();
  }
  const resp = await fetch(target, init);
  const headers = new Headers(resp.headers);
  Object.entries(cors(request)).forEach(([k, v]) => headers.set(k, v));
  return new Response(resp.body, { status: resp.status, headers });
}
