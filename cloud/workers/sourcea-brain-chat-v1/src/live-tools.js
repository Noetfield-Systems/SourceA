/** Public read-only live tools for Brain v5. */

const SOURCEA_ORIGIN = "https://sourcea.app";
const DATA_BASE = `${SOURCEA_ORIGIN}/sourcea/data`;
const PLAN_REGISTRY_URL = "https://sourcea-cloud-auto-runtime-tick-v1.sina-kazemnezhad-ca.workers.dev/plan-registry";
const TOOL_TIMEOUT_MS = 1400;

const ROUTES = {
  proof: `${SOURCEA_ORIGIN}/sourcea/proof/live`,
  forge_terminal: `${SOURCEA_ORIGIN}/sourcea/forge/terminal`,
  pricing: `${SOURCEA_ORIGIN}/sourcea/pricing`,
  factories: `${SOURCEA_ORIGIN}/sourcea/factories/`,
  start: `${SOURCEA_ORIGIN}/start`,
  products: `${SOURCEA_ORIGIN}/sourcea/`,
};

function wants(message, pattern) {
  return pattern.test(String(message || "").toLowerCase());
}

function wantsPricing(message) {
  const q = String(message || "").toLowerCase();
  return (
    /\b(price|pricing|cost|how much|tier)\b/.test(q) ||
    /\b(?:build|rent|own)\s+(?:tier|plan|pricing|option|model)\b/.test(q)
  );
}

async function fetchJson(path) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TOOL_TIMEOUT_MS);
  try {
    const resp = await fetch(`${DATA_BASE}/${path}`, {
      headers: { Accept: "application/json", "User-Agent": "SourceA-Brain-LiveTools/1.0" },
      signal: ctrl.signal,
    });
    if (!resp.ok) return { ok: false, status: resp.status, path };
    const row = await resp.json();
    return { ok: true, path, row };
  } catch (err) {
    return { ok: false, path, error: String(err && err.message ? err.message : err).slice(0, 120) };
  } finally {
    clearTimeout(timer);
  }
}

function publicUrl(url) {
  const raw = String(url || "").trim();
  if (!raw) return "";
  if (raw.startsWith("https://sourcea.app")) return raw;
  if (raw.startsWith("/")) return `${SOURCEA_ORIGIN}${raw}`;
  return "";
}

function cleanPublicCopy(text) {
  return String(text || "")
    .replace(/\bPASS\/BLOCK\b/g, "allowed-or-stopped result")
    .replace(/\bPASS or BLOCK\b/g, "allowed or stopped")
    .replace(/\bALLOW\/BLOCK\b/g, "allowed-or-stopped result")
    .replace(/\bALLOW or BLOCK\b/g, "allowed or stopped")
    .replace(/\bPASS\b/g, "passed")
    .replace(/\bALLOW\b/g, "allowed")
    .replace(/\bBLOCK\b/g, "stopped")
    .replace(/\bOpenRouter routing\b/gi, "AI model routing")
    .replace(/\bOpenRouter\b/gi, "AI model layer")
    .replace(/\bFactory proceed\b/gi, "Cloud execution")
    .replace(/\bG0[–-]G3\b/gi, "controlled")
    .replace(/\bprove pack\b/gi, "proof pack")
    .replace(/\bFINTRAC-shaped\b/gi, "compliance-shaped")
    .replace(/\bCorporate registry docs in\b/gi, "Company documents in")
    .replace(/\bRunReceipt\b/gi, "run receipt")
    .replace(/\bcontrolled controlled\b/gi, "controlled")
    .replace(/\s{2,}/g, " ")
    .trim();
}

function compactItems(items, limit = 7) {
  return (items || []).slice(0, limit).map((item) => ({
    title: cleanPublicCopy(item.title || item.name || item.slug || item.id),
    subtitle: cleanPublicCopy(item.subtitle || item.tagline || item.proof || ""),
    status: item.status || "",
    url: publicUrl(item.url || item.href || item.demo_url || ""),
  }));
}

function findPlanId(message) {
  const match = String(message || "").match(/\b(?:cu|sa|brain|cloud|tf|nf|fbe|forge|site|sourcea)[a-z0-9-]*-\d{3,5}\b/i);
  return match ? match[0] : "";
}

