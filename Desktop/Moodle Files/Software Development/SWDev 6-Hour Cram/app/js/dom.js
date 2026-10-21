// DOM helpers. h() builds elements; text children are always text nodes, so user input can never
// become markup. The only HTML ever parsed is build-time content HTML, passed as {html: ...}.
CR.dom = (() => {
  const SVG_NS = "http://www.w3.org/2000/svg";

  function append(el, children) {
    for (const child of children.flat(Infinity)) {
      if (child === null || child === undefined || child === false) continue;
      el.append(child instanceof Node ? child : String(child));
    }
  }

  // h("a", {href: "#home", class: "btn"}, "Home"). Props: class, text, html (content HTML only),
  // on<event> handlers, dataset, booleans (true sets the attribute), anything else as attribute.
  function h(tag, props, ...children) {
    const el = document.createElement(tag);
    for (const [key, value] of Object.entries(props || {})) {
      if (value === null || value === undefined || value === false) continue;
      if (key === "class") el.className = value;
      else if (key === "text") el.textContent = value;
      else if (key === "html") el.innerHTML = value;
      else if (key === "dataset") Object.assign(el.dataset, value);
      else if (key.startsWith("on") && typeof value === "function") {
        el.addEventListener(key.slice(2), value);
      } else el.setAttribute(key, value === true ? "" : String(value));
    }
    append(el, children);
    return el;
  }

  // svg("path", {d: "M3 8l3 3"}) builds an SVG element; props are plain attributes.
  function svg(tag, props, ...children) {
    const el = document.createElementNS(SVG_NS, tag);
    for (const [key, value] of Object.entries(props || {})) el.setAttribute(key, String(value));
    append(el, children);
    return el;
  }

  // Replaces an element's children; like append, it skips null and false and flattens lists.
  function fill(el, ...children) {
    el.replaceChildren();
    append(el, children);
    return el;
  }

  // Polite screen-reader announcement (answer verdicts, timer warnings).
  function announce(message) {
    const live = document.getElementById("live");
    if (!live) return;
    live.textContent = "";
    window.setTimeout(() => {
      live.textContent = message;
    }, 50);
  }

  // Inputs that take no typed text: single-key shortcuts still work while one has focus.
  const KEYLESS = new Set(["radio", "checkbox", "button", "submit", "reset", "range", "color"]);

  // True while the user types in a field: single-key shortcuts must stay out of the way.
  function isTyping(event) {
    const t = event.target;
    if (!(t instanceof HTMLElement)) return false;
    if (t.isContentEditable || t.tagName === "TEXTAREA" || t.tagName === "SELECT") return true;
    return t.tagName === "INPUT" && !KEYLESS.has(t.type);
  }

  // Bring a result into view and put keyboard focus on it, so what was just activated (a button
  // that has gone) does not leave focus on the page body.
  function reveal(el) {
    if (!el.hasAttribute("tabindex")) el.tabIndex = -1;
    el.focus({ preventScroll: true });
    el.scrollIntoView({ block: "nearest" });
  }

  // Scroll to an element by id without touching the hash (the hash is the router's).
  function scrollToId(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.scrollIntoView({ block: "start", behavior: "auto" });
    reveal(el);
  }

  // Content HTML -> plain text for a prompt, keeping line breaks of paragraphs and code.
  function textOf(html) {
    const box = document.createElement("div");
    box.innerHTML = html;
    box.querySelectorAll(".code-lang").forEach((el) => el.remove());
    box.querySelectorAll(".dline, p, li, pre, tr, h2, h3, h4").forEach((el) => el.append("\n"));
    return box.textContent.replace(/\n{3,}/g, "\n\n").trim();
  }

  // A plain-text excerpt of content HTML for lists: code blocks are left out and the text is cut at
  // a word, or at the end of its first sentence when that fits.
  function excerpt(html, max = 110) {
    const box = document.createElement("div");
    box.innerHTML = html;
    box.querySelectorAll(".code").forEach((el) => el.remove());
    const flat = box.textContent.replace(/\s+/g, " ").trim();
    const first = /^.+?[.?](?=\s|$)/.exec(flat);
    if (first && first[0].length <= max) return first[0];
    if (flat.length <= max) return flat;
    const cut = flat.slice(0, max - 1);
    const space = cut.lastIndexOf(" ");
    return (space > max * 0.4 ? cut.slice(0, space) : cut).trimEnd().replace(/[,;:.\-–]$/, "") + "…";
  }

  // Content text with backtick code marks ("`tmp_path`: a file"): the nodes for it, the marked parts
  // as <code>. plain() is the same text without the marks, for lines that stay plain text.
  function codeText(text) {
    return String(text)
      .split("`")
      .map((part, i) => (i % 2 === 1 && part ? h("code", { text: part }) : part));
  }

  const plain = (text) => String(text).replace(/`/g, "");

  return { h, svg, append, fill, announce, isTyping, reveal, scrollToId, textOf, excerpt, codeText, plain };
})();
