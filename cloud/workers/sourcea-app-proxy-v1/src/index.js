/** sourcea.app — Pages static + Chat Unify cloud API proxy */
const PAGES = "https://sourcea-com.pages.dev";
const CHAT_UNIFY_UPSTREAM_DEFAULT = "https://sourcea-chat-unify-production.up.railway.app";
const BRAIN_CHAT_PATH = "/api/brain/chat/v1";
const BRAIN_WORKER_URL =
  "https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/api/brain/chat/v1";

function upstreamPath(sub) {
  const clean = (sub || "").replace(/^\//, "");
  if (!clean || clean === "health") return "/health";
  if (clean.startsWith("form")) return `/${clean}`;
  if (clean.startsWith("terminal/")) return `/${clean}`;
  return `/api/${clean}`;
}

function corsHeaders(request) {
  const origin = request.headers.get("Origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    Vary: "Origin",
    "Content-Type": "application/json",
  };
}

function jsonResponse(request, body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: corsHeaders(request) });
}

async function proxyChatUnify(request, env, apiPrefix) {
  const incoming = new URL(request.url);
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders(request) });
  }
  const sub = incoming.pathname.replace(new RegExp(`^${apiPrefix}/?`), "") || "";
  const base = String(env.CHAT_UNIFY_UPSTREAM_URL || CHAT_UNIFY_UPSTREAM_DEFAULT).replace(/\/$/, "");
  const target = `${base}${upstreamPath(sub)}${incoming.search}`;
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
  Object.entries(corsHeaders(request)).forEach(([k, v]) => {
    if (k.toLowerCase() !== "content-type" || !headers.get("content-type")) headers.set(k, v);
  });
  headers.set("X-SourceA-Proxy", "sourcea-app-proxy-v1");
  headers.set("X-Chat-Unify-Upstream", base);
  return new Response(resp.body, { status: resp.status, headers });
}

async function proxyBrainChat(request) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders(request) });
  }
  if (request.method !== "GET" && request.method !== "POST") {
    return jsonResponse(request, { ok: false, error: "method_not_allowed" }, 405);
  }

  const init = {
    method: request.method,
    headers: {
      Accept: request.headers.get("Accept") || "application/json",
    },
  };
  const ct = request.headers.get("Content-Type");
  if (ct) init.headers["Content-Type"] = ct;
  if (request.method === "POST") {
    init.body = request.body;
  }

  const resp = await fetch(BRAIN_WORKER_URL, init);
  const headers = new Headers(resp.headers);
  Object.entries(corsHeaders(request)).forEach(([k, v]) => {
    if (k.toLowerCase() !== "content-type" || !headers.get("content-type")) headers.set(k, v);
  });
  headers.set("X-SourceA-Proxy", "sourcea-app-proxy-v1");
  headers.set("X-SourceA-Brain-Upstream", "sourcea-brain-chat-v1");
  return new Response(resp.body, { status: resp.status, headers });
}

export default {
  async fetch(request, env) {
    const incoming = new URL(request.url);
    const { pathname } = incoming;

    if (pathname === "/health") {
      return jsonResponse(request, {
        ok: true,
        service: "sourcea.app",
        plane: "edge",
        proxy: "sourcea-app-proxy-v1",
        pages_origin: PAGES,
        brain_path: BRAIN_CHAT_PATH,
      });
    }

    if (pathname === BRAIN_CHAT_PATH) {
      return proxyBrainChat(request);
    }

    if (pathname.startsWith("/api/chat-unify-cloud/v1") || pathname.startsWith("/api/chat-unify-demo-cloud/v1")) {
      const prefix = pathname.startsWith("/api/chat-unify-demo-cloud/v1")
        ? "/api/chat-unify-demo-cloud/v1"
        : "/api/chat-unify-cloud/v1";
      return proxyChatUnify(request, env, prefix);
    }

    if (pathname === "/kernel" || pathname === "/kernel/") {
      return Response.redirect(`${incoming.origin}/sourcea/`, 302);
    }

    const target = new URL(pathname + incoming.search, PAGES);
    const headers = new Headers(request.headers);
    headers.set("Host", "sourcea-com.pages.dev");
    headers.delete("cf-connecting-ip");
    const proxied = new Request(target.toString(), {
      method: request.method,
      headers,
      body: request.body,
      redirect: "manual",
    });
    const response = await fetch(proxied);
    const out = new Headers(response.headers);
    out.set("X-SourceA-Proxy", "sourcea-app-proxy-v1");
    out.set("X-SourceA-Origin", "pages-green-unified");
    const loc = response.headers.get("Location");
    if (loc) {
      out.set(
        "Location",
        loc
          .replace(/^https?:\/\/sourcea-com\.pages\.dev/i, `https://${incoming.host}`)
          .replace(/^https?:\/\/source-a\.vercel\.app/i, `https://${incoming.host}`),
      );
    }
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: out,
    });
  },
};
