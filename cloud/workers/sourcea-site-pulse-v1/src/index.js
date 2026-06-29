const EVENT_PATH = "/api/site/event/v1";
const FEEDBACK_PATH = "/api/site/feedback/v1";
const STATS_PATH = "/api/site/stats/v1";
const DASHBOARD_PATH = "/api/site/dashboard/v1";
const STATUS_PATH = "/api/site/status/v1";
const HEALTH_PATH = "/health";
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const NOTIFY_TO = "hello@sourcea.app";
const FEEDBACK_TO = "forge@sourcea.app";
const NOTIFY_FROM = "SourceA Site <onboarding@resend.dev>";
const MAX_MSG = 4000;
const MAX_EVENTS_BATCH = 25;
const MAX_FEEDBACK_INBOX = 50;
const ALLOWED_ORIGIN_RE = /^https?:\/\/(?:localhost(?::\d+)?|127\.0\.0\.1(?::\d+)?|(?:www\.)?sourcea\.app|sourcea-com\.pages\.dev)$/;

function cors(request) {
  const origin = request.headers.get("Origin") || "*";
  const allowOrigin = origin === "*" || ALLOWED_ORIGIN_RE.test(origin) ? origin : "https://sourcea.app";
  return {
    "Access-Control-Allow-Origin": allowOrigin,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-SourceA-Pulse-Key",
    Vary: "Origin",
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
  };
}

function json(request, body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: cors(request) });
}

function utcDay(offset = 0) {
  const d = new Date();
  d.setUTCDate(d.getUTCDate() - offset);
  return d.toISOString().slice(0, 10);
}

function founderToken(request) {
  const auth = request.headers.get("Authorization") || "";
  if (auth.startsWith("Bearer ")) return auth.slice(7).trim();
  return (request.headers.get("X-SourceA-Pulse-Key") || "").trim();
}

function founderAuthorized(request, env) {
  const expected = env.FOUNDER_PULSE_KEY;
  if (!expected) return false;
  const token = founderToken(request);
  return token.length > 0 && token === expected;
}

async function bumpStat(env, field, n = 1) {
  if (!env.PULSE_KV) return null;
  const key = `stats:${utcDay()}`;
  let row = {};
  try {
    const raw = await env.PULSE_KV.get(key);
    if (raw) row = JSON.parse(raw);
  } catch {
    row = {};
  }
  row[field] = (Number(row[field]) || 0) + n;
  row.updated_at = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  await env.PULSE_KV.put(key, JSON.stringify(row), { expirationTtl: 60 * 60 * 24 * 90 });
  return row;
}

async function storeFeedback(env, record) {
  if (!env.PULSE_KV) return;
  const id = record.feedback_id;
  await env.PULSE_KV.put(`feedback:${id}`, JSON.stringify(record), { expirationTtl: 60 * 60 * 24 * 365 });
  const listKey = "feedback:index";
  let ids = [];
  try {
    const raw = await env.PULSE_KV.get(listKey);
    if (raw) ids = JSON.parse(raw);
  } catch {
    ids = [];
  }
  ids.unshift(id);
  await env.PULSE_KV.put(listKey, JSON.stringify(ids.slice(0, 500)));
  await bumpStat(env, "feedback_count");
}

async function sendResend(env, { to, subject, text, replyTo }) {
  if (!env.RESEND_API_KEY) {
    return { ok: false, skipped: true, reason: "RESEND_API_KEY_missing" };
  }
  const resp = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: NOTIFY_FROM,
      to: Array.isArray(to) ? to : [to],
      reply_to: replyTo || undefined,
      subject,
      text,
    }),
  });
  if (!resp.ok) {
    return { ok: false, error: "resend_failed", status: resp.status };
  }
  const data = await resp.json();
  return { ok: true, resend_id: data.id };
}

function summarizeStatsRow(row, day) {
  const top_events = [];
  const top_pages = [];
  for (const [k, v] of Object.entries(row || {})) {
    const n = Number(v) || 0;
    if (!n || k === "updated_at") continue;
    if (k.startsWith("event:")) top_events.push({ name: k.slice(6), count: n });
    else if (k.startsWith("page:")) top_pages.push({ path: k.slice(5), count: n });
  }
  top_events.sort((a, b) => b.count - a.count);
  top_pages.sort((a, b) => b.count - a.count);
  return {
    day,
    pageviews: Number(row?.pageviews) || 0,
    feedback_count: Number(row?.feedback_count) || 0,
    top_events: top_events.slice(0, 10),
    top_pages: top_pages.slice(0, 10),
    updated_at: row?.updated_at,
  };
}

