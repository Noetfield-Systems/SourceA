/** sourcea.app — Pages static + Chat Unify cloud API proxy */
const PAGES = "https://sourcea-com.pages.dev";
const CHAT_UNIFY_UPSTREAM_DEFAULT = "https://sourcea-chat-unify-production.up.railway.app";
const BRAIN_CHAT_PATH = "/api/brain/chat/v1";
const BRAIN_STATUS_PATH = "/api/brain/status/v1";
const BRAIN_WORKER_BASE = "https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev";
const SITE_PULSE_BASE = "https://sourcea-site-pulse-v1.sina-kazemnezhad-ca.workers.dev";
const AUTO_RUNTIME_BASE = "https://sourcea-cloud-auto-runtime-tick-v1.sina-kazemnezhad-ca.workers.dev";
const ROUTE_MANIFEST_PATH = "/api/sourcea/routes/v1";

/** Clean public paths → Pages canonical paths (200 body, no 302 chain). */
const PAGES_PATH_ALIASES = new Map([
  ["/operating-brain-install", "/sourcea/operating-brain-install"],
  ["/ai-value-governance", "/sourcea/ai-value-governance"],
  ["/enterprise-ai-control-plane", "/sourcea/enterprise-ai-control-plane"],
]);

/** Regional trust domains → canonical sourcea.app contract paths (301, no duplicate homepage). */
const REGIONAL_HOST_DEFAULT = new Map([
  ["sourcea.ca", "https://sourcea.app/ai-value-governance"],
  ["www.sourcea.ca", "https://sourcea.app/ai-value-governance"],
  ["sourcea.uk", "https://sourcea.app/enterprise-ai-control-plane"],
  ["www.sourcea.uk", "https://sourcea.app/enterprise-ai-control-plane"],
]);

function regionalRedirect(incoming) {
  const host = incoming.hostname.toLowerCase();
  const canonical = REGIONAL_HOST_DEFAULT.get(host);
  if (!canonical) return null;
  const path = incoming.pathname.replace(/\/$/, "") || "/";
  if (path === "/" || path === "/ai-value-governance" || path === "/enterprise-ai-control-plane") {
    return Response.redirect(canonical, 301);
  }
  return Response.redirect(canonical, 301);
}

function resolvePagesPath(pathname) {
  if (PAGES_PATH_ALIASES.has(pathname)) return PAGES_PATH_ALIASES.get(pathname);
  if (pathname.startsWith("/attach/")) return `/sourcea/attach/${pathname.slice("/attach/".length)}`;
  if (pathname.startsWith("/loops/")) return `/sourcea/loops/${pathname.slice("/loops/".length)}`;
  if (pathname.startsWith("/case-studies/")) return `/sourcea/case-studies/${pathname.slice("/case-studies/".length)}`;
  return pathname;
}

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
  const headers = corsHeaders(request);
  headers["Cache-Control"] = "no-store";
  return new Response(JSON.stringify(body), { status, headers });
}

function applyApiHeaders(request, headers, extra = {}) {
  Object.entries(corsHeaders(request)).forEach(([k, v]) => {
    if (k.toLowerCase() !== "content-type" || !headers.get("content-type")) headers.set(k, v);
  });
  headers.set("Cache-Control", "no-store");
  for (const [key, value] of Object.entries(extra)) {
    headers.set(key, value);
  }
  return headers;
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
  const headers = applyApiHeaders(request, new Headers(resp.headers), {
    "X-SourceA-Proxy": "sourcea-app-proxy-v1",
    "X-Chat-Unify-Upstream": base,
  });
  return new Response(resp.body, { status: resp.status, headers });
}

async function proxyBrain(request) {
  const incoming = new URL(request.url);
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

  const resp = await fetch(`${BRAIN_WORKER_BASE}${incoming.pathname}${incoming.search}`, init);
  const headers = applyApiHeaders(request, new Headers(resp.headers), {
    "X-SourceA-Proxy": "sourcea-app-proxy-v1",
    "X-SourceA-Brain-Upstream": "sourcea-brain-chat-v1",
  });
  return new Response(resp.body, { status: resp.status, headers });
}

