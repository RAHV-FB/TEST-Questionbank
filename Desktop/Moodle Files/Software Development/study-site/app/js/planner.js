// Pure study-plan logic: which day is today, and how much of a day is done.
SD.planner = (() => {
  // days are sorted by date ("YYYY-MM-DD"); key is today's date in the same format. Before the
  // plan starts this is the first day, after it ends the last day, in a gap the next day.
  function todayIndex(days, key) {
    if (days.length === 0) return -1;
    const next = days.findIndex((day) => day.date >= key);
    return next === -1 ? days.length - 1 : next;
  }

  function dayProgress(day, planState) {
    const done = day.items.filter((item) => planState[item.id]?.done).length;
    return { done, total: day.items.length };
  }

  // Items of the days before day `index` that are not ticked, in plan order: [{day, item}].
  function missed(days, planState, index) {
    return days
      .slice(0, Math.max(0, index))
      .flatMap((day) => day.items.filter((item) => !planState[item.id]?.done).map((item) => ({ day, item })));
  }

  // A short status for a plan item read from the progress it leads to: "3 of 9 sections read"
  // for a module, "last 14/27" for a paper, "" otherwise. lookup: {sections(moduleId) -> {read,
  // total} | null, lastExam(paperId) -> {score, max} | null}.
  function hint(link, lookup) {
    const route = SD.route.parse(String(link).replace(/^#/, ""));
    if (!route) return "";
    if (route.view === "learn" && route.args.length === 1) {
      const n = lookup.sections(route.args[0]);
      return n && n.read > 0 ? `${n.read} of ${n.total} sections read` : "";
    }
    if (route.view === "exam" && route.args.length === 1) {
      const last = lookup.lastExam(route.args[0]);
      return last ? `last ${last.score}/${last.max}` : "";
    }
    return "";
  }

  return { todayIndex, dayProgress, missed, hint };
})();