async function loadStatsDay(env, day) {
  let row = {};
  if (env.PULSE_KV) {
    try {
      const raw = await env.PULSE_KV.get(`stats:${day}`);
      if (raw) row = JSON.parse(raw);
    } catch {
      /* ignore */
    }
  }
  return summarizeStatsRow(row, day);
}

async function loadStatsRange(env, days = 7) {
  const out = [];
  for (let i = 0; i < days; i += 1) {
    out.push(await loadStatsDay(env, utcDay(i)));
  }
  return out;
}

async function loadFeedbackInbox(env, limit = MAX_FEEDBACK_INBOX) {
  if (!env.PULSE_KV) return [];
  let ids = [];
  try {
    const raw = await env.PULSE_KV.get("feedback:index");
    if (raw) ids = JSON.parse(raw);
  } catch {
    ids = [];
  }
  const items = [];
  for (const id of ids.slice(0, limit)) {
    try {
      const raw = await env.PULSE_KV.get(`feedback:${id}`);
      if (raw) items.push(JSON.parse(raw));
    } catch {
      /* skip */
    }
  }
  return items;
}

async function handleEvent(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    body = {};
  }
  const events = Array.isArray(body.events) ? body.events.slice(0, MAX_EVENTS_BATCH) : [body];
  let accepted = 0;
  for (const ev of events) {
    if (!ev || typeof ev !== "object") continue;
    const name = String(ev.event || ev.name || "unknown").slice(0, 64);
    if (name === "pageview") {
      await bumpStat(env, "pageviews");
      const path = String(ev.path || "").slice(0, 120);
      if (path) {
        const safe = path.replace(/[^a-zA-Z0-9/_-]/g, "_").slice(0, 96);
        await bumpStat(env, `page:${safe}`);
      }
    } else {
      await bumpStat(env, `event:${name}`);
    }
    accepted += 1;
  }
  return json(request, {
    ok: true,
    schema: "sourcea-site-event-receipt-v1",
    accepted,
    at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
  });
}

async function handleFeedback(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    body = {};
  }
  const type = String(body.type || "feedback").slice(0, 32);
  const message = String(body.message || "").trim();
  const page = String(body.page || body.path || "").slice(0, 256);
  const url = String(body.url || "").slice(0, 512);
  const email = String(body.email || "").trim().toLowerCase();
  if (!message || message.length < 4) {
    return json(request, { ok: false, schema: "sourcea-site-feedback-receipt-v1", errors: ["message_required"] }, 400);
  }
  if (message.length > MAX_MSG) {
    return json(request, { ok: false, errors: ["message_too_long"] }, 400);
  }
  if (email && !EMAIL_RE.test(email)) {
    return json(request, { ok: false, errors: ["email_invalid"] }, 400);
  }
  const feedbackId = `fb-${crypto.randomUUID().replace(/-/g, "").slice(0, 12)}`;
  const at = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const record = {
    schema: "sourcea-site-feedback-v1",
    feedback_id: feedbackId,
    status: "open",
    type,
    message,
    page,
    url,
    email: email || undefined,
    at,
    user_agent: request.headers.get("User-Agent")?.slice(0, 200) || undefined,
  };
  await storeFeedback(env, record);
  const subject = `[Site ${type}] ${page || "sourcea.app"} — ${message.slice(0, 48)}`;
  const text = [
    `Feedback ${feedbackId}`,
    `Type: ${type}`,
    `Page: ${page}`,
    `URL: ${url}`,
    email ? `From: ${email}` : "From: anonymous",
    "",
    message,
  ].join("\n");
  const notify = await sendResend(env, {
    to: [FEEDBACK_TO, NOTIFY_TO],
    subject,
    text,
    replyTo: email || undefined,
  });
  return json(request, {
    ok: true,
    schema: "sourcea-site-feedback-receipt-v1",
    feedback_id: feedbackId,
    at,
    end_screen: "Thanks — we read every report. If you left email, we may follow up.",
    notify,
  });
}

