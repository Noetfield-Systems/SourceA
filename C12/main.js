/* C12 — minimal interactions for SourceA clone */

(function () {
  const track = document.getElementById("testimonialTrack");
  const dots = document.getElementById("testimonialDots");
  if (!track || !dots) return;

  const cards = Array.from(track.querySelectorAll(".testimonial-card"));
  const dotBtns = Array.from(dots.querySelectorAll("button"));
  let idx = 0;
  let timer;

  function show(i) {
    idx = (i + cards.length) % cards.length;
    cards.forEach((c, j) => c.classList.toggle("active", j === idx));
    dotBtns.forEach((d, j) => d.classList.toggle("active", j === idx));
  }

  dotBtns.forEach((btn, i) => {
    btn.addEventListener("click", () => {
      show(i);
      resetTimer();
    });
  });

  function resetTimer() {
    clearInterval(timer);
    timer = setInterval(() => show(idx + 1), 6000);
  }

  resetTimer();
})();

(function () {
  const toggle = document.getElementById("menuToggle");
  const nav = document.querySelector(".nav");
  if (!toggle || !nav) return;
  toggle.addEventListener("click", () => {
    const open = nav.style.display === "flex";
    nav.style.display = open ? "none" : "flex";
    if (!open) {
      nav.style.flexDirection = "column";
      nav.style.position = "absolute";
      nav.style.top = "72px";
      nav.style.left = "0";
      nav.style.right = "0";
      nav.style.background = "#fff";
      nav.style.padding = "1rem";
      nav.style.borderBottom = "1px solid #e5e8f0";
    }
  });
})();