async function proxySitePulse(request) {
  const incoming = new URL(request.url);
  const target = `${SITE_PULSE_BASE}${incoming.pathname}${incoming.search}`;
  const init = {
    method: request.method,
    headers: {
      Accept: request.headers.get("Accept") || "application/json",
    },
  };
  const ct = request.headers.get("Content-Type");
  if (ct) init.headers["Content-Type"] = ct;
  const pulseKey = request.headers.get("X-SourceA-Pulse-Key");
  if (pulseKey) init.headers["X-SourceA-Pulse-Key"] = pulseKey;
  const auth = request.headers.get("Authorization");
  if (auth) init.headers.Authorization = auth;
  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = request.body;
  }

  const resp = await fetch(target, init);
  const headers = applyApiHeaders(request, new Headers(resp.headers), {
    "X-SourceA-Proxy": "sourcea-app-proxy-v1",
    "X-SourceA-Site-Upstream": "sourcea-site-pulse-v1",
  });
  return new Response(resp.body, { status: resp.status, headers });
}

async function proxyAutoRuntime(request, targetPath) {
  if (request.method !== "GET") {
    return jsonResponse(request, { ok: false, error: "method_not_allowed" }, 405);
  }
  const incoming = new URL(request.url);
  const target = `${AUTO_RUNTIME_BASE}${targetPath}${incoming.search}`;
  const resp = await fetch(target, { headers: { Accept: "application/json" } });
  const headers = applyApiHeaders(request, new Headers(resp.headers), {
    "X-SourceA-Proxy": "sourcea-app-proxy-v1",
    "X-SourceA-Auto-Runtime-Upstream": "sourcea-cloud-auto-runtime-tick-v1",
  });
  return new Response(resp.body, { status: resp.status, headers });
}

function routeManifest(request) {
  return jsonResponse(request, {
    ok: true,
    schema: "sourcea-public-api-routes-v1",
    service: "sourcea-app-proxy-v1",
    routes: [
      { path: "/health", upstream: "sourcea-app-proxy-v1", public: true },
      { path: BRAIN_CHAT_PATH, upstream: "sourcea-brain-chat-v1", public: true },
      { path: BRAIN_STATUS_PATH, upstream: "sourcea-brain-chat-v1", public: true },
      { path: "/api/site/pulse/v1", upstream: "sourcea-site-pulse-v1", public: true },
      { path: "/api/site/status/v1", upstream: "sourcea-site-pulse-v1", public: true },
      { path: "/api/site/stats/v1", upstream: "sourcea-site-pulse-v1", public: true },
      { path: "/api/site/event/v1", upstream: "sourcea-site-pulse-v1", public: true },
      { path: "/api/site/feedback/v1", upstream: "sourcea-site-pulse-v1", public: true },
      { path: "/api/site/dashboard/v1", upstream: "sourcea-site-pulse-v1", public: false },
      { path: "/api/cloud-forge-run/health/v1", upstream: "sourcea-cloud-auto-runtime-tick-v1", public: true },
      { path: "/api/cloud-forge-run/status/v1", upstream: "sourcea-cloud-auto-runtime-tick-v1", public: true },
      { path: "/api/cloud-forge-run/queue/v1", upstream: "sourcea-cloud-auto-runtime-tick-v1", public: true },
      { path: "/api/cloud-forge-run/observer/v1", upstream: "sourcea-cloud-auto-runtime-tick-v1", public: true },
      { path: "/api/sourcea/plan-registry/v1", upstream: "sourcea-cloud-auto-runtime-tick-v1", public: true },
      { path: "/api/chat-unify-cloud/v1/*", upstream: "sourcea-chat-unify-production", public: true },
      { path: "/api/chat-unify-demo-cloud/v1/*", upstream: "sourcea-chat-unify-production", public: true },
    ],
  });
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
        brain_status_path: BRAIN_STATUS_PATH,
        site_pulse_prefix: "/api/site/",
        auto_runtime_prefix: "/api/cloud-forge-run/",
      });
    }

    if (pathname === ROUTE_MANIFEST_PATH) {
      return routeManifest(request);
    }

    if (pathname === BRAIN_CHAT_PATH) {
      return proxyBrain(request);
    }
    if (pathname === BRAIN_STATUS_PATH) {
      return proxyBrain(request);
    }

    if (pathname.startsWith("/api/site/")) {
      return proxySitePulse(request);
    }

    if (pathname === "/api/cloud-forge-run/health/v1") {
      return proxyAutoRuntime(request, "/health");
    }
    if (pathname === "/api/cloud-forge-run/status/v1") {
      return proxyAutoRuntime(request, "/status");
    }
    if (pathname === "/api/cloud-forge-run/queue/v1") {
      return proxyAutoRuntime(request, "/queue");
    }
    if (pathname === "/api/cloud-forge-run/observer/v1") {
      return proxyAutoRuntime(request, "/observer-json");
    }
    if (pathname === "/api/sourcea/plan-registry/v1") {
      return proxyAutoRuntime(request, "/plan-registry");
    }

    if (pathname.startsWith("/api/chat-unify-cloud/v1") || pathname.startsWith("/api/chat-unify-demo-cloud/v1")) {
      const prefix = pathname.startsWith("/api/chat-unify-demo-cloud/v1")
        ? "/api/chat-unify-demo-cloud/v1"
        : "/api/chat-unify-cloud/v1";
      return proxyChatUnify(request, env, prefix);
    }

    if (pathname.startsWith("/api/")) {
      return jsonResponse(request, {
        ok: false,
        schema: "sourcea-public-api-error-v1",
        error: "api_route_not_found",
        route_manifest: ROUTE_MANIFEST_PATH,
        path: pathname,
      }, 404);
    }

    if (pathname === "/kernel" || pathname === "/kernel/") {
      return Response.redirect(`${incoming.origin}/sourcea/`, 302);
    }

    const regional = regionalRedirect(incoming);
    if (regional) return regional;

    return proxyPages(request, incoming, resolvePagesPath(pathname));
  },
};