async function handleStats(request, env) {
  const url = new URL(request.url);
  const days = Math.min(14, Math.max(1, Number(url.searchParams.get("days") || "1") || 1));
  const range = await loadStatsRange(env, days);
  const today = range[0] || summarizeStatsRow({}, utcDay());
  return json(request, {
    ok: true,
    schema: "sourcea-site-stats-public-v1",
    stats: today,
    range: days > 1 ? range : undefined,
    at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
  });
}

async function handleStatus(request, env) {
  const today = await loadStatsDay(env, utcDay());
  return json(request, {
    ok: true,
    schema: "sourcea-site-pulse-status-v1",
    service: "sourcea-site-pulse-v1",
    kv_ready: Boolean(env.PULSE_KV),
    resend_ready: Boolean(env.RESEND_API_KEY),
    founder_dashboard_ready: Boolean(env.FOUNDER_PULSE_KEY),
    endpoints: {
      event: EVENT_PATH,
      feedback: FEEDBACK_PATH,
      stats: STATS_PATH,
      dashboard: DASHBOARD_PATH,
      status: STATUS_PATH,
      health: HEALTH_PATH,
    },
    today,
    at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
  });
}

async function handleDashboard(request, env) {
  if (!founderAuthorized(request, env)) {
    return json(
      request,
      {
        ok: false,
        schema: "sourcea-site-dashboard-v1",
        error: "founder_key_required",
        hint: "Set FOUNDER_PULSE_KEY on worker · pass X-SourceA-Pulse-Key header",
      },
      401
    );
  }
  const url = new URL(request.url);
  const days = Math.min(14, Math.max(1, Number(url.searchParams.get("days") || "7") || 7));
  const limit = Math.min(100, Math.max(1, Number(url.searchParams.get("limit") || String(MAX_FEEDBACK_INBOX)) || MAX_FEEDBACK_INBOX));
  const [range, inbox] = await Promise.all([loadStatsRange(env, days), loadFeedbackInbox(env, limit)]);
  const rollup = range.reduce(
    (acc, row) => {
      acc.pageviews += row.pageviews;
      acc.feedback_count += row.feedback_count;
      return acc;
    },
    { pageviews: 0, feedback_count: 0, days }
  );
  return json(request, {
    ok: true,
    schema: "sourcea-site-dashboard-v1",
    at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
    service: "sourcea-site-pulse-v1",
    today: range[0],
    rollup,
    range,
    inbox,
    inbox_count: inbox.length,
    open_feedback_count: inbox.filter((item) => (item.status || "open") === "open").length,
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/$/, "") || "/";

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(request) });
    }

    if (path === HEALTH_PATH && request.method === "GET") {
      return json(request, {
        ok: true,
        schema: "sourcea-site-pulse-health-v1",
        service: "sourcea-site-pulse-v1",
        kv_ready: Boolean(env.PULSE_KV),
        at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
      });
    }
    if (path === STATUS_PATH && request.method === "GET") {
      return handleStatus(request, env);
    }
    if (path === EVENT_PATH && request.method === "POST") {
      return handleEvent(request, env);
    }
    if (path === FEEDBACK_PATH && request.method === "POST") {
      return handleFeedback(request, env);
    }
    if (path === STATS_PATH && request.method === "GET") {
      return handleStats(request, env);
    }
    if (path === DASHBOARD_PATH && request.method === "GET") {
      return handleDashboard(request, env);
    }
    if (path === "/api/site/pulse/v1" && request.method === "GET") {
      return json(request, {
        ok: true,
        schema: "sourcea-site-pulse-v1",
        endpoints: {
          event: EVENT_PATH,
          feedback: FEEDBACK_PATH,
          stats: STATS_PATH,
          dashboard: DASHBOARD_PATH,
          status: STATUS_PATH,
          health: HEALTH_PATH,
        },
        kv_ready: Boolean(env.PULSE_KV),
        founder_dashboard_ready: Boolean(env.FOUNDER_PULSE_KEY),
      });
    }

    return json(request, { ok: false, error: "not_found" }, 404);
  },
};
