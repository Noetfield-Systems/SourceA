export type TargetPolicyResult =
  | { ok: true; url: string; hostname: string }
  | { ok: false; reason: string };

/**
 * Exact-host allowlist for the WEBPAGE_REPAIR slice.
 * Missing configuration is a hard block; credentials, non-HTTPS URLs,
 * alternate ports, IP literals and host suffix tricks are not accepted.
 */
export function validateExecutiveTargetUrl(
  raw: string,
  allowedHosts: string | string[] | undefined,
): TargetPolicyResult {
  const hosts = (Array.isArray(allowedHosts) ? allowedHosts : String(allowedHosts ?? "").split(","))
    .map((host) => host.trim().toLowerCase())
    .filter(Boolean);
  if (hosts.length === 0) return { ok: false, reason: "target_allowlist_missing" };

  let url: URL;
  try {
    url = new URL(raw);
  } catch {
    return { ok: false, reason: "target_url_invalid" };
  }

  if (url.protocol !== "https:") return { ok: false, reason: "target_https_required" };
  if (url.username || url.password) return { ok: false, reason: "target_credentials_forbidden" };
  if (url.port && url.port !== "443") return { ok: false, reason: "target_port_forbidden" };
  if (url.hostname.endsWith(".") || url.hostname.includes("%")) {
    return { ok: false, reason: "target_hostname_noncanonical" };
  }
  const hostname = url.hostname.toLowerCase();
  if (!hosts.includes(hostname)) return { ok: false, reason: "target_host_not_allowed" };
  url.hash = "";
  return { ok: true, url: url.toString(), hostname };
}
