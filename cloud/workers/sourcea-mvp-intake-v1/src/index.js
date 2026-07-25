const INTAKE_PATH = "/api/commercial/mvp-intake/v1";
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const END_SCREEN = "We'll respond in 2 hours with a plan.";
const NOTIFY_TO = "hello@sourcea.app";
const NOTIFY_FROM = "SourceA Intake <onboarding@resend.dev>";

function cors(request, methods = "GET, POST, OPTIONS") {
  const origin = request.headers.get("Origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": methods,
    "Access-Control-Allow-Headers": "Content-Type",
    Vary: "Origin",
    "Content-Type": "application/json",
  };
}

function json(request, body, status = 200, methods) {
  return new Response(JSON.stringify(body), { status, headers: cors(request, methods) });
}

async function persistIntake(env, intakeId, record) {
  if (!env.INTAKE_KV) {
    return { ok: false, skipped: true, reason: "INTAKE_KV_missing" };
  }
  await env.INTAKE_KV.put(`intake:${intakeId}`, JSON.stringify(record), {
    expirationTtl: 60 * 60 * 24 * 365,
  });
  return { ok: true, storage: "kv" };
}

async function readIntake(env, intakeId) {
  if (!env.INTAKE_KV) {
    return null;
  }
  const raw = await env.INTAKE_KV.get(`intake:${intakeId}`);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
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
  const at = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const record = {
    schema: "sourcea-mvp-intake-record-v1",
    intake_id: intakeId,
    at,
    channel: "cloudflare_worker",
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
  };
  const storage = await persistIntake(env, intakeId, record);
  let notify = { ok: false, skipped: true, reason: "RESEND_API_KEY_missing" };
  if (env.RESEND_API_KEY) {
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
  }
  return json(request, {
    schema: "sourcea-mvp-intake-receipt-v1",
    ok: true,
    intake_id: intakeId,
    at,
    channel: "cloudflare_worker",
    plane: "commercial",
    business: "48h-mvp-service",
    intake: record.intake,
    end_screen: END_SCREEN,
    storage,
    notify,
  });
}

async function handleGet(request, env, intakeId) {
  const row = await readIntake(env, intakeId);
  if (!row) {
    return json(request, { ok: false, schema: "sourcea-mvp-intake-read-v1", error: "not_found", intake_id: intakeId }, 404);
  }
  return json(request, {
    ok: true,
    schema: "sourcea-mvp-intake-read-v1",
    intake_id: row.intake_id,
    at: row.at,
    intake: row.intake,
    storage: { ok: true, storage: "kv" },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(request) });
    }
    if (url.pathname === INTAKE_PATH && request.method === "POST") {
      return handlePost(request, env);
    }
    const readPrefix = `${INTAKE_PATH}/`;
    if (url.pathname.startsWith(readPrefix) && request.method === "GET") {
      const intakeId = decodeURIComponent(url.pathname.slice(readPrefix.length)).trim();
      if (!intakeId || intakeId.includes("/")) {
        return json(request, { ok: false, error: "invalid_intake_id" }, 400);
      }
      return handleGet(request, env, intakeId);
    }
    return new Response("Not found", { status: 404 });
  },
};
