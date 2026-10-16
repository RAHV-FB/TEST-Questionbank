// Pure question selection for Practice: filters, the four modes, and stable option shuffles.
SD.select = (() => {
  const NEXT_WEAK = 3; // "Next 10" mixes in at most this many weak spots before new questions

  // scope: {kind: "all"} | {kind: "module", id} | {kind: "section", id};
  // type: "any" | "mcq" | "open" | "sort"; levels: list of allowed levels.
  function filter(questions, { scope, type, levels }) {
    return questions.filter(
      (q) =>
        (scope.kind === "all" ||
          (scope.kind === "module" && q.mid === scope.id) ||
          (scope.kind === "section" && q.section_ref === scope.id)) &&
        (type === "any" || q.type === type) &&
        levels.includes(q.level),
    );
  }

  // The nine originals in paper order, each followed by its variants.
  function sampleOrder(pool) {
    const originals = pool.filter((q) => q.origin === "teacher-sample");
    const variants = pool.filter((q) => q.origin === "teacher-variant");
    const out = [];
    for (const original of originals) {
      out.push(original.id);
      for (const v of variants) if (v.variant_of === original.id) out.push(v.id);
    }
    for (const v of variants) if (!out.includes(v.id)) out.push(v.id);
    return out;
  }

  // pool: question objects in course order. Returns at most n question ids.
  function pick(mode, pool, qState, n) {
    const ids = pool.map((q) => q.id);
    const weak = SD.progress.weakSpots(ids, qState);
    const fresh = SD.progress.notTried(ids, qState);
    if (mode === "weak") return weak.slice(0, n);
    if (mode === "new") return fresh.slice(0, n);
    if (mode === "sample") return sampleOrder(pool).slice(0, n);
    if (mode === "next10") {
      const solid = ids
        .filter((id) => qState[id] && !SD.progress.isWeak(qState[id]))
        .sort((a, b) => qState[a].last - qState[b].last);
      const order = [...weak.slice(0, NEXT_WEAK), ...fresh, ...weak.slice(NEXT_WEAK), ...solid];
      return order.slice(0, n);
    }
    throw new RangeError(`unknown practice mode ${mode}`);
  }

  // Display order of an mcq's options: shuffled, but the same for one question and attempt.
  function optionOrder(qid, attempt, count = 4) {
    const positions = Array.from({ length: count }, (_, i) => i);
    return SD.util.shuffled(positions, SD.util.hashString(`${qid}#${attempt}`));
  }

  return { filter, pick, sampleOrder, optionOrder };
})();
