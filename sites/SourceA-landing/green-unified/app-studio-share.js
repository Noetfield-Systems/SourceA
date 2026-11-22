/* SourceA App Studio: real opt-in native sharing, with clipboard fallback. No referral ledger. */
(function () {
  "use strict";
  var status = document.getElementById("studio-share-status");
  function setStatus(message) { if (status) status.textContent = message; }
  document.querySelectorAll("[data-studio-share]").forEach(function (button) {
    button.addEventListener("click", async function () {
      var title = button.getAttribute("data-share-title") || "SourceA App Studio";
      var text = button.getAttribute("data-share-text") || "Explore this experience.";
      var url = button.getAttribute("data-share-url");
      if (!url || !/^https:\/\//.test(url)) { setStatus("This share link is unavailable."); return; }
      setStatus("");
      if (typeof navigator.share === "function") {
        try { await navigator.share({title:title,text:text,url:url}); setStatus("Shared — thanks for inviting someone in."); return; }
        catch (error) { if (error && error.name === "AbortError") return; }
      }
      try {
        if (!navigator.clipboard || typeof navigator.clipboard.writeText !== "function") throw Error("clipboard-unavailable");
        await navigator.clipboard.writeText(url);
        setStatus("Link copied. Paste it into a message to invite someone.");
      } catch (_) {
        setStatus("Sharing is unavailable in this browser. Use the Open preview link and copy its address.");
      }
    });
  });
})();
