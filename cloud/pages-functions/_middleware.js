/**
 * Pages middleware — commercial MVP intake + static passthrough.
 */
const INTAKE_PATH = "/api/commercial/mvp-intake/v1";
const BRAIN_CHAT_PATH = "/api/brain/chat/v1";
const BRAIN_WORKER_URL =
  "https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/api/brain/chat/v1";
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const END_SCREEN = "We'll respond in 2 hours with a plan.";
const NOTIFY_TO = "hello@sourcea.app";
const NOTIFY_FROM = "SourceA Intake <onboarding@resend.dev>";

function cors(request) {
  const origin = request.headers.get("Origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    Vary: "Origin",
    "Content-Type": "application/json",
  };
}

function json(request, body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: cors(request) });
}

async function handlePost(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    body = {};
  }
  const b = body && typeof body === "object" ? body : {};
  const errors = [];
  const building = String(b.building || "").trim();
  if (!building) errors.push("building_required");
  const deadline = String(b.deadline || "").trim();
  if (!deadline) errors.push("deadline_required");
  const budget = String(b.budget || "").trim();
  if (!budget) errors.push("budget_required");
  const email = String(b.email || "").trim().toLowerCase();
  if (!email || !EMAIL_RE.test(email)) errors.push("email_invalid");
  if (errors.length) {
    return json(request, { ok: false, schema: "sourcea-mvp-intake-receipt-v1", errors }, 400);
  }
  const intakeId = `mvp-${crypto.randomUUID().replace(/-/g, "").slice(0, 12)}`;
  let notify = { ok: false, skipped: true, reason: "RESEND_API_KEY_missing" };
  if (env.RESEND_API_KEY) {
    try {
      const resp = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: NOTIFY_FROM,
          to: [NOTIFY_TO],
          reply_to: email,
          subject: `[48h MVP] ${building.slice(0, 60)}`,
          text: `Intake ${intakeId}\n${building}\n${email}`,
        }),
      });
      notify = resp.ok
        ? { ok: true, resend_id: (await resp.json()).id }
        : { ok: false, error: "resend_failed", status: resp.status };
    } catch (e) {
      notify = { ok: false, error: String(e).slice(0, 120) };
    }
  }
  return json(request, {
    schema: "sourcea-mvp-intake-receipt-v1",
    ok: true,
    intake_id: intakeId,
    at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
    channel: "cloudflare_pages",
    plane: "commercial",
    business: "48h-mvp-service",
    intake: {
      building,
      building_type: b.building_type || undefined,
      competitor: b.competitor || undefined,
      deadline,
      budget,
      email,
    },
    end_screen: END_SCREEN,
    notify,
  });
}

async function proxyBrainChat(request) {
  const init = {
    method: request.method,
    headers: {
      "Content-Type": request.headers.get("Content-Type") || "application/json",
      Accept: "application/json",
    },
  };
  if (request.method === "POST") {
    init.body = await request.text();
  }
  const resp = await fetch(BRAIN_WORKER_URL, init);
  const text = await resp.text();
  return new Response(text, { status: resp.status, headers: cors(request) });
}

function chatUnifyUpstreamPath(sub) {
  const clean = (sub || "").replace(/^\//, "");
  if (!clean || clean === "health") return "/health";
  if (clean.startsWith("form")) return `/${clean}`;
  if (clean.startsWith("terminal/")) return `/${clean}`;
  return `/api/${clean}`;
}

async function proxyChatUnify(request, env, apiPrefix) {
  const url = new URL(request.url);
  let sub = url.pathname.replace(new RegExp(`^${apiPrefix}/?`), "") || "";
  const upstreamBase = String(env.CHAT_UNIFY_UPSTREAM_URL || "").replace(/\/$/, "");
  if (!upstreamBase) {
    const shell =
      apiPrefix === "/unify-demo/api"
        ? {
            ok: true,
            mode: "demo_shell",
            service: "chat-unify-demo",
            ui_version: "4.9.9",
            message: "Set CHAT_UNIFY_UPSTREAM_URL on Pages",
          }
        : {
            ok: false,
            mode: "web_shell",
            service: "chat-unify",
            error: "upstream_missing",
          };
    return json(request, shell, shell.ok ? 200 : 503);
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
  Object.entries(cors(request)).forEach(([k, v]) => headers.set(k, v));
  return new Response(resp.body, { status: resp.status, headers });
}

export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  if (url.pathname.startsWith("/api/chat-unify-cloud/v1") || url.pathname.startsWith("/api/chat-unify-demo-cloud/v1")) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(request) });
    }
    const prefix = url.pathname.startsWith("/api/chat-unify-demo-cloud/v1")
      ? "/api/chat-unify-demo-cloud/v1"
      : "/api/chat-unify-cloud/v1";
    return proxyChatUnify(request, env, prefix);
  }
  if (url.pathname.startsWith("/unify/api") || url.pathname.startsWith("/unify-demo/api")) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(request) });
    }
    const prefix = url.pathname.startsWith("/unify-demo/api") ? "/unify-demo/api" : "/unify/api";
    return proxyChatUnify(request, env, prefix);
  }
  if (url.pathname === BRAIN_CHAT_PATH) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(request) });
    }
    if (request.method === "GET" || request.method === "POST") {
      return proxyBrainChat(request);
    }
    return json(request, { ok: false, error: "method_not_allowed" }, 405);
  }
  if (url.pathname === INTAKE_PATH) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(request) });
    }
    if (request.method === "POST") {
      return handlePost(request, env);
    }
    return json(request, { ok: false, error: "method_not_allowed" }, 405);
  }
  return context.next();
}
