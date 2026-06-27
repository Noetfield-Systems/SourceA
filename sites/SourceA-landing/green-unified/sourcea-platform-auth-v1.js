/**
 * SourceA Platform auth — Supabase (Google · GitHub · email · magic link).
 * Public config: /sourcea/data/sourcea-platform-auth-config-v1.json
 */
(function (global) {
  "use strict";

  const AUTH_VERSION = "1.4.0";
  const CONFIG_URL = "/sourcea/data/sourcea-platform-auth-config-v1.json";
  const SUPABASE_CDN = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js";

  let config = null;
  let client = null;

  function $(id) {
    return document.getElementById(id);
  }

  function showStatus(el, text, kind) {
    if (!el) return;
    el.textContent = text || "";
    el.hidden = !text;
    el.classList.toggle("is-error", kind === "error");
    el.classList.toggle("is-ok", kind === "ok");
  }

  function friendlyAuthError(err) {
    const msg = String((err && (err.message || err.error_description || err.msg)) || err || "");
    if (/redirect_uri|redirect url/i.test(msg)) {
      return "OAuth redirect mismatch — add this page URL in Supabase → Authentication → URL configuration.";
    }
    if (/provider is not enabled/i.test(msg)) {
      return "That sign-in provider is not enabled yet in Supabase → Authentication → Providers.";
    }
    if (/invalid login credentials/i.test(msg)) {
      return "Email or password is wrong — try again or use Google/GitHub.";
    }
    if (/email not confirmed/i.test(msg)) {
      return "Confirm your email first — check your inbox, then sign in.";
    }
    return msg || "Sign-in failed";
  }

  function redirectUrl() {
    const path = global.location.pathname || "";
    if (path.indexOf("/signup") !== -1 || path.indexOf("/signin") !== -1) {
      return global.location.origin + path;
    }
    const fallback =
      (config && config.redirect_path) ||
      (global.SourceAPlatformSession && global.SourceAPlatformSession.ROUTES.signin) ||
      "/sourcea/forge/terminal/signin";
    return global.location.origin + fallback;
  }

  function sessionFromUser(user) {
    const meta = user.user_metadata || {};
    const name =
      meta.full_name ||
      meta.name ||
      (meta.given_name && meta.family_name ? meta.given_name + " " + meta.family_name : "") ||
      (user.email ? user.email.split("@")[0] : "Founder");
    return {
      email: user.email || "",
      name: name,
      signed_in_at: new Date().toISOString(),
      auth_provider: (user.app_metadata && user.app_metadata.provider) || "email",
      supabase_user_id: user.id,
      step: "profile",
    };
  }

  function applyUserToSession(user) {
    const S = global.SourceAPlatformSession;
    if (!S || !user) return S ? S.read() : {};
    const merged = S.write(Object.assign({}, S.read(), sessionFromUser(user)));
    S.syncToMac(merged);
    return merged;
  }

  function routeAfterSignIn(merged) {
    const S = global.SourceAPlatformSession;
    if (!S) return;
    const R = S.ROUTES;
    if (merged.project_name) {
      global.location.href = R.workspace;
      return;
    }
    global.location.href = R.profile;
  }

  function afterAuth(user) {
    routeAfterSignIn(applyUserToSession(user));
  }

  function clearAuthParamsFromUrl() {
    const u = new URL(global.location.href);
    ["code", "error", "error_code", "error_description"].forEach(function (k) {
      u.searchParams.delete(k);
    });
    const clean = u.pathname + (u.searchParams.toString() ? "?" + u.searchParams.toString() : "");
    global.history.replaceState(null, "", clean + u.hash.replace(/access_token=[^&]+&?|refresh_token=[^&]+&?|type=[^&]+&?/g, "").replace(/^#$/, ""));
    if (global.location.hash && (global.location.hash.includes("access_token") || global.location.hash.includes("error"))) {
      global.history.replaceState(null, "", u.pathname + u.search);
    }
  }

  function parseUrlAuthError() {
    const params = new URLSearchParams(global.location.search || "");
    const hash = global.location.hash || "";
    const err =
      params.get("error_description") ||
      params.get("error") ||
      (hash.match(/error_description=([^&]+)/) || [])[1];
    if (!err) return "";
    try {
      return decodeURIComponent(String(err).replace(/\+/g, " "));
    } catch (_) {
      return String(err);
    }
  }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (global.supabase && global.supabase.createClient) {
        resolve();
        return;
      }
      const s = document.createElement("script");
      s.src = src;
      s.async = true;
      s.onload = function () {
        resolve();
      };
      s.onerror = function () {
        reject(new Error("Failed to load Supabase client"));
      };
      document.head.appendChild(s);
    });
  }

  async function loadConfig() {
    if (config) return config;
    const res = await fetch(CONFIG_URL, { cache: "no-store" });
    if (!res.ok) throw new Error("Auth config missing");
    config = await res.json();
    return config;
  }

  async function getClient() {
    if (client) return client;
    const cfg = await loadConfig();
    if (!cfg.configured || !cfg.supabase_url || !cfg.supabase_anon_key) {
      throw new Error("Sign-in is not configured yet — try the public demo or Start your Forge project.");
    }
    await loadScript(SUPABASE_CDN);
    if (!global.supabase || !global.supabase.createClient) {
      throw new Error("Supabase client unavailable");
    }
    client = global.supabase.createClient(cfg.supabase_url, cfg.supabase_anon_key, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
        flowType: "pkce",
      },
    });
    return client;
  }

  async function consumeOAuthCallback(sb) {
    const params = new URLSearchParams(global.location.search || "");
    const code = params.get("code");
    const urlErr = parseUrlAuthError();
    if (urlErr) throw new Error(friendlyAuthError(urlErr));

    if (code) {
      const row = await sb.auth.exchangeCodeForSession(code);
      if (row.error) throw row.error;
      clearAuthParamsFromUrl();
      return row.data && row.data.session;
    }

    const hash = global.location.hash || "";
    if (hash.includes("access_token") || hash.includes("type=recovery")) {
      const row = await sb.auth.getSession();
      clearAuthParamsFromUrl();
      return row.data && row.data.session;
    }
    return null;
  }

  async function hydratePlatformSession() {
    const S = global.SourceAPlatformSession;
    if (!S) return {};
    let cur = S.read();
    if (S.isSignedIn(cur)) return cur;
    try {
      const sb = await getClient();
      await consumeOAuthCallback(sb);
      const row = await sb.auth.getSession();
      if (row.data && row.data.session && row.data.session.user) {
        cur = applyUserToSession(row.data.session.user);
      }
    } catch (e) {
      const status = $("sa-po-auth-status");
      if (status) showStatus(status, friendlyAuthError(e), "error");
    }
    return cur;
  }

  function wireAuthStateListener() {
    getClient()
      .then(function (sb) {
        sb.auth.onAuthStateChange(function (event, session) {
          if ((event === "SIGNED_IN" || event === "TOKEN_REFRESHED") && session && session.user) {
            const S = global.SourceAPlatformSession;
            const path = global.location.pathname || "";
            if (S && (path.indexOf("signin") !== -1 || path.indexOf("signup") !== -1)) {
              afterAuth(session.user);
            }
          }
        });
      })
      .catch(function () {
        /* unconfigured */
      });
  }

  async function signOutSupabase() {
    try {
      const sb = await getClient();
      await sb.auth.signOut();
    } catch (_) {
      /* quiet */
    }
    client = null;
  }

  async function handleOAuthReturn() {
    const merged = await hydratePlatformSession();
    const S = global.SourceAPlatformSession;
    const path = global.location.pathname || "";
    if (S && S.isSignedIn(merged) && (path.indexOf("signin") !== -1 || path.indexOf("signup") !== -1)) {
      routeAfterSignIn(merged);
    }
  }

  async function signInWithPassword(email, password) {
    const sb = await getClient();
    const row = await sb.auth.signInWithPassword({ email: email, password: password });
    if (row.error) throw row.error;
    if (!row.data || !row.data.user) throw new Error("Sign in failed");
    afterAuth(row.data.user);
  }

  async function signInWithMagicLink(email) {
    const sb = await getClient();
    const row = await sb.auth.signInWithOtp({
      email: email,
      options: { emailRedirectTo: redirectUrl(), shouldCreateUser: true },
    });
    if (row.error) throw row.error;
    return { sent: true };
  }

  async function sendPasswordReset(email) {
    const sb = await getClient();
    const row = await sb.auth.resetPasswordForEmail(email, { redirectTo: redirectUrl() });
    if (row.error) throw row.error;
    return { sent: true };
  }

  async function signUpWithPassword(email, password, name) {
    const sb = await getClient();
    const row = await sb.auth.signUp({
      email: email,
      password: password,
      options: {
        data: { full_name: name, name: name },
        emailRedirectTo: redirectUrl(),
      },
    });
    if (row.error) throw row.error;
    if (row.data && row.data.user && row.data.session) {
      afterAuth(row.data.user);
      return;
    }
    return { needsEmailConfirm: true };
  }

  async function signInWithOAuth(provider) {
    const sb = await getClient();
    const row = await sb.auth.signInWithOAuth({
      provider: provider,
      options: {
        redirectTo: redirectUrl(),
        skipBrowserRedirect: false,
      },
    });
    if (row.error) throw row.error;
  }

  function paintSupabaseUI(cfg) {
    const banner = $("sa-po-supabase-banner");
    const oauth = $("sa-po-supabase-oauth");
    const divider = $("sa-po-email-divider");
    const form = $("sa-po-signin-form") || $("sa-po-signup-form");
    const providers = (cfg && cfg.oauth_providers) || ["google", "github"];
    const google = $("sa-po-google");
    const github = $("sa-po-github");
    if (google) google.hidden = providers.indexOf("google") === -1;
    if (github) github.hidden = providers.indexOf("github") === -1;

    if (cfg && cfg.configured) {
      if (banner) {
        banner.hidden = false;
        banner.classList.remove("is-off");
        const text = $("sa-po-supabase-banner-text");
        if (text) {
          text.innerHTML =
            "<strong>Supabase auth</strong> — Google, GitHub, email, or magic link";
        }
      }
      return;
    }
    if (banner) {
      banner.hidden = false;
      banner.classList.add("is-off");
      const text = $("sa-po-supabase-banner-text");
      if (text) {
        text.innerHTML =
          "<strong>Supabase auth</strong> is wiring up — use Start your Forge project below or the public demo.";
      }
    }
    if (oauth) oauth.hidden = true;
    if (divider) divider.hidden = true;
    if (form) form.hidden = true;
  }

  function bindLocalForgeStart() {
    const status = $("sa-po-auth-status");
    const btn = $("sa-ft-local-start");
    if (!btn) return;
    btn.addEventListener("click", function () {
      const S = global.SourceAPlatformSession;
      const email = ($("sa-ft-local-email") || {}).value.trim();
      const name = ($("sa-ft-local-name") || {}).value.trim();
      if (!email) {
        showStatus(status, "Email is required to start your Forge project.", "error");
        return;
      }
      showStatus(status, "Starting your project…", "ok");
      try {
        const merged = S.establishLocalSession(email, name);
        S.syncToMac(merged);
        routeAfterSignIn(merged);
      } catch (e) {
        showStatus(status, String(e.message || e), "error");
      }
    });
  }

  function bindMagicLinkAndReset() {
    const status = $("sa-po-auth-status");
    const magicBtn = $("sa-po-magic-link");
    const resetBtn = $("sa-po-forgot-password");
    if (magicBtn) {
      magicBtn.addEventListener("click", function (ev) {
        ev.preventDefault();
        const email = ($("sa-po-email") || {}).value.trim();
        if (!email) {
          showStatus(status, "Enter your email above first.", "error");
          return;
        }
        showStatus(status, "Sending magic link…", "ok");
        signInWithMagicLink(email)
          .then(function () {
            showStatus(status, "Check your email — click the link to sign in.", "ok");
          })
          .catch(function (e) {
            showStatus(status, friendlyAuthError(e), "error");
          });
      });
    }
    if (resetBtn) {
      resetBtn.addEventListener("click", function (ev) {
        ev.preventDefault();
        const email = ($("sa-po-email") || {}).value.trim();
        if (!email) {
          showStatus(status, "Enter your email above first.", "error");
          return;
        }
        showStatus(status, "Sending reset link…", "ok");
        sendPasswordReset(email)
          .then(function () {
            showStatus(status, "Password reset email sent — check your inbox.", "ok");
          })
          .catch(function (e) {
            showStatus(status, friendlyAuthError(e), "error");
          });
      });
    }
  }

  function bindSignIn() {
    const status = $("sa-po-auth-status");
    const form = $("sa-po-signin-form");
    const google = $("sa-po-google");
    const github = $("sa-po-github");

    loadConfig()
      .then(function (cfg) {
        paintSupabaseUI(cfg);
        const urlErr = parseUrlAuthError();
        if (urlErr) showStatus(status, friendlyAuthError(urlErr), "error");
        if (!cfg.configured) {
          showStatus(
            status,
            "Password & OAuth sign-in is wiring up — use Start your Forge project below or the public demo.",
            "error",
          );
          if (google) google.disabled = true;
          if (github) github.disabled = true;
          return;
        }
        wireAuthStateListener();
        return handleOAuthReturn();
      })
      .catch(function (e) {
        showStatus(status, friendlyAuthError(e), "error");
      });

    if (google) {
      google.addEventListener("click", function () {
        showStatus(status, "Redirecting to Google…", "ok");
        signInWithOAuth("google").catch(function (e) {
          showStatus(status, friendlyAuthError(e), "error");
        });
      });
    }
    if (github) {
      github.addEventListener("click", function () {
        showStatus(status, "Redirecting to GitHub…", "ok");
        signInWithOAuth("github").catch(function (e) {
          showStatus(status, friendlyAuthError(e), "error");
        });
      });
    }

    if (form) {
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        const email = ($("sa-po-email") || {}).value.trim();
        const password = ($("sa-po-password") || {}).value || "";
        if (!email || !password) return;
        showStatus(status, "Signing in…", "ok");
        signInWithPassword(email, password).catch(function (e) {
          showStatus(status, friendlyAuthError(e), "error");
        });
      });
    }
    bindMagicLinkAndReset();
  }

  function bindSignUp() {
    const status = $("sa-po-auth-status");
    const form = $("sa-po-signup-form");
    const google = $("sa-po-google");
    const github = $("sa-po-github");

    loadConfig()
      .then(function (cfg) {
        paintSupabaseUI(cfg);
        const urlErr = parseUrlAuthError();
        if (urlErr) showStatus(status, friendlyAuthError(urlErr), "error");
        if (!cfg.configured) {
          showStatus(
            status,
            "Supabase account creation is wiring up — try the public demo or start from sign in.",
            "error",
          );
          if (google) google.disabled = true;
          if (github) github.disabled = true;
          return;
        }
        wireAuthStateListener();
        return handleOAuthReturn();
      })
      .catch(function (e) {
        showStatus(status, friendlyAuthError(e), "error");
      });

    if (google) {
      google.addEventListener("click", function () {
        showStatus(status, "Redirecting to Google…", "ok");
        signInWithOAuth("google").catch(function (e) {
          showStatus(status, friendlyAuthError(e), "error");
        });
      });
    }
    if (github) {
      github.addEventListener("click", function () {
        showStatus(status, "Redirecting to GitHub…", "ok");
        signInWithOAuth("github").catch(function (e) {
          showStatus(status, friendlyAuthError(e), "error");
        });
      });
    }

    if (form) {
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        const name = ($("sa-po-name") || {}).value.trim();
        const email = ($("sa-po-email") || {}).value.trim();
        const password = ($("sa-po-password") || {}).value || "";
        const confirm = ($("sa-po-password-confirm") || {}).value || "";
        if (!name || !email || !password) return;
        if (password.length < 8) {
          showStatus(status, "Password must be at least 8 characters.", "error");
          return;
        }
        if (password !== confirm) {
          showStatus(status, "Passwords do not match.", "error");
          return;
        }
        showStatus(status, "Creating your account…", "ok");
        signUpWithPassword(email, password, name)
          .then(function (row) {
            if (row && row.needsEmailConfirm) {
              showStatus(
                status,
                "Check your email to confirm your account — then sign in.",
                "ok",
              );
              return;
            }
          })
          .catch(function (e) {
            showStatus(status, friendlyAuthError(e), "error");
          });
      });
    }
  }

  async function bootSignUpPage() {
    const S = global.SourceAPlatformSession;
    const merged = await hydratePlatformSession();
    if (S && S.isSignedIn(merged)) {
      routeAfterSignIn(merged);
      return;
    }
    bindSignUp();
  }

  async function bootSignInPage() {
    const S = global.SourceAPlatformSession;
    const merged = await hydratePlatformSession();
    if (S && S.isSignedIn(merged)) {
      routeAfterSignIn(merged);
      return;
    }
    bindSignIn();
    bindLocalForgeStart();
  }

  global.SourceAPlatformAuth = {
    VERSION: AUTH_VERSION,
    loadConfig: loadConfig,
    getClient: getClient,
    bindSignIn: bindSignIn,
    bindSignUp: bindSignUp,
    afterAuth: afterAuth,
    hydratePlatformSession: hydratePlatformSession,
    signOutSupabase: signOutSupabase,
    bootSignInPage: bootSignInPage,
    bootSignUpPage: bootSignUpPage,
    friendlyAuthError: friendlyAuthError,
  };
})(typeof window !== "undefined" ? window : globalThis);
