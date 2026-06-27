/** Pure Flow site config — client URLs (Pages + API Worker) */
(function () {
  var host = window.location.hostname || "";
  var onPages = host.indexOf("pages.dev") !== -1;
  var origin = onPages ? "https://pureflow-pool.pages.dev" : "https://pureflow.sourcea.app";
  var seg = (window.location.pathname || "").split("/").filter(Boolean)[0];
  var locale = ["en", "fr", "fa", "zh"].indexOf(seg) !== -1 ? seg : "en";
  var apiOrigin = onPages ? "https://pureflow.sourcea.app" : "";

  window.PUREFLOW_CONFIG = {
    siteUrl: origin + "/" + locale + "/",
    locale: locale,
    phone: "(604) 555-0123",
    phoneTel: "+16045550123",
    email: "hello@pureflow.sourcea.app",
    quoteApi: apiOrigin + "/api/quote",
    responseHours: 4,
    foundingSpotsLeft: 25,
  };
})();
