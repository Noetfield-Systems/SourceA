/** Proxy Brain chat to OpenRouter worker — same-origin /api/brain/chat/v1 on Pages. */
const BRAIN_WORKER_URL =
  "https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/api/brain/chat/v1";

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

export async function onRequest(context) {
  const { request } = context;
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: cors(request) });
  }
  if (request.method !== "GET" && request.method !== "POST") {
    return new Response(JSON.stringify({ ok: false, error: "method_not_allowed" }), {
      status: 405,
      headers: cors(request),
    });
  }
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
