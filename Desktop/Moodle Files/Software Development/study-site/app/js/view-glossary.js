// Glossary (#glossary): every term A–Z with its module and a link to the section that teaches it.
(() => {
  const { h } = SD.dom;

  // The letter a term is filed under (as the build sorts it): backticks and quotes do not
  // count; a term that starts with a symbol, a flag or a digit goes under "#".
  const initial = (term) => {
    const c = term.replace(/[`"'‘’“”]/g, "").trim().charAt(0).toUpperCase();
    return /[A-Z]/.test(c) ? c : "#";
  };

  SD.router.register("glossary", {
    render({ root }) {
      const entries = SD.data.glossary.map((entry) => {
        const mod = SD.data.module(entry.mid);
        const section = SD.data.section(entry.section_ref);
        const el = h(
          "div",
          { class: "term" },
          h("dt", { html: entry.term_html }),
          h(
            "dd",
            {},
            h("span", { class: "prose", html: entry.definition_html }),
            h(
              "a",
              {
                class: "term-link",
                href: section ? "#" + SD.data.sectionRoute(section.id) : SD.route.href("learn", entry.mid),
              },
              mod.title,
              section ? ` · section ${section.index + 1}` : "",
            ),
          ),
        );
        return { entry, el, text: `${entry.term} ${el.textContent}`.toLowerCase() };
      });
      const groups = new Map();
      for (const item of entries) {
        const letter = initial(item.entry.term);
        if (!groups.has(letter)) groups.set(letter, []);
        groups.get(letter).push(item);
      }
      const sections = [...groups].map(([letter, items]) => ({
        items,
        el: h(
          "section",
          { class: "gloss-group" },
          h("h2", { class: "gloss-letter", text: letter }),
          h("dl", { class: "terms" }, items.map((i) => i.el)),
        ),
      }));
      const count = h("p", { class: "fine", "aria-live": "polite" });
      const filter = h("input", {
        type: "search",
        id: "glossary-filter",
        placeholder: "Type part of a term or definition",
        autocomplete: "off",
      });
      const paint = () => {
        const needle = filter.value.trim().toLowerCase();
        let shown = 0;
        for (const group of sections) {
          let any = false;
          for (const item of group.items) {
            const match = !needle || item.text.includes(needle);
            item.el.hidden = !match;
            if (match) shown += 1;
            any = any || match;
          }
          group.el.hidden = !any;
        }
        count.textContent = needle
          ? `${SD.util.plural(shown, "term")} match "${filter.value.trim()}".`
          : `${SD.util.plural(entries.length, "term")} from ${SD.util.plural(SD.data.modules.length, "module")}.`;
      };
      filter.addEventListener("input", paint);
      root.append(
        h(
          "div",
          { class: "page" },
          h("h1", { text: "Glossary" }),
          h("div", { class: "field filter-field" }, h("label", { for: "glossary-filter", text: "Filter" }), filter),
          count,
          sections.map((g) => g.el),
        ),
      );
      paint();
      return { title: "Glossary" };
    },
  });
})();
