// Plan (#plan): the eight days from Wed 14 Oct to the exam, each with checkable items.
(() => {
  const { h } = SD.dom;

  SD.router.register("plan", {
    render({ root }) {
      const days = SD.data.plan;
      const todayIndex = SD.planner.todayIndex(days, SD.util.dateKey(Date.now(), SD.util.EXAM_TZ));
      const counts = [];
      const sections = days.map((day, i) => {
        const count = h("span", { class: "plan-count" });
        counts.push([day, count]);
        return h(
          "section",
          {
            class: i === todayIndex ? "plan-day is-today" : "plan-day",
            "aria-labelledby": `day-${day.id}`,
          },
          h(
            "div",
            { class: "plan-day-head" },
            h(
              "h2",
              { id: `day-${day.id}` },
              h("span", { class: "plan-date", text: day.label }),
              h("span", { class: "plan-title", text: day.title }),
            ),
            h(
              "p",
              { class: "plan-meta" },
              i === todayIndex ? SD.ui.chip("today", "tag") : null,
              day.when ? h("span", { text: day.when }) : null,
              count,
            ),
          ),
          day.note_html ? h("div", { class: "prose fine-prose", html: day.note_html }) : null,
          SD.ui.planItems(day.items),
        );
      });
      const paint = () => {
        for (const [day, el] of counts) {
          const p = SD.planner.dayProgress(day, SD.store.get().plan);
          el.textContent = `${p.done}/${p.total} done`;
        }
      };
      paint();
      root.append(
        h(
          "div",
          { class: "page page-wide" },
          h("h1", { text: "Study plan" }),
          h("p", {
            class: "lead",
            text:
              "Eight days, from the baseline on Wednesday evening to the exam on Thursday 22 " +
              "October at 14:00. Tick each item when it is done; the home page shows today's block.",
          }),
          sections,
        ),
      );
      const stop = SD.store.subscribe((_, kind) => {
        if (kind === "plan") paint();
      });
      return { title: "Study plan", cleanup: stop, live: true };
    },
  });
})();
