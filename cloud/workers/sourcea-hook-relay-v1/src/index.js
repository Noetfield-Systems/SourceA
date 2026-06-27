/** Hosted webhook relay — forwards to founder Mac hook or queues (STAB-056). */
const HOOK_SECRET = ""; // set via wrangler secret HOOK_SECRET

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== "/v1/relay" && url.pathname !== "/v1/relay/") {
      return new Response(JSON.stringify({ ok: false, error: "not_found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      });
    }
    if (request.method === "GET") {
      return new Response(
        JSON.stringify({
          ok: true,
          schema: "sourcea-hook-relay-v1",
          hook: "POST /v1/relay",
          manifest: "https://sourcea.app/sourcea/data/chat-unify-integrations-v1.json",
          n8n_template: "https://sourcea.app/sourcea/data/n8n-template-sourcea-chat-unify-v1.json",
        }),
        { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } },
      );
    }
    if (request.method !== "POST") {
      return new Response(JSON.stringify({ ok: false, error: "method_not_allowed" }), { status: 405 });
    }
    const secret = env.HOOK_SECRET || HOOK_SECRET;
    if (secret && request.headers.get("X-SourceA-Hook-Secret") !== secret) {
      return new Response(JSON.stringify({ ok: false, error: "unauthorized" }), { status: 401 });
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
    return new Response(JSON.stringify(receipt), {
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  },
};