async function fetchPlanRegistry(params) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TOOL_TIMEOUT_MS);
  const url = new URL(PLAN_REGISTRY_URL);
  for (const [key, value] of Object.entries(params || {})) {
    if (value !== undefined && value !== null && String(value).trim()) {
      url.searchParams.set(key, String(value).trim());
    }
  }
  try {
    const resp = await fetch(url, {
      headers: { Accept: "application/json", "User-Agent": "Mozilla/5.0 SourceA-Brain-PlanRegistry/1.0" },
      signal: ctrl.signal,
    });
    if (!resp.ok) return { ok: false, status: resp.status };
    const row = await resp.json();
    const rows = Array.isArray(row.rows) ? row.rows.slice(0, 5) : [];
    return {
      id: "plan_registry",
      ok: Boolean(row.ok),
      count: row.count,
      total: row.total,
      found: row.found,
      plan_id: row.plan_id || params.plan_id || "",
      items: rows.map((item) => ({
        plan_id: item.plan_id,
        title: cleanPublicCopy(item.title || item.plan_id || ""),
        status: item.status || "",
        lane: item.lane || "",
        priority: item.priority || "",
      })),
    };
  } catch (err) {
    return { id: "plan_registry", ok: false, error: String(err && err.message ? err.message : err).slice(0, 120) };
  } finally {
    clearTimeout(timer);
  }
}

function proofTool(row) {
  const checks = Array.isArray(row.checks) ? row.checks : [];
  return {
    id: "proof_status",
    ok: Boolean(row.ok || row.verdict === "PASS" || row.verdict === "APPROVED"),
    verdict: row.verdict || row.public_display?.result || "unknown",
    at: row.at || row.exported_at || null,
    summary: row.founder_line || row.prove_summary || row.public_display?.status || "",
    checks_passed: checks.filter((c) => c.ok !== false).length || undefined,
    url: ROUTES.proof,
  };
}

function productsTool(row) {
  const groups = ["platform", "services", "case_studies"];
  const items = groups.flatMap((key) => (Array.isArray(row[key]) ? row[key] : []));
  return {
    id: "products_catalog",
    ok: true,
    count: row.product_count || items.length,
    items: compactItems(items, 8),
    url: ROUTES.products,
  };
}

function factoriesTool(row) {
  const factories = Array.isArray(row.factories) ? row.factories : [];
  return {
    id: "factories_catalog",
    ok: true,
    count: factories.length,
    items: compactItems(factories, 8),
    url: ROUTES.factories,
  };
}

function routeTool(id, url, label) {
  return { id, ok: true, label, url };
}

export async function gatherLiveTools(message) {
  const q = String(message || "").toLowerCase();
  const jobs = [];
  const tools = [];

  if (wants(q, /\b(live receipt|receipt|proof|status|is .* live|up|running)\b/)) {
    jobs.push(
      fetchJson("boot-proof.json").then((res) => res.ok && tools.push(proofTool(res.row))),
      fetchJson("phase1-proof-pack-public-v1.json").then((res) => res.ok && tools.push(proofTool(res.row))),
    );
  }

  if (wants(q, /\b(factory|factories|workflow factory|what factories)\b/)) {
    jobs.push(fetchJson("factories-catalog.json").then((res) => res.ok && tools.push(factoriesTool(res.row))));
  }

  if (wants(q, /\b(product|products|platform|tools|chat unify|cloud workers|case stud|what do you offer)\b/)) {
    jobs.push(fetchJson("sourcea-products-catalog-v1.json").then((res) => res.ok && tools.push(productsTool(res.row))));
  }

  if (wantsPricing(q)) {
    tools.push(routeTool("pricing_route", ROUTES.pricing, "Public pricing page"));
  }

  if (wants(q, /\b(forge terminal|try forge|browser|demo|ide cloud)\b/)) {
    tools.push(routeTool("forge_terminal_route", ROUTES.forge_terminal, "Forge Terminal browser demo"));
  }

  if (wants(q, /\b(start|get started|sandbox|register|try sourcea)\b/)) {
    tools.push(routeTool("start_route", ROUTES.start, "Start / sandbox path"));
  }

  const planId = findPlanId(q);
  if (planId || wants(q, /\b(plan registry|plan id|plan_id|roadmap row|next plans?)\b/)) {
    jobs.push(
      fetchPlanRegistry(planId ? { plan_id: planId } : { limit: 5 }).then((tool) => {
        if (tool && tool.id === "plan_registry") tools.push(tool);
      }),
    );
  }

  await Promise.allSettled(jobs);
  return tools;
}

