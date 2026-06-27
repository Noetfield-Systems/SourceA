const INTAKE_PATH = "/api/commercial/mvp-intake/v1";
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const END_SCREEN = "We'll respond in 2 hours with a plan.";
const NOTIFY_TO = "hello@sourcea.app";
const NOTIFY_FROM = "SourceA Intake <onboarding@resend.dev>";

function cors(request) {
  const origin = request.headers.get("Origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
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
    at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
    channel: "cloudflare_worker",
    plane: "commercial",
    business: "48h-mvp-service",
    intake: {
      building,
      building_type: b.building_type || undefined,
      : b. || undefined,
      deadline,
      budget,
      email,
    },
    end_screen: END_SCREEN,
    notify,
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== INTAKE_PATH) {
      return new Response("Not found", { status: 404 });
    }
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(request) });
    }
    if (request.method === "POST") {
      return handlePost(request, env);
    }
    return json(request, { ok: false, error: "method_not_allowed" }, 405);
  },
};
