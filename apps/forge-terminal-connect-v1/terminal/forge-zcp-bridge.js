(function () {
  "use strict";

  var ZCP_PREFIX = /^(FIX:|CRITIC:|\{[\s\S]*"task_id")/i;

  function zcpHeaders() {
    return {
      "Content-Type": "application/json",
      "X-Forge-Token": sessionStorage.getItem("forge_local_token") || "",
    };
  }

  function zcpApi(body) {
    return fetch(window.location.origin + "/api/zcp/v1", {
      method: "POST",
      headers: zcpHeaders(),
      body: JSON.stringify(body),
    }).then(function (r) {
      return r.json();
    });
  }

  function isZcpMessage(text) {
    var t = (text || "").trim();
    if (!t) return false;
    return ZCP_PREFIX.test(t);
  }

  window.forgeZcpIsMessage = isZcpMessage;

  window.forgeZcpParse = function (text) {
    return zcpApi({ action: "parse", input: text });
  };

  window.forgeZcpIngest = function (text, opts) {
    opts = opts || {};
    return zcpApi({
      action: "ingest",
      input: text,
      plane: opts.plane || "auto",
      dispatch: !!opts.dispatch,
      dry_run: !!opts.dryRun,
      complexity: opts.complexity || "medium",
    });
  };

  window.forgeZcpCritic = function (output) {
    return zcpApi({
      action: "critic",
      output: typeof output === "string" ? output : JSON.stringify(output),
    });
  };

  window.forgeZcpTryIngest = async function (text) {
    if (!isZcpMessage(text)) return false;
    try {
      var row = await window.forgeZcpIngest(text, { plane: "auto", dispatch: false });
      var show =
        (row.for_founder && row.for_founder.show_this) ||
        (row.zcp && row.zcp.mode ? "ZCP " + row.zcp.mode + " · " + (row.plane || "auto") : "ZCP ingested");
      if (typeof window.forgeZcpOnResult === "function") {
        window.forgeZcpOnResult(row);
      }
      if (typeof appendChatBubble === "function") {
        appendChatBubble("assistant", show, "plain");
      }
      if (typeof log === "function") {
        log("zcp " + (row.zcp && row.zcp.mode) + " · " + (row.task_id || ""), row.ok ? "ok" : "err");
      }
      if (typeof setStatus === "function") {
        setStatus(row.ok ? "ZCP " + (row.zcp && row.zcp.mode) : "ZCP failed");
      }
      return true;
    } catch (e) {
      if (typeof log === "function") log("zcp bridge: " + e, "err");
      return false;
    }
  };
})();
