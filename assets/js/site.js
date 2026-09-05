/* Artelle — progressive enhancement for the static catalog. */
(function () {
  "use strict";
  var year = document.getElementById("yr");
  if (year) year.textContent = new Date().getFullYear();
  var chips = document.querySelectorAll(".chip");
  var works = Array.prototype.slice.call(document.querySelectorAll("a.work"));
  var workCount = document.getElementById("work-count");
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      chips.forEach(function (other) { other.setAttribute("aria-pressed", String(other === chip)); });
      var category = chip.getAttribute("data-filter");
      works.forEach(function (work) { work.hidden = category !== "all" && work.getAttribute("data-cats") !== category; });
      if (workCount) workCount.textContent = visibleWorks().length;
    });
  });
  var search = document.getElementById("catalog-search");
  if (search) {
    var rows = document.querySelectorAll(".catalog-table tbody tr");
    var tableCount = document.getElementById("table-count");
    search.addEventListener("input", function () {
      var query = search.value.trim().toLowerCase();
      var count = 0;
      rows.forEach(function (row) {
        row.hidden = row.getAttribute("data-search").indexOf(query) === -1;
        if (!row.hidden) count++;
      });
      tableCount.textContent = count;
    });
  }
  function visibleWorks() { return works.filter(function (work) { return !work.hidden; }); }
  var lightbox = document.getElementById("lightbox");
  if (!lightbox || !works.length) return;
  var frame = lightbox.querySelector(".lb-frame");
  var title = lightbox.querySelector(".lb-title");
  var meta = lightbox.querySelector(".lb-meta");
  var detail = lightbox.querySelector(".lb-detail");
  var closeButton = lightbox.querySelector(".lb-x");
  var current = -1;
  var lastFocus = null;
  var priorOverflow = "";
  var background = [];
  function render(work) {
    var image = document.createElement("img");
    image.src = work.getAttribute("data-image");
    image.alt = work.querySelector("img").alt;
    frame.replaceChildren(image);
    title.textContent = work.getAttribute("data-title");
    meta.textContent = work.getAttribute("data-meta");
    detail.href = work.href;
    lightbox.setAttribute("aria-label", title.textContent + " — artwork viewer");
  }
  function open(work) {
    current = visibleWorks().indexOf(work);
    if (current < 0) return;
    lastFocus = document.activeElement;
    render(work);
    priorOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = "hidden";
    lightbox.classList.add("open");
    lightbox.setAttribute("aria-hidden", "false");
    background = Array.prototype.map.call(document.querySelectorAll("header, main, footer"), function (element) {
      var previous = element.inert;
      element.inert = true;
      return { element: element, previous: previous };
    });
    closeButton.focus();
  }
  function close() {
    lightbox.classList.remove("open");
    lightbox.setAttribute("aria-hidden", "true");
    document.documentElement.style.overflow = priorOverflow;
    background.forEach(function (item) { item.element.inert = item.previous; });
    if (lastFocus) lastFocus.focus();
  }
  function step(direction) {
    var visible = visibleWorks();
    if (!visible.length) return;
    current = (current + direction + visible.length) % visible.length;
    render(visible[current]);
  }
  works.forEach(function (work) {
    work.addEventListener("click", function (event) {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
      event.preventDefault();
      open(work);
    });
  });
  closeButton.addEventListener("click", close);
  lightbox.querySelector(".lb-prev").addEventListener("click", function () { step(-1); });
  lightbox.querySelector(".lb-next").addEventListener("click", function () { step(1); });
  lightbox.addEventListener("click", function (event) { if (event.target === lightbox) close(); });
  document.addEventListener("keydown", function (event) {
    if (!lightbox.classList.contains("open")) return;
    if (event.key === "Escape") { event.preventDefault(); close(); }
    else if (event.key === "ArrowLeft") { event.preventDefault(); step(-1); }
    else if (event.key === "ArrowRight") { event.preventDefault(); step(1); }
    else if (event.key === "Tab") {
      var focusable = Array.prototype.slice.call(lightbox.querySelectorAll("button, a[href]"));
      var index = focusable.indexOf(document.activeElement);
      if (event.shiftKey && index <= 0) { event.preventDefault(); focusable[focusable.length - 1].focus(); }
      else if (!event.shiftKey && (index === focusable.length - 1 || index === -1)) { event.preventDefault(); focusable[0].focus(); }
    }
  });
})();
