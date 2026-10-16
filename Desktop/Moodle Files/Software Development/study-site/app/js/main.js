// Boot: read the content, load progress, draw the frame, start routing, then (without waiting)
// try the optional cloud sync. Keyboard shortcuts go to the shortcuts panel or the current view.
(() => {
  // Enter and Space keep their own meaning on these (a focused mcq radio is not one of them:
  // Enter there checks the answer).
  const NATIVE = "a, button, select, textarea, summary, input:not([type='radio'])";
  // Where focus rests when a page opens, or while a code block is read: Enter there is not an answer.
  const INERT = "h1, pre";

  function onKey(event) {
    if (event.defaultPrevented || SD.dom.isTyping(event)) return;
    if (event.key === "?") {
      SD.shell.toggleShortcuts();
      event.preventDefault();
      return;
    }
    if (event.key === "Escape") {
      SD.shell.closeShortcuts();
      return;
    }
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    if ((event.key === "Enter" || event.key === " ") && event.target.closest?.(NATIVE)) return;
    if (event.key === "Enter" && event.target.closest?.(INERT)) return;
    if (SD.router.onKey(event)) event.preventDefault();
  }

  function boot() {
    try {
      SD.data = SD.readContent();
    } catch (error) {
      console.error(error);
      document.getElementById("main").textContent =
        "The study content could not be read. Rebuild the page with tools/build.py.";
      return;
    }
    if (!document.documentElement.lang) document.documentElement.lang = "en";
    SD.store.init();
    SD.store.attach(window, document);
    SD.examPaper.settle();
    SD.shell.init();
    document.addEventListener("keydown", onKey);
    SD.router.start();
    window.setTimeout(SD.sync.start, 0);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
