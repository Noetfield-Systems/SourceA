/** Hosted webhook relay — forwards to founder Mac hook or queues (STAB-056). */
const HOOK_SECRET = ""; // set via wrangler secret HOOK_SECRET
const RELAY_PATH = "/v1/relay";
const STATUS_PATH = "/v1/status";

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "no-store",
    },
  });
}

function statusBody(env) {
  return {
    ok: true,
    schema: "sourcea-hook-relay-status-v1",
    service: "sourcea-hook-relay-v1",
    relay: `POST ${RELAY_PATH}`,
    auth_ready: Boolean(env.HOOK_SECRET || HOOK_SECRET),
    forward_ready: Boolean(env.MAC_HOOK_URL),
    manifest: "https://sourcea.app/sourcea/data/chat-unify-integrations-v1.json",
    n8n_template: "https://sourcea.app/sourcea/data/n8n-template-sourcea-chat-unify-v1.json",
    endpoints: {
      health: "/health",
      status: STATUS_PATH,
      relay: RELAY_PATH,
    },
    at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
  };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/$/, "") || "/";
    if (path === "/health" && request.method === "GET") {
      return json({
        ok: true,
        schema: "sourcea-hook-relay-health-v1",
        service: "sourcea-hook-relay-v1",
        auth_ready: Boolean(env.HOOK_SECRET || HOOK_SECRET),
        forward_ready: Boolean(env.MAC_HOOK_URL),
        at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
      });
    }
    if (path === STATUS_PATH && request.method === "GET") {
      return json(statusBody(env));
    }
    if (path !== RELAY_PATH) {
      return json({ ok: false, error: "not_found" }, 404);
    }
    if (request.method === "GET") {
      return json({ ...statusBody(env), schema: "sourcea-hook-relay-v1", hook: `POST ${RELAY_PATH}` });
    }
    if (request.method !== "POST") {
      return json({ ok: false, error: "method_not_allowed" }, 405);
    }
    const secret = env.HOOK_SECRET || HOOK_SECRET;
    if (secret && request.headers.get("X-SourceA-Hook-Secret") !== secret) {
      return json({ ok: false, error: "unauthorized" }, 401);
    }
    let body;
    try {
      body = await request.json();
    } catch {
      body = {};
    }
    const receipt = {
      schema: "sourcea-hook-relay-receipt-v1",
      ok: true,
      at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
      event: body.event || "forge.mission",
      source: body.source || "hosted",
      note: "Relay accepted — wire Mac hook URL in env MAC_HOOK_URL for forward v2",
    };
    const macUrl = env.MAC_HOOK_URL;
    if (macUrl) {
      try {
        const fwd = await fetch(macUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        receipt.forward = { ok: fwd.ok, status: fwd.status };
      } catch (e) {
        receipt.forward = { ok: false, error: String(e).slice(0, 120) };
      }
    }
    return json(receipt);
  },
};
