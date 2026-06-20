(function () {
  const btn = document.getElementById("menuBtn");
  const nav = document.getElementById("mainNav");
  if (!btn || !nav) return;
  btn.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    nav.style.display = open ? "flex" : "";
    if (open) {
      nav.style.flexDirection = "column";
      nav.style.position = "absolute";
      nav.style.top = "68px";
      nav.style.left = "0";
      nav.style.right = "0";
      nav.style.background = "#0c1019";
      nav.style.padding = "1rem";
      nav.style.borderBottom = "1px solid #1f2937";
      nav.style.zIndex = "40";
    }
  });
})();
