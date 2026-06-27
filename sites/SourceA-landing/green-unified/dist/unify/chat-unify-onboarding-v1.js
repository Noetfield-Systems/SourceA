(function () {
  "use strict";
  var path = window.location.pathname || "";
  if (/\/unify-demo(\/|$)/.test(path) || (/\/unify(\/|$)/.test(path) && !/\/unify-demo(\/|$)/.test(path))) return;

  var KEY = "chat-unify-onboarding-v4.6";
  if (localStorage.getItem(KEY)) return;

  var overlay = document.createElement("div");
  overlay.className = "cu-onboarding-overlay";
  overlay.innerHTML =
    '<div class="cu-onboarding-card" role="dialog" aria-labelledby="cu-onb-title">' +
    '<p class="cu-onboarding-kicker">Welcome · Chat Unify 4.9.9</p>' +
    '<h2 id="cu-onb-title">Where do you want to start?</h2>' +
    '<p class="cu-onboarding-lead">Paste any AI reply, verify with PASS or BLOCK, and keep receipts in the repository — no Cursor required to begin.</p>' +
    '<div class="cu-onboarding-paths">' +
    '<button type="button" data-path="new"><strong>New to agents</strong><span>Paste in Chat · verify your first reply</span></button>' +
    '<button type="button" data-path="cursor"><strong>Cursor power user</strong><span>Forge a bounded mission · Connect your stack</span></button>' +
    '<button type="button" data-path="founder"><strong>Verify before you act</strong><span>Run Verify &amp; Act on one reply</span></button>' +
    "</div>" +
    '<button type="button" class="cu-onboarding-dismiss">Skip — I know my way</button>' +
    "</div>";
  document.body.appendChild(overlay);

  function dismiss() {
    localStorage.setItem(KEY, "1");
    overlay.remove();
  }
  function go(tab) {
    dismiss();
    var btn = document.querySelector('[data-tab="' + tab + '"]');
    if (btn) btn.click();
  }
  overlay.querySelector(".cu-onboarding-dismiss").addEventListener("click", dismiss);
  overlay.querySelector('[data-path="founder"]').addEventListener("click", function () {
    go("founder");
  });
  overlay.querySelector('[data-path="cursor"]').addEventListener("click", function () {
    go("forge");
  });
  overlay.querySelector('[data-path="new"]').addEventListener("click", function () {
    go("home");
  });
})();
