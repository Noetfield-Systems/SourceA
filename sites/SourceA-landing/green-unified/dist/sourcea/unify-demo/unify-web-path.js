(function (global) {
  "use strict";
  function cuWebPath() {
    var path = global.location.pathname || "";
    var isDemo = /\/unify-demo(\/|$)/.test(path);
    var isFull = /\/unify(\/|$)/.test(path) && !isDemo;
    var isWeb = isDemo || isFull;
    if (isWeb && global.document && global.document.documentElement) {
      global.document.documentElement.setAttribute("data-cu-web", isDemo ? "demo" : "full");
    }
    return { path: path, isDemo: isDemo, isFull: isFull, isWeb: isWeb };
  }
  global.__cuWebPath = cuWebPath;
  cuWebPath();
})(window);
