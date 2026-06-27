import {
  chatUnifyProxyRequest,
} from "../../_chat_unify_proxy_v1.js";

const SHELL_HEALTH = {
  ok: false,
  mode: "web_shell",
  tier: "paid",
  service: "chat-unify",
  ui_version: "4.9.9",
  message:
    "Cloud Chat Unify API is not wired yet. Set CHAT_UNIFY_UPSTREAM_URL on Cloudflare Pages.",
  download: "https://sourcea.app/downloads/chat-unify-mac-v1.dmg",
  forge_demo: "https://sourcea.app/sourcea/forge/terminal",
};

const SHELL_ERROR = {
  ...SHELL_HEALTH,
  error: "upstream_missing",
};

export async function onRequest(context) {
  return chatUnifyProxyRequest(context, {
    apiPrefix: "/unify/api",
    shellHealth: SHELL_HEALTH,
    shellError: SHELL_ERROR,
  });
}
