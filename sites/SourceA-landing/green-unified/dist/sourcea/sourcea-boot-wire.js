/**
 * sourcea-boot site wire — ensure eval/GitHub links resolve from trust-signals.json
 * on every page that includes this script.
 */
(function () {
  const EVAL = "/eval";
  const DEFAULT_REPO = "https://github.com/sourcea-io/sourcea-boot";

  function ensureGithubLinks(url) {
    document.querySelectorAll("[data-trust-github-link]").forEach((a) => {
      if (url) a.href = url;
      if (!a.getAttribute("href")) a.href = DEFAULT_REPO;
    });
  }

  function ensureEvalLinks() {
    document.querySelectorAll("[data-sa-boot-eval]").forEach((el) => {
      if (!el.querySelector('a[href="/eval"]')) {
        const a = document.createElement("a");
        a.href = EVAL;
        a.textContent = "sourcea-boot eval";
        el.appendChild(a);
      }
    });
  }

  fetch("/sourcea/data/trust-signals.json", { cache: "no-store" })
    .then((r) => (r.ok ? r.json() : null))
    .then((data) => {
      ensureGithubLinks(data && data.github && data.github.url);
      ensureEvalLinks();
    })
    .catch(() => {
      ensureGithubLinks(DEFAULT_REPO);
      ensureEvalLinks();
    });

  fetch("/sourcea/data/phase1-proof-pack-public-v1.json", { cache: "no-store" })
    .then((r) => {
      if (!r.ok) throw new Error("proof fetch");
      const ct = (r.headers.get("content-type") || "").toLowerCase();
      if (ct.includes("text/html")) throw new Error("html not json");
      return r.json();
    })
    .then((proof) => {
      if (!proof) return;
      if (window.SourceAPublicDisplay) {
        window.SourceAPublicDisplay.paintPhase0Proof(proof);
      } else if (window.SourceASiteFallback) {
        window.SourceASiteFallback.paintProof(proof);
      }
      if (window.SourceASiteFallback) window.SourceASiteFallback.paintReceiptCard(document);
    })
    .catch(() => {
      if (window.SourceASiteFallback) {
        window.SourceASiteFallback.paintProof(window.SourceASiteFallback.PROOF);
        window.SourceASiteFallback.paintReceiptCard(document);
      }
    });
})();
