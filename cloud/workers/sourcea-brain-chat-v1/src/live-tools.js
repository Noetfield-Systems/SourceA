/** Public read-only live tools for Brain v5. */

const SOURCEA_ORIGIN = "https://sourcea.app";
const DATA_BASE = `${SOURCEA_ORIGIN}/sourcea/data`;
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

  if (wants(q, /\b(price|pricing|cost|tier|build|rent|own|how much)\b/)) {
    tools.push(routeTool("pricing_route", ROUTES.pricing, "Public pricing page"));
  }

  if (wants(q, /\b(forge terminal|try forge|browser|demo|ide cloud)\b/)) {
    tools.push(routeTool("forge_terminal_route", ROUTES.forge_terminal, "Forge Terminal browser demo"));
  }

  if (wants(q, /\b(start|get started|sandbox|register|try sourcea)\b/)) {
    tools.push(routeTool("start_route", ROUTES.start, "Start / sandbox path"));
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
        .map((item) => `- ${item.title}${item.subtitle ? `: ${item.subtitle}` : ""}${item.url ? ` (${item.url})` : ""}`)
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

  if (/\b(price|pricing|cost|how much|tier|build|rent|own)\b/.test(q) && byId.pricing_route) {
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

  if (/\b(live receipt|receipt|proof|is .* live|running|status)\b/.test(q) && byId.proof_status) {
    const t = byId.proof_status;
    if (/\b(is .* live|running|status|up)\b/.test(q)) {
      return [
        `Live proof is ${t.ok ? "available" : "not showing as available"}${t.verdict ? ` (${t.verdict})` : ""}.`,
        "",
        `Live proof: ${SOURCEA_ORIGIN}/sourcea/proof/live`,
      ].join("\n");
    }
    return [
      `Live proof is ${t.ok ? "available" : "not showing as available"}${t.verdict ? ` (${t.verdict})` : ""}.`,
      "",
      "A live receipt is proof that a SourceA run actually happened: what ran, what was checked, and what result it produced.",
      "",
      `Live proof: ${SOURCEA_ORIGIN}/sourcea/proof/live`,
    ].join("\n");
  }

  return "";
}
