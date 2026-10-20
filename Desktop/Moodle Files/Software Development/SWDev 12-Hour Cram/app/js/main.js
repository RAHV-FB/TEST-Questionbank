// Boot: read the content, load progress, draw the frame, start routing. Keyboard shortcuts go to the
// shortcuts panel or the current view.
(() => {
  // Enter and Space keep their own meaning on these (a focused mcq radio is not one of them:
  // Enter there checks the answer).
  const NATIVE = "a, button, select, textarea, summary, input:not([type='radio'])";
  // Where focus rests when a page opens, or while a code block is read: Enter there is not an answer.
  const INERT = "h1, pre";

  function onKey(event) {
    if (event.defaultPrevented || CR.dom.isTyping(event)) return;
    if (event.key === "?") {
      CR.shell.toggleShortcuts();
      event.preventDefault();
      return;
    }
    if (event.key === "Escape") {
      CR.shell.closeShortcuts();
      return;
    }
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    if ((event.key === "Enter" || event.key === " ") && event.target.closest?.(NATIVE)) return;
    if (event.key === "Enter" && event.target.closest?.(INERT)) return;
    if (CR.router.onKey(event)) event.preventDefault();
  }

  function boot() {
    try {
      CR.data = CR.indexData(JSON.parse(document.getElementById("cram-data").textContent));
    } catch (error) {
      console.error(error);
      document.getElementById("main").textContent = "The content could not be read. Rebuild the page with build_cram.py.";
      return;
    }
    if (!document.documentElement.lang) document.documentElement.lang = "en";
    CR.store = CR.makeStore();
    CR.store.init();
    CR.store.attach(window, document);
    CR.papers.settle();
    CR.shell.init();
    document.addEventListener("keydown", onKey);
    CR.router.start();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