export function liveToolsPrompt(tools) {
  if (!Array.isArray(tools) || !tools.length) return "";
  const blocks = tools.map((tool) => {
    if (tool.items) {
      const items = tool.items
        .filter((item) => item.title)
        .map((item) => {
          if (tool.id === "plan_registry") {
            return `- ${item.plan_id}: ${item.title}${item.status ? ` · ${item.status}` : ""}${item.lane ? ` · ${item.lane}` : ""}`;
          }
          return `- ${item.title}${item.subtitle ? `: ${item.subtitle}` : ""}${item.url ? ` (${item.url})` : ""}`;
        })
        .join("\n");
      return `### ${tool.id}\nStatus: ${tool.ok ? "ok" : "unavailable"}\nCount: ${tool.count || tool.items.length}\nURL: ${tool.url}\n${items}`;
    }
    return `### ${tool.id}\nStatus: ${tool.ok ? "ok" : "unavailable"}\n${tool.verdict ? `Verdict: ${tool.verdict}\n` : ""}${tool.summary ? `Summary: ${tool.summary}\n` : ""}URL: ${tool.url}`;
  });
  return `\n\nLIVE TOOL RESULTS (current public data; prefer this over corpus for status/catalog facts):\n${blocks.join("\n\n")}`;
}

export function liveToolsMeta(tools) {
  return (tools || []).map((tool) => ({
    id: tool.id,
    ok: tool.ok,
    count: tool.count || undefined,
    verdict: tool.verdict || undefined,
    url: tool.url || undefined,
    found: tool.found,
    plan_id: tool.plan_id || undefined,
  }));
}

function bullets(items, limit = 5) {
  return (items || [])
    .slice(0, limit)
    .filter((item) => item.title)
    .map((item) => `- ${item.title}${item.subtitle ? ` — ${item.subtitle}` : ""}${item.url ? `\n  ${item.url}` : ""}`)
    .join("\n");
}

export function directLiveToolAnswer(message, tools) {
  const q = String(message || "").toLowerCase();
  const byId = Object.fromEntries((tools || []).map((tool) => [tool.id, tool]));

  if (wantsPricing(q) && byId.pricing_route) {
    return [
      "Pricing depends on the scope and ownership model.",
      "",
      "Use the pricing page for the current public tiers: https://sourcea.app/sourcea/pricing",
      "",
      "Simple read: Build is for a scoped project, Rent is for an ongoing managed system, and Own is for buying the system/IP path.",
    ].join("\n");
  }

  if (/\b(factory|factories|what factories)\b/.test(q) && byId.factories_catalog) {
    const t = byId.factories_catalog;
    return [
      `SourceA currently lists ${t.count || "multiple"} public factories.`,
      "",
      bullets(t.items, 6),
      "",
      `Full catalog: ${t.url}`,
    ].join("\n");
  }

  if (/\b(product|products|platform|tools|what do you offer)\b/.test(q) && byId.products_catalog) {
    const t = byId.products_catalog;
    return [
      `SourceA currently lists ${t.count || "multiple"} public products, services, and proof surfaces.`,
      "",
      bullets(t.items, 6),
      "",
      `Start here: ${SOURCEA_ORIGIN}/sourcea/`,
    ].join("\n");
  }

  if (byId.plan_registry && /\b(plan registry|plan id|plan_id|roadmap row|next plans?|cu-|sa-|brain-|cloud-)\b/.test(q)) {
    const t = byId.plan_registry;
    const items = t.items || [];
    if (!items.length) {
      return "I can check only small public-safe plan slices. I could not find a matching plan row for that request.";
    }
    return [
      t.plan_id
        ? `I found this plan row for ${t.plan_id}:`
        : `I can summarize a small public-safe slice of the plan registry. Total visible rows: ${t.total || "available"}.`,
      "",
      items
        .slice(0, 5)
        .map((item) => `- ${item.plan_id}: ${item.title}${item.status ? ` · ${item.status}` : ""}${item.lane ? ` · ${item.lane}` : ""}`)
        .join("\n"),
      "",
      "I will not dump the full backlog into chat. Use an exact plan id or a narrow lane/status filter for more detail.",
    ].join("\n");
  }

  if (/\b(live receipt|receipt|is .* live|running|status)\b/.test(q) && byId.proof_status) {
    const t = byId.proof_status;
    if (/\b(is .* live|running|status|up)\b/.test(q)) {
      return [
        `Live proof is ${t.ok ? "available" : "not showing as available"}.`,
        "",
        `Live proof: ${SOURCEA_ORIGIN}/sourcea/proof/live`,
      ].join("\n");
    }
    return [
      `Live proof is ${t.ok ? "available" : "not showing as available"}.`,
      "",
      "A live receipt is proof that a SourceA run actually happened: what ran, what was checked, and what result it produced.",
      "",
      `Live proof: ${SOURCEA_ORIGIN}/sourcea/proof/live`,
    ].join("\n");
  }

  return "";
}
