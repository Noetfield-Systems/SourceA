/**
 * Pure Flow — unified Worker (static assets + intake API + email + KV)
 */

const PROPERTY_LABELS = {
  pool: "Pool only",
  spa: "Spa / hot tub only",
  both: "Pool + spa",
  unsure: "Not sure yet",
};

const INTEREST_LABELS = {
  weekly: "Weekly pool maintenance",
  biweekly: "Bi-weekly pool maintenance",
  combo: "Pool + spa combo plan",
  opening: "Spring pool opening",
  closing: "Fall pool closing",
  recovery: "Green / cloudy water (urgent)",
  quote: "One-time service / not sure",
};

const DATE_LABELS = {
  asap: "As soon as possible",
  "this-week": "This week",
  "next-week": "Next week",
  flexible: "Flexible",
};

const TIME_LABELS = {
  morning: "Morning (8am – 12pm)",
  afternoon: "Afternoon (12pm – 5pm)",
  flexible: "Either works",
};

function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      ...extraHeaders,
    },
  });
}

function validate(body) {
  const errors = [];
  for (const key of ["name", "email", "phone", "postal", "property", "interest", "preferred_date", "preferred_time"]) {
    if (!String(body[key] || "").trim()) errors.push(`${key} is required`);
  }
  const email = String(body.email || "").trim();
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.push("invalid email");
  const phone = String(body.phone || "").replace(/\D/g, "");
  if (phone && phone.length < 10) errors.push("invalid phone");
  return errors;
}

function formatLeadEmail(body, leadId) {
  const lines = [
    "New Pure Flow booking request",
    `Booking ref: ${leadId}`,
    `Received: ${new Date().toISOString()}`,
    "",
    `Name: ${body.name}`,
    `Email: ${body.email}`,
    `Phone: ${body.phone}`,
    `Service address: ${body.postal}`,
    `Needs service: ${PROPERTY_LABELS[body.property] || body.property}`,
    `Service booked: ${INTEREST_LABELS[body.interest] || body.interest}`,
    `Preferred day: ${DATE_LABELS[body.preferred_date] || body.preferred_date}`,
    `Preferred time: ${TIME_LABELS[body.preferred_time] || body.preferred_time}`,
    `Found via: ${body.referral || "N/A"}`,
    `Language: ${body.locale || "en"}`,
    "",
    "Notes:",
    body.message || "(none)",
  ];
  const text = lines.join("\n");
  const html = lines.map((l) => `<p>${l.replace(/</g, "&lt;")}</p>`).join("");
  return { text, html };
}

