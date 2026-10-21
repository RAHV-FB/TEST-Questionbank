// Hash router. Views register a render function; the router owns #main, the document title, focus
// and scroll, and remembers the route in memory in case the hash cannot be written.
CR.router = (() => {
  const BASE_TITLE = "SWDev 6-Hour Cram";
  const views = new Map();
  const listeners = new Set();
  let current = null; // {view, args, route}
  let active = {}; // what the current view's render returned
  let memoryRoute = "home";
  let scrollTimer = null;

  // Each history entry remembers where its page was scrolled to (in history.state), so Back and
  // Forward return to that place; a link opens a page at the top. Where the viewer does not allow
  // history.state, every page opens at the top.
  function rememberScroll() {
    try {
      const state = window.history.state;
      const base = state !== null && typeof state === "object" ? state : {};
      window.history.replaceState({ ...base, scroll: window.scrollY }, "");
    } catch {
      // nothing to do: pages simply open at the top
    }
  }

  function savedScroll() {
    try {
      const y = window.history.state?.scroll;
      return Number.isFinite(y) ? y : null;
    } catch {
      return null;
    }
  }

  // view: {render(ctx), nav?: name of the nav item to mark current (defaults to the route name)}.
  // render receives {args, route, root} and may return {title, onKey, cleanup}.
  function register(name, view) {
    if (!/^[A-Za-z0-9_~-]+$/.test(name)) throw new TypeError(`bad route name ${name}`);
    if (views.has(name)) throw new Error(`route "${name}" is already registered`);
    views.set(name, view);
  }

  function readHash() {
    try {
      return window.location.hash;
    } catch {
      return "#" + memoryRoute;
    }
  }

  // go("type.S3") or go("#type.S3"). Writes the hash (so back/forward work) and renders.
  function go(target) {
    const parsed = CR.route.parse(target);
    if (!parsed) return;
    rememberScroll();
    memoryRoute = parsed.route;
    let moved = false;
    try {
      if (window.location.hash.slice(1) !== parsed.route) {
        window.location.hash = parsed.route;
        moved = true;
      }
    } catch {
      moved = false;
    }
    if (!moved) render(parsed.route);
  }

  function page(root, title, text) {
    root.replaceChildren(
      CR.dom.h(
        "div",
        { class: "page" },
        CR.dom.h("h1", { text: title }),
        CR.dom.h("p", { text }),
        CR.dom.h("p", {}, CR.dom.h("a", { href: "#home", text: "Back to the route" })),
      ),
    );
  }

  function failed(root, error) {
    console.error(error);
    page(root, "This page could not be shown", String(error && error.message ? error.message : error));
    return { title: "Error" };
  }

  // restore: this is Back or Forward, so return to the scroll position the entry remembers.
  function render(routeText, restore = false) {
    const parsed = CR.route.parse(routeText) || CR.route.parse("home");
    if (typeof active.cleanup === "function") active.cleanup();
    current = parsed;
    memoryRoute = parsed.route;
    const root = document.getElementById("main");
    root.replaceChildren();
    const view = views.get(parsed.view);
    try {
      if (view) {
        active = view.render({ args: parsed.args, route: parsed.route, root }) || {};
      } else {
        page(root, "Nothing at this address", `There is no page called "${parsed.route}".`);
        active = { title: "Not found" };
      }
    } catch (error) {
      active = failed(root, error);
    }
    document.title = active.title ? `${active.title} · ${BASE_TITLE}` : BASE_TITLE;
    window.scrollTo(0, restore ? (savedScroll() ?? 0) : 0);
    const heading = root.querySelector("h1");
    if (heading) {
      heading.tabIndex = -1;
      heading.focus({ preventScroll: true });
    }
    const nav = view && view.nav ? view.nav : parsed.view;
    for (const listener of listeners) listener(parsed, nav);
  }

  function start() {
    window.addEventListener("hashchange", () => render(readHash().slice(1) || memoryRoute, true));
    window.addEventListener(
      "scroll",
      () => {
        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(rememberScroll, 150);
      },
      { passive: true },
    );
    // A link click leaves this page: note where it was scrolled to before the hash changes.
    document.addEventListener("click", (event) => {
      if (event.target instanceof Element && event.target.closest("a[href^='#']")) rememberScroll();
    });
    render(readHash().slice(1) || "home");
  }

  return {
    register,
    go,
    start,
    refresh: () => current && render(current.route),
    current: () => current,
    onKey: (event) => (typeof active.onKey === "function" ? active.onKey(event) : false),
    onChange: (listener) => listeners.add(listener),
  };
})();
