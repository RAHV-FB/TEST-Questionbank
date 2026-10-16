// More (#more): on phones the tab bar holds five places; everything else is listed here.
(() => {
  const { h } = SD.dom;
  const PLACES = [
    ["#plan", "Study plan", "The eight days to the exam, with today's block."],
    ["#cards", "Flashcards", "Leitner boxes: due cards first."],
    ["#history", "Expense-tracker history", "All 25 commits, diff by diff."],
    ["#labs", "Terminal lab", "Pipelines, permissions, paths, exit codes and Lab 10 solved."],
    ["#glossary", "Glossary", "Every term, A–Z."],
  ];

  SD.router.register("more", {
    render({ root }) {
      root.append(
        h(
          "div",
          { class: "page" },
          h("h1", { text: "More" }),
          h(
            "ul",
            { class: "link-list" },
            PLACES.map(([href, title, text]) =>
              h(
                "li",
                {},
                h(
                  "a",
                  { href },
                  h("span", { class: "link-title", text: title }),
                  h("span", { class: "fine", text }),
                ),
              ),
            ),
          ),
        ),
      );
      return { title: "More" };
    },
  });
})();
