/* artelle.xyz — reveal on scroll, work filters, lightbox */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- reveal on scroll ---- */
  var revealEls = document.querySelectorAll(".reveal");
  if (!reduced && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---- work filters (works page) ---- */
  var chips = document.querySelectorAll(".chip");
  var works = document.querySelectorAll(".work");
  if (chips.length && works.length) {
    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c === chip)); });
        var cat = chip.getAttribute("data-filter");
        works.forEach(function (w) {
          var cats = (w.getAttribute("data-cats") || "").split(/\s+/);
          w.hidden = !(cat === "all" || cats.indexOf(cat) !== -1);
        });
      });
    });
  }

  /* ---- lightbox (any page with .work links) ---- */
  var lb = document.getElementById("lightbox");
  if (!lb || !works.length) return;

  var frame = lb.querySelector(".lb-frame");
  var titleEl = lb.querySelector(".lb-title");
  var metaEl = lb.querySelector(".lb-meta");
  var lastFocus = null;
  var current = -1;

  function visibleWorks() {
    return Array.prototype.filter.call(works, function (w) { return !w.hidden; });
  }

  function openAt(work) {
    var list = visibleWorks();
    current = list.indexOf(work);
    if (current < 0) return;
    var svg = work.querySelector(".plate").innerHTML;
    frame.innerHTML = svg;
    titleEl.textContent = work.getAttribute("data-title") || "";
    metaEl.textContent = work.getAttribute("data-meta") || "";
    lb.classList.add("open");
    lb.querySelector(".lb-x").focus();
    document.documentElement.style.overflow = "hidden";
  }

  function close() {
    lb.classList.remove("open");
    document.documentElement.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }

  function step(dir) {
    var list = visibleWorks();
    if (!list.length) return;
    current = (current + dir + list.length) % list.length;
    var w = list[current];
    frame.innerHTML = w.querySelector(".plate").innerHTML;
    titleEl.textContent = w.getAttribute("data-title") || "";
    metaEl.textContent = w.getAttribute("data-meta") || "";
  }

  Array.prototype.forEach.call(document.querySelectorAll("a.work"), function (link) {
    link.addEventListener("click", function (ev) {
      ev.preventDefault();
      lastFocus = link;
      openAt(link);
    });
  });

  lb.addEventListener("click", function (ev) { if (ev.target === lb) close(); });
  lb.querySelector(".lb-x").addEventListener("click", close);
  lb.querySelector(".lb-prev").addEventListener("click", function () { step(-1); });
  lb.querySelector(".lb-next").addEventListener("click", function () { step(1); });
  document.addEventListener("keydown", function (ev) {
    if (!lb.classList.contains("open")) return;
    if (ev.key === "Escape") close();
    else if (ev.key === "ArrowLeft") step(-1);
    else if (ev.key === "ArrowRight") step(1);
  });
})();
