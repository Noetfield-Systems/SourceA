/**
 * SourceA Platform session — Sign in → Profile → Workspace.
 * Browser: localStorage · Mac Forge: ~/.sina/sourcea-platform-session-v1.json via API.
 */
(function (global) {
  "use strict";

  const SCHEMA = "sourcea-platform-session-v1";
  const STORAGE_KEY = "sourcea-platform-session-v1";
  const VERSION = "1.5.0";
  const STEPS = ["sign-in", "profile", "workspace"];
  const ROUTES = {
    signin: "/auth/sign-in",
    signup: "/auth/sign-up",
    callback: "/auth/callback",
    signout: "/auth/sign-out",
    signinForge: "/sourcea/forge/terminal/signin",
    signupForge: "/sourcea/forge/terminal/signup",
    profile: "/sourcea/forge/terminal/profile",
    workspace: "/sourcea/forge/terminal/workspace",
    demo: "/sourcea/forge/terminal",
    platform: "/platform",
  };

  function emptySession() {
    return { schema: SCHEMA, step: "sign-in" };
  }

  function readLocal() {
    try {
      const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
      if (raw && raw.schema === SCHEMA) return raw;
      if (raw && (raw.email || raw.supabase_user_id || raw.signed_in_at)) {
        return Object.assign(emptySession(), raw, { schema: SCHEMA });
      }
      return emptySession();
    } catch {
      return emptySession();
    }
  }

  function writeLocal(row) {
    const prev = readLocal();
    const next = Object.assign(emptySession(), prev, row, { schema: SCHEMA, updated_at: new Date().toISOString() });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    return next;
  }

  function isSignedIn(session) {
    const s = session || readLocal();
    return !!((s.email || s.supabase_user_id) && s.signed_in_at);
  }

  function stepIndex(step) {
    const i = STEPS.indexOf(step);
    return i >= 0 ? i : 0;
  }

  function canAccess(step, session) {
    const s = session || readLocal();
    if (step === "sign-in") return true;
    if (step === "profile") return isSignedIn(s);
    if (step === "workspace") return isSignedIn(s) && !!s.project_name;
    return false;
  }

  function establishLocalSession(email, name) {
    const em = String(email || "").trim();
    const nm = String(name || "").trim() || (em ? em.split("@")[0] : "Founder");
    if (!em) throw new Error("Email is required to start your Forge project.");
    return writeLocal({
      email: em,
      name: nm,
      signed_in_at: new Date().toISOString(),
      auth_provider: "forge_local",
      step: "profile",
    });
  }

  function mountStepNav(navEl, currentStep, opts) {
    if (!navEl) return;
    opts = opts || {};
    const cur = readLocal();
    const order = ["sign-in", "profile", "workspace"];
    const steps = [
      { key: "sign-in", label: opts.signLabel || "1 · Sign in", route: ROUTES.signin },
      { key: "profile", label: "2 · Profile", route: ROUTES.profile },
      { key: "workspace", label: "3 · Workspace", route: ROUTES.workspace },
    ];
    const curIdx = order.indexOf(currentStep);
    navEl.innerHTML = "";
    steps.forEach(function (s, i) {
      const active = s.key === currentStep;
      const done = curIdx > i;
      const canGo = canAccess(s.key, cur) && !active;
      let node;
      if (canGo) {
        node = document.createElement("a");
        node.href = s.route;
        node.className = "sa-po-step is-link" + (done ? " is-done" : "");
      } else {
        node = document.createElement("span");
        node.className = "sa-po-step" + (active ? " is-active" : "") + (done ? " is-done" : "");
      }
      node.textContent = s.label;
      navEl.appendChild(node);
    });
  }

  function currentPath() {
    if (typeof window === "undefined") return "/";
    return (window.location.pathname || "/") + (window.location.search || "");
  }

  function signInUrl(nextPath) {
    var next = nextPath || currentPath();
    var base = ROUTES.signin;
    if (
      !next ||
      next.indexOf("/auth/sign-in") === 0 ||
      next.indexOf("/auth/sign-up") === 0 ||
      next.indexOf("/auth/callback") === 0
    ) {
      return base;
    }
    return base + "?next=" + encodeURIComponent(next);
  }

  function redirectToSignin(nextPath) {
    if (typeof window === "undefined") return;
    var path = window.location.pathname || "";
    if (path.indexOf("/sign-in") !== -1 || path.indexOf("/signin") !== -1 || path.indexOf("/auth/callback") !== -1) {
      return;
    }
    window.location.replace(signInUrl(nextPath));
  }

  function bootTier2HeadGuard(step) {
    if (typeof window === "undefined") return;
    var s = readLocal();
    if (canAccess(step, s)) return;
    if (step === "workspace" && isSignedIn(s)) {
      window.location.replace(ROUTES.profile);
      return;
    }
    redirectToSignin();
  }

  function routeGuard(step) {
    const s = readLocal();
    if (canAccess(step, s)) return s;
    if (step === "workspace" && isSignedIn(s)) {
      window.location.replace(ROUTES.profile);
      return s;
    }
    redirectToSignin();
    return s;
  }

  async function routeGuardAsync(step) {
    let s = readLocal();
    if (!canAccess(step, s) && global.SourceAPlatformAuth && global.SourceAPlatformAuth.hydratePlatformSession) {
      s = await global.SourceAPlatformAuth.hydratePlatformSession();
    }
    if (canAccess(step, s)) return s;
    if (step === "workspace" && isSignedIn(s)) {
      window.location.replace(ROUTES.profile);
      return s;
    }
    redirectToSignin();
    return s;
  }

  async function forgeApi(body) {
    const base = "http://127.0.0.1:13029";
    const health = await fetch(base + "/health", { cache: "no-store" });
    if (!health.ok) throw new Error("Forge Terminal not running on this Mac");
    const token = (await health.json()).forge_local_token || "";
    const res = await fetch(base + "/api/forge-terminal/v1", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Forge-Token": token,
      },
      body: JSON.stringify(body),
    });
    return res.json();
  }

  async function syncToMac(session) {
    try {
      await forgeApi({ action: "platform_session_save", session: session });
      return true;
    } catch {
      return false;
    }
  }

  async function provisionOnMac(profile) {
    try {
      return await forgeApi({
        action: "provision_user_workspace",
        email: profile.email,
        name: profile.name,
        org: profile.org,
        project_name: profile.project_name,
        slug: profile.workspace_slug,
        profile: profile.profile || "startup",
      });
    } catch (e) {
      return { ok: false, error: String(e.message || e) };
    }
  }

  async function pullFromMac() {
    try {
      const row = await forgeApi({ action: "platform_session_get" });
      if (row.session && row.session.workspace_path) {
        writeLocal(row.session);
      }
      return row;
    } catch {
      return null;
    }
  }

  async function signOut() {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (_) {
      /* quiet */
    }
    if (global.SourceAPlatformAuth && global.SourceAPlatformAuth.signOutSupabase) {
      try {
        await global.SourceAPlatformAuth.signOutSupabase();
      } catch (_) {
        /* quiet */
      }
    }
    if (typeof window !== "undefined") {
      window.location.href = ROUTES.signout;
    }
  }

  function initials(name, email) {
    const n = String(name || email || "?").trim();
    const parts = n.split(/\s+/);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return n.slice(0, 2).toUpperCase();
  }

  global.SourceAPlatformSession = {
    VERSION: VERSION,
    SCHEMA: SCHEMA,
    STEPS: STEPS,
    ROUTES: ROUTES,
    read: readLocal,
    write: writeLocal,
    isSignedIn: isSignedIn,
    canAccess: canAccess,
    signInUrl: signInUrl,
    currentPath: currentPath,
    routeGuard: routeGuard,
    routeGuardAsync: routeGuardAsync,
    bootTier2HeadGuard: bootTier2HeadGuard,
    stepIndex: stepIndex,
    syncToMac: syncToMac,
    provisionOnMac: provisionOnMac,
    pullFromMac: pullFromMac,
    forgeApi: forgeApi,
    signOut: signOut,
    initials: initials,
    establishLocalSession: establishLocalSession,
    mountStepNav: mountStepNav,
  };
})(typeof window !== "undefined" ? window : globalThis);
