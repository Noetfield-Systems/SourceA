/** Temporary bridge: www.witnessbc.com -> Cloudflare Pages commercial deploy. */
export default {
  async fetch(request, env) {
    const origin = env.WITNESSBC_ORIGIN || env.VERCEL_ORIGIN || "witnessbc-commercial.pages.dev";
    const publicHost = env.PUBLIC_HOST || "www.witnessbc.com";
    const incoming = new URL(request.url);
    const target = new URL(incoming.pathname + incoming.search, `https://${origin}`);
    const headers = new Headers(request.headers);
    headers.set("Host", origin);
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