async function handleQuote(request, env) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: { "Access-Control-Allow-Origin": "*" } });
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ ok: false, error: "invalid_json" }, 400);
  }

  const errors = validate(body);
  if (errors.length) {
    return json({ ok: false, error: "validation_failed", messages: errors }, 422);
  }

  const leadId = `pf_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  const record = {
    id: leadId,
    ...body,
    submittedAt: new Date().toISOString(),
    source: "pureflow-landing",
    userAgent: request.headers.get("User-Agent") || "",
  };

  try {
    await env.PUREFLOW_LEADS.put(leadId, JSON.stringify(record), {
      metadata: { email: body.email, interest: body.interest },
    });
  } catch (err) {
    return json({ ok: false, error: "storage_failed", detail: String(err) }, 500);
  }

  const notifyTo = env.NOTIFY_EMAIL || "";
  const siteUrl = (env.SITE_URL || "https://pureflow.sourcea.app").replace(/\/$/, "");
  const fromRaw = env.NOTIFY_FROM || "Pure Flow Pool & Spa <hello@pureflow.sourcea.app>";
  const fromMatch = fromRaw.match(/^(.*)<([^>]+)>$/);
  const fromName = fromMatch ? fromMatch[1].trim() : "Pure Flow Pool & Spa";
  const fromEmail = fromMatch ? fromMatch[2].trim() : "hello@pureflow.sourcea.app";

  let emailSent = false;
  let emailError = null;

  if (env.EMAIL) {
    try {
      const { text, html } = formatLeadEmail(body, leadId);
      await env.EMAIL.send({
        to: notifyTo,
        from: { email: fromEmail, name: fromName },
        replyTo: body.email,
        subject: `Pure Flow booking — ${body.name} (${INTEREST_LABELS[body.interest] || body.interest})`,
        text,
        html,
      });
      emailSent = true;
    } catch (err) {
      emailError = String(err);
    }

    if (body.email) {
      try {
        await env.EMAIL.send({
          to: body.email,
          from: { email: fromEmail, name: fromName },
          subject: "Pure Flow — your booking request is received",
          text: `Hi ${body.name},\n\nThanks for booking with Pure Flow Pool & Spa. We received your request for ${INTEREST_LABELS[body.interest] || body.interest}.\n\nPreferred: ${DATE_LABELS[body.preferred_date] || body.preferred_date}, ${TIME_LABELS[body.preferred_time] || body.preferred_time}\n\nWe'll confirm your exact visit time within 4 business hours.\n\nBooking ref: ${leadId}\n\n— Pure Flow Pool & Spa\nMetro Vancouver`,
          html: `<p>Hi ${body.name},</p><p>Thanks for booking with <strong>Pure Flow Pool &amp; Spa</strong>. We received your request for <strong>${INTEREST_LABELS[body.interest] || body.interest}</strong>.</p><p><strong>Preferred:</strong> ${DATE_LABELS[body.preferred_date] || body.preferred_date}, ${TIME_LABELS[body.preferred_time] || body.preferred_time}</p><p>We'll confirm your exact visit time within <strong>4 business hours</strong>.</p><p>Booking ref: <code>${leadId}</code></p><p>— Pure Flow Pool &amp; Spa · Metro Vancouver</p>`,
        });
      } catch {
        /* non-fatal */
      }
    }
  }

  return json({
    ok: true,
    leadId,
    emailSent,
    emailError: emailError || undefined,
    message: "Booking received. We'll confirm your visit time within 4 business hours.",
  });
}

async function handleHealth(env) {
  return json({
    ok: true,
    service: "pureflow-intake",
    version: "1.1.0",
    kv: Boolean(env.PUREFLOW_LEADS),
    email: Boolean(env.EMAIL),
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const canonicalHost = new URL(env.SITE_URL || "https://pureflow.sourcea.app").host;

    if (url.host !== canonicalHost && url.host.endsWith(".workers.dev")) {
      const target = new URL(request.url);
      target.protocol = "https:";
      target.host = canonicalHost;
      return Response.redirect(target.toString(), 301);
    }

    if (url.pathname === "/api/health") {
      return handleHealth(env);
    }

    if (url.pathname === "/api/quote") {
      if (request.method !== "POST") {
        return json({ ok: false, error: "method_not_allowed" }, 405);
      }
      return handleQuote(request, env);
    }

    const path = url.pathname;
    if (path === "/" || path === "") {
      return Response.redirect(`${url.origin}/en/`, 302);
    }

    const localeRoot = path.match(/^\/(en|fr|fa|zh)\/?$/);
    if (localeRoot) {
      const indexUrl = new URL(request.url);
      indexUrl.pathname = "/index.html";
      const assetResponse = await env.ASSETS.fetch(
        new Request(indexUrl.toString(), { method: "GET", headers: request.headers })
      );
      if (assetResponse.status >= 300 && assetResponse.status < 400) {
        const direct = await env.ASSETS.fetch(
          new Request(new URL("/index.html", request.url).toString(), { method: "GET" })
        );
        return new Response(direct.body, {
          status: 200,
          headers: { "content-type": "text/html; charset=utf-8" },
        });
      }
      return assetResponse;
    }

    return env.ASSETS.fetch(request);
  },
};
