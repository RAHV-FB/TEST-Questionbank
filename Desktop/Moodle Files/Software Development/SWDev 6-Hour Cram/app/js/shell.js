// The frame: the exam countdown, the nav marks, the note about a paper in progress, the footer
// (saving, shortcuts, theme) and the skip link.
CR.shell = (() => {
  const THEMES = ["system", "light", "dark"];
  const THEME_LABEL = { system: "system", light: "light", dark: "dark" };

  const examStart = () => Date.parse(CR.data.meta.exam.date);

  function paintCountdown() {
    const el = document.getElementById("countdown");
    if (!el) return;
    const now = Date.now();
    const start = examStart();
    const end = start + CR.data.meta.exam.minutes * CR.util.MINUTE;
    if (now < start) {
      el.replaceChildren("Mid-term in ", Object.assign(document.createElement("span"), { className: "count", textContent: CR.util.countdown(start - now) }));
    } else {
      el.textContent = now < end ? "The mid-term is in progress" : "The mid-term is over";
    }
    el.title = `${CR.util.dateTimeLabel(start, CR.util.EXAM_TZ)} (Madrid), room ${CR.data.meta.exam.room}`;
  }

  // A paper in progress, on every other page: its name and the time left, as a link back.
  function paintSitting() {
    const chip = document.getElementById("sitting-chip");
    if (!chip) return;
    const running = CR.paper.running(CR.store.get().papers);
    const here = CR.router.current();
    if (!running || (here && here.view === "sit" && here.args[0] === running.id)) {
      chip.hidden = true;
      return;
    }
    chip.hidden = false;
    chip.href = CR.route.href("sit", running.id);
    chip.textContent = `${running.title} is running: ${CR.util.clock(CR.paper.timeLeft(running, Date.now()))} left. Go back to the paper.`;
  }

  function paintMistakes() {
    const n = CR.mistakes.queue(CR.store.get().q, CR.data.knownIds).length;
    for (const el of document.querySelectorAll("[data-mistakes-count]")) {
      el.textContent = n > 0 ? String(n) : "";
      el.hidden = n === 0;
    }
  }

  function paintSave() {
    const el = document.getElementById("save-status");
    if (!el) return;
    el.textContent = CR.store.storageMode() === "local" ? "Progress is saved on this device." : "Progress is not being saved: storage is blocked. It lasts until you close this page.";
  }

  function markNav(name) {
    for (const a of document.querySelectorAll("[data-nav]")) {
      if (a.dataset.nav === name) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    }
  }

  function applyTheme(theme) {
    if (theme === "light" || theme === "dark") document.documentElement.dataset.theme = theme;
    else delete document.documentElement.dataset.theme;
    const button = document.getElementById("theme-toggle");
    if (button) button.textContent = `Theme: ${THEME_LABEL[theme]}`;
  }

  function toggleShortcuts(force) {
    const panel = document.getElementById("shortcuts");
    const opener = document.getElementById("shortcuts-open");
    if (!panel) return;
    const show = typeof force === "boolean" ? force : panel.hidden;
    panel.hidden = !show;
    if (opener) opener.setAttribute("aria-expanded", String(show));
    if (show) panel.querySelector("h2")?.focus();
  }

  function init() {
    const meta = document.getElementById("build-info");
    if (meta) meta.textContent = `Built ${CR.data.meta.built.slice(0, 16).replace("T", " ")}${CR.data.meta.mode !== "full" ? ` (${CR.data.meta.mode} build)` : ""}`;
    const theme = CR.store.get().prefs.theme || "system";
    applyTheme(theme);
    document.getElementById("theme-toggle")?.addEventListener("click", () => {
      const now = CR.store.get().prefs.theme || "system";
      const next = THEMES[(THEMES.indexOf(now) + 1) % THEMES.length];
      CR.store.setPref("theme", next === "system" ? null : next);
      applyTheme(next);
    });
    document.getElementById("shortcuts-open")?.addEventListener("click", () => toggleShortcuts());
    document.getElementById("shortcuts-close")?.addEventListener("click", () => toggleShortcuts(false));
    document.getElementById("skip")?.addEventListener("click", () => CR.dom.reveal(document.getElementById("main")));
    CR.router.onChange((_route, nav) => {
      markNav(nav);
      paintSitting();
      paintSave();
    });
    CR.store.subscribe((_, kind) => {
      if (kind === "q" || kind === "all") paintMistakes();
      if (kind === "papers" || kind === "all") paintSitting();
    });
    paintCountdown();
    paintMistakes();
    paintSave();
    window.setInterval(() => {
      paintCountdown();
      if (CR.papers.settle()) paintMistakes();
      paintSitting();
    }, 1000);
  }

  return { init, toggleShortcuts, closeShortcuts: () => toggleShortcuts(false) };
})();