const REDIRECT_STATUSES = new Set([301, 302, 303, 307, 308]);

async function fetchPagesCandidate(request, incoming, candidate, redirectBudget = 4) {
  const target = new URL(candidate + incoming.search, PAGES);
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
  if (REDIRECT_STATUSES.has(response.status) && redirectBudget > 0) {
    const loc = response.headers.get("Location");
    if (loc) {
      const next = new URL(loc, target);
      if (next.origin === new URL(PAGES).origin) {
        return fetchPagesCandidate(request, incoming, `${next.pathname}${next.search}`, redirectBudget - 1);
      }
    }
  }
  return { response, candidate };
}

async function proxyPages(request, incoming, pagesPath) {
  const candidates = [pagesPath];
  if (!pagesPath.endsWith(".html") && !pagesPath.endsWith("/")) {
    candidates.push(`${pagesPath}.html`);
  }

  let lastError = null;
  for (const candidate of candidates) {
    try {
      const { response, candidate: resolvedCandidate } = await fetchPagesCandidate(request, incoming, candidate);
      if (response.status >= 500 && candidates.indexOf(candidate) < candidates.length - 1) {
        continue;
      }
      const out = new Headers(response.headers);
      out.set("X-SourceA-Proxy", "sourcea-app-proxy-v1");
      out.set("X-SourceA-Origin", "pages-green-unified");
      out.set("X-SourceA-Pages-Path", resolvedCandidate);
      out.delete("Location");
      const status = REDIRECT_STATUSES.has(response.status) ? 502 : response.status;
      if (REDIRECT_STATUSES.has(response.status)) {
        return jsonResponse(
          request,
          {
            ok: false,
            schema: "sourcea-public-api-error-v1",
            error: "pages_redirect_not_resolved",
            pages_origin: PAGES,
            path: resolvedCandidate,
          },
          502,
        );
      }
      return new Response(response.body, {
        status,
        statusText: response.statusText,
        headers: out,
      });
    } catch (err) {
      lastError = err;
    }
  }

  return jsonResponse(
    request,
    {
      ok: false,
      schema: "sourcea-public-api-error-v1",
      error: "pages_origin_unavailable",
      pages_origin: PAGES,
      path: pagesPath,
      detail: lastError ? String(lastError) : "unknown",
    },
    502,
  );
}
