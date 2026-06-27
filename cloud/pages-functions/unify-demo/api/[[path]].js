import { chatUnifyProxyRequest } from "../../_chat_unify_proxy_v1.js";

const DEMO_HEALTH = {
  ok: true,
  mode: "demo_shell",
  service: "chat-unify-demo",
  ui_version: "4.9.9",
  ui_profile: "4.6.1-demo",
  message: "Public demo — proxies to cloud API when CHAT_UNIFY_UPSTREAM_URL is set.",
  upgrade_url: "https://sourcea.app/unify/",
  demo_url: "https://sourcea.app/unify-demo/",
};

const DEMO_ERROR = {
  ok: false,
  mode: "demo_shell",
  service: "chat-unify-demo",
  error: "upstream_missing",
  message: "Demo shell — set CHAT_UNIFY_UPSTREAM_URL on Pages or use Mac app.",
  upgrade_url: "https://sourcea.app/unify/",
};

export async function onRequest(context) {
  return chatUnifyProxyRequest(context, {
    apiPrefix: "/unify-demo/api",
    shellHealth: DEMO_HEALTH,
    shellError: DEMO_ERROR,
  });
}
