/** Temporary bridge: www.witnessbc.com → main Vercel deploy (DNS auto via CF Custom Domain). */
export default {
  async fetch(request, env) {
    const origin = env.VERCEL_ORIGIN || "deploy-witnessbc-agentic-governance-theta.vercel.app";
    const publicHost = env.PUBLIC_HOST || "www.witnessbc.com";
    const incoming = new URL(request.url);
    const target = new URL(incoming.pathname + incoming.search, `https://${origin}`);
    const headers = new Headers(request.headers);
    headers.set("Host", publicHost);
    headers.set("X-Forwarded-Host", publicHost);
    return fetch(
      new Request(target.toString(), {
        method: request.method,
        headers,
        body: request.method === "GET" || request.method === "HEAD" ? undefined : request.body,
        redirect: "manual",
      }),
    );
  },
};
