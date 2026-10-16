// The frame around every view: the module rail, current-page marks in both navs, the header
// countdown, the note about a paper in progress, the footer status line, the theme switch and the
// shortcuts panel.
SD.shell = (() => {
  const { h } = SD.dom;
  const THEMES = [null, "light", "dark"];
  // The places the phone tab bar names; every other page counts as "More".
  const TAB_PLACES = new Set(["home", "learn", "practice", "exam"]);
  const SAVE_TEXT = {
    synced: "Progress synced",
    large: "Progress saved on this device (too large to sync)",
  };
  let railModule = null;
  let route = null; // the parsed current route
  let shortcutsReturn = null; // {focus, scroll}: where to go back to when the panel closes

  const byId = (id) => document.getElementById(id);
  const rail = () => byId("rail");

  function renderRail(toActive = false) {
    const keep = rail().scrollTop;
    const lists = SD.ui.moduleGroups().map(([code, mods]) =>
      h(
        "div",
        { class: "rail-group" },
        h("p", { class: "label rail-label", text: SD.ui.groupLabel(code) }),
        h(
          "ul",
          {},
          mods.map((mod) => {
            const st = SD.stats.module(mod.id);
            const current = mod.id === railModule;
            const detail = st.status === "fail" ? `${st.fail} failing` : `${st.pass}/${st.total}`;
            const sub = [
              current ? SD.ui.dots(st.sections.map((s) => s.status)) : null,
              mod.predicted ? SD.ui.chip("predicted", "warn") : null,
            ].filter(Boolean);
            return h(
              "li",
              {},
              h(
                "a",
                {
                  class: "rail-item",
                  href: SD.route.href("learn", mod.id),
                  title: mod.title,
                  "aria-current": current ? "page" : null,
                },
                h(
                  "span",
                  { class: "rail-row" },
                  SD.ui.statusMark(st.status),
                  h("span", { class: "rail-title", text: mod.title }),
                  h("span", { class: "rail-count", text: detail }),
                ),
                sub.length ? h("span", { class: "rail-sub" }, sub) : null,
              ),
            );
          }),
        ),
      ),
    );
    rail().replaceChildren(...lists);
    rail().scrollTop = keep;
    if (toActive) rail().querySelector("[aria-current='page']")?.scrollIntoView({ block: "nearest" });
  }

  function markNav(nav) {
    document.querySelectorAll("[data-nav]").forEach((a) => {
      const place = a.closest(".tabbar") && !TAB_PLACES.has(nav) ? "more" : nav;
      if (a.dataset.nav === place) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }

  function paintCountdown() {
    const exam = SD.stats.exam();
    const el = byId("countdown");
    if (exam.state === "before") {
      el.replaceChildren(
        h("span", { class: "count", text: exam.text }),
        h("span", { class: "countdown-rest", text: " to the mid-term" }),
      );
    } else {
      el.textContent = exam.text;
    }
  }

  // A paper that is running: a note in the header on every other page, and on the paper itself
  // the page drops its navigation, so the sitting looks like the paper it stands for.
  function paintSitting() {
    const live = SD.exam.running(SD.store.get().exams);
    const here = route && route.view === "exam" && route.args[0] === "attempt" && live && route.args[1] === live.id;
    document.documentElement.classList.toggle("is-sitting", Boolean(here));
    const chip = byId("sitting-chip");
    chip.hidden = !live || Boolean(here);
    if (live) {
      const left = SD.util.countdown(SD.exam.timeLeft(live, Date.now()));
      chip.href = SD.route.href("exam", "attempt", live.id);
      chip.textContent = `${live.title} in progress · ${left} left`;
    }
    // The note is a sticky bar under the header: keep focused fields and jump targets clear of it.
    // (On the paper itself the exam bar owns this value.)
    const page = document.documentElement.style;
    if (!chip.hidden) page.setProperty("--sticky-extra", `${chip.offsetHeight}px`);
    else if (!here) page.removeProperty("--sticky-extra");
  }

  function applyTheme(theme) {
    if (theme) document.documentElement.dataset.theme = theme;
    else delete document.documentElement.dataset.theme;
    byId("theme-toggle").textContent = `Theme: ${theme || "system"}`;
  }

  function paintSaveStatus(cloud) {
    let text = "Progress saved on this device";
    if (SAVE_TEXT[cloud]) text = SAVE_TEXT[cloud];
    else if (SD.store.storageMode() !== "local") {
      text = "Progress is not being saved: this browser blocks storage";
    }
    byId("save-status").textContent = text;
  }

  // Open or close the shortcuts list. It sits above the page, so opening scrolls up to it;
  // closing puts focus and the scroll position back where they were.
  function setShortcuts(open) {
    const panel = byId("shortcuts");
    const wasOpen = !panel.hidden;
    if (open === wasOpen) return false;
    panel.hidden = !open;
    for (const opener of document.querySelectorAll("[aria-controls='shortcuts']")) {
      opener.setAttribute("aria-expanded", String(open));
    }
    if (open) {
      shortcutsReturn = { focus: document.activeElement, scroll: window.scrollY };
      byId("shortcuts-close").focus();
    } else if (shortcutsReturn) {
      window.scrollTo(0, shortcutsReturn.scroll);
      shortcutsReturn.focus?.focus?.({ preventScroll: true });
      shortcutsReturn = null;
    }
    return true;
  }

  function init() {
    const meta = SD.data.meta;
    applyTheme(SD.store.get().prefs.theme);
    byId("theme-toggle").addEventListener("click", () => {
      const now = SD.store.get().prefs.theme;
      const next = THEMES[(THEMES.indexOf(now) + 1) % THEMES.length];
      SD.store.setPref("theme", next);
      applyTheme(next);
    });
    byId("build-info").textContent =
      `Built ${SD.util.dateTimeLabel(Date.parse(meta.built))}` + (meta.fixture ? " from test data" : "");
    byId("shortcuts-open").addEventListener("click", () => setShortcuts(true));
    byId("shortcuts-close").addEventListener("click", () => setShortcuts(false));
    byId("skip").addEventListener("click", () => {
      const target = byId("main").querySelector("h1") || byId("main");
      target.focus();
    });
    renderRail();
    SD.store.subscribe((state, kind) => {
      if (kind === "q" || kind === "all") renderRail();
      if (kind === "exams" || kind === "all") paintSitting();
      if (kind === "all") applyTheme(state.prefs.theme);
    });
    SD.router.onChange((parsed, nav) => {
      route = parsed;
      markNav(nav);
      railModule = parsed.view === "learn" ? parsed.args[0] || null : null;
      renderRail(true);
      paintSitting();
    });
    paintCountdown();
    // Every half minute: the countdown, and a sitting whose time ran out while no one looked.
    window.setInterval(() => {
      SD.examPaper.settle();
      paintCountdown();
      paintSitting();
    }, 30 * 1000);
    SD.sync.onStatus(paintSaveStatus);
  }

  return {
    init,
    toggleShortcuts: () => setShortcuts(byId("shortcuts").hidden),
    closeShortcuts: () => setShortcuts(false),
  };
})();
