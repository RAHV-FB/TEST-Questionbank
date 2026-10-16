// Pure exam logic: the papers on offer, a paper drawn from the bank, the clock and its warnings,
// answer states, marking, and the attempt records (shape in app/API.md). No DOM, no store.
SD.exam = (() => {
  const SAMPLE = "sample";
  const BANK = "bank";
  const BANK_SHAPE = Object.freeze({ mcq: 12, open: 3 });
  const SAMPLE_MINUTES = 30; // the sample document has nine questions; half the real hour
  const PAPER_MINUTES = 60;
  const TYPE_ORDER = { mcq: 0, sort: 1, open: 2 };

  // Marks a question is worth: an open question its parts' marks, anything else one mark.
  function marksOf(q) {
    return q.type === "open" ? q.parts.reduce((sum, p) => sum + p.marks, 0) : 1;
  }

  function typeCounts(questions) {
    const counts = { mcq: 0, open: 0, sort: 0 };
    for (const q of questions) counts[q.type] += 1;
    return counts;
  }

  // The papers on offer, in the order a student should meet them: the teacher's sample paper,
  // the mock papers, then a paper drawn from the bank (questions: null until it is drawn).
  // data: SD.data, or SD.indexContent(...) in tests.
  function catalogue(data) {
    const list = [];
    const sample = data.module("sample-paper");
    const originals = sample ? sample.questions.filter((q) => q.origin === "teacher-sample") : [];
    if (originals.length) {
      list.push({
        id: SAMPLE,
        title: "The teacher's sample paper",
        kind: "sample",
        minutes: SAMPLE_MINUTES,
        intro_html: null,
        questions: originals.map((q) => q.id),
      });
    }
    for (const paper of data.papers) {
      list.push({
        id: paper.id,
        title: paper.title,
        kind: paper.kind,
        minutes: paper.minutes || PAPER_MINUTES,
        intro_html: paper.intro_html || null,
        questions: paper.questions.map((q) => q.id),
      });
    }
    list.push({
      id: BANK,
      title: "A paper from the bank",
      kind: "bank",
      minutes: PAPER_MINUTES,
      intro_html: null,
      questions: null,
    });
    return list;
  }

  // ---- a paper from the bank

  // A question and its variants count as one family: a paper never holds two of them.
  const family = (q) => q.variant_of || q.id;

  // Weak spots first (seen longest ago first), then questions not tried yet, then the rest
  // (seen longest ago first); ties in a stable random order for this seed.
  function preference(qState, seed, bank) {
    const random = SD.util.seededRandom(seed);
    const tie = new Map(bank.map((q) => [q.id, random()]));
    const rank = (q) => {
      const entry = qState[q.id];
      if (SD.progress.isWeak(entry)) return 0;
      return entry ? 2 : 1;
    };
    return (a, b) => {
      const ra = rank(a);
      const rb = rank(b);
      if (ra !== rb) return ra - rb;
      if (ra !== 1) {
        const age = (qState[a.id].last || 0) - (qState[b.id].last || 0);
        if (age !== 0) return age;
      }
      return tie.get(a.id) - tie.get(b.id);
    };
  }

  // Draw a paper: for each type, take one question per module per round (so modules differ by at
  // most one question), the module with the most pressing candidate first, until the shape is
  // full or the bank runs out. Never the same question, or two of one family, twice.
  // bank: question objects in course order. Returns ids: multiple choice first, then open
  // questions, each in course order.
  function buildBank(bank, qState, seed, shape = BANK_SHAPE) {
    const better = preference(qState, seed, bank);
    const taken = [];
    const families = new Set();
    for (const type of Object.keys(shape)) {
      const queues = new Map();
      for (const q of bank) {
        if (q.type !== type) continue;
        if (!queues.has(q.mid)) queues.set(q.mid, []);
        queues.get(q.mid).push(q);
      }
      for (const queue of queues.values()) queue.sort(better);
      let need = shape[type];
      while (need > 0) {
        const heads = [];
        for (const queue of queues.values()) {
          while (queue.length && families.has(family(queue[0]))) queue.shift();
          if (queue.length) heads.push(queue);
        }
        if (heads.length === 0) break;
        heads.sort((a, b) => better(a[0], b[0]));
        for (const queue of heads) {
          if (need === 0) break;
          // An earlier module in this round may have taken a variant of this module's head.
          while (queue.length && families.has(family(queue[0]))) queue.shift();
          if (queue.length === 0) continue;
          const q = queue.shift();
          families.add(family(q));
          taken.push(q);
          need -= 1;
        }
      }
    }
    const position = new Map(bank.map((q, i) => [q.id, i]));
    return taken
      .sort((a, b) => TYPE_ORDER[a.type] - TYPE_ORDER[b.type] || position.get(a.id) - position.get(b.id))
      .map((q) => q.id);
  }

  // ---- sitting the sample paper again

  // A second sitting of the teacher's paper with each question swapped for a variant of the same
  // type (one the student has not seen, else the one seen longest ago), so a better score shows
  // understanding and not memory. originals: the nine questions in paper order; variants: every
  // variant question; a question with no variant of its type stays as it is. Returns ids.
  function resit(originals, variants, qState, seed) {
    const random = SD.util.seededRandom(seed);
    return originals.map((original) => {
      const options = variants.filter((v) => v.variant_of === original.id && v.type === original.type);
      if (options.length === 0) return original.id;
      const rank = (q) => (qState[q.id] ? 1 : 0);
      const tie = new Map(options.map((q) => [q.id, random()]));
      options.sort(
        (a, b) =>
          rank(a) - rank(b) || (qState[a.id]?.last || 0) - (qState[b.id]?.last || 0) || tie.get(a.id) - tie.get(b.id),
      );
      return options[0].id;
    });
  }

  // ---- the attempt record

  // paper: a catalogue entry; questions: the question objects of this sitting, in paper order.
  function start(paper, questions, now) {
    return {
      id: `${paper.id}-${now}`,
      paper: paper.id,
      title: paper.title,
      minutes: paper.minutes,
      status: "running",
      started: now,
      ended: null,
      used_ms: 0,
      timed_out: false,
      questions: questions.map((q) => q.id),
      answers: {},
      flags: [],
      paper_answers: [],
      recorded: [],
      ticks: {},
      marks: {},
      passed: 0,
      failed: 0,
      to_mark: 0,
      score: 0,
      max: questions.reduce((sum, q) => sum + marksOf(q), 0),
    };
  }

  // The questions of a record that still exist (content can change between builds).
  function questionsOf(record, lookup) {
    return record.questions.map(lookup).filter(Boolean);
  }

  // ---- the clock

  const deadline = (record) => record.started + record.minutes * SD.util.MINUTE;
  const timeLeft = (record, now) => Math.max(0, deadline(record) - now);
  const expired = (record, now) => record.status === "running" && now >= deadline(record);

  // The warning the bar shows for the time left: 10 in the last ten minutes, 5 in the last five,
  // otherwise 0.
  function warning(left) {
    if (left <= 5 * SD.util.MINUTE) return 5;
    if (left <= 10 * SD.util.MINUTE) return 10;
    return 0;
  }

  // Hand the paper in. At or past the deadline it counts as time running out, and ends at 0:00.
  function finish(record, now, timedOut = false) {
    const end = deadline(record);
    const out = Boolean(timedOut) || now >= end;
    const ended = out ? end : now;
    return { ...record, status: "done", ended, used_ms: ended - record.started, timed_out: out };
  }

  // ---- answers and marking

  // "blank", "partial" (an open question with an empty part, a sort with an item unplaced) or "full".
  // onPaper: the student wrote this open answer on paper, as on the day, so it counts as answered.
  function answerState(q, answer, onPaper = false) {
    if (q.type === "mcq") return Number.isInteger(answer) ? "full" : "blank";
    if (q.type === "open" && onPaper) return "full";
    let filled = 0;
    let total = 0;
    if (q.type === "open") {
      total = q.parts.length;
      filled = q.parts.filter((p) => String(answer?.[p.label] ?? "").trim() !== "").length;
    } else {
      total = q.items.length;
      filled = Array.isArray(answer) ? answer.filter((a) => a !== null && a !== undefined).length : 0;
    }
    if (filled === 0) return "blank";
    return filled === total ? "full" : "partial";
  }

  const tallyRow = () => ({ count: 0, passed: 0, failed: 0, toMark: 0, score: 0, max: 0 });

  function add(into, r) {
    into.count += 1;
    into.passed += r.status === "pass" ? 1 : 0;
    into.failed += r.status === "fail" ? 1 : 0;
    into.toMark += r.status === "mark" ? 1 : 0;
    into.score += r.score;
    into.max += r.max;
  }

  // Results grouped by a key ("mid" or "sid"), in order of first appearance.
  function tally(results, key) {
    const groups = new Map();
    for (const r of results) {
      if (!groups.has(r[key])) groups.set(r[key], { [key]: r[key], ...tallyRow() });
      add(groups.get(r[key]), r);
    }
    return [...groups.values()];
  }

  // Each question's result, the totals, and the same figures per module and per section.
  // Multiple choice and sort are marked here; an open question scores what the student recorded
  // against its rubric (record.marks), counts as passed only at full marks, scores 0 when left
  // blank, and is "mark" (to mark) until then.
  function mark(questions, record) {
    const marks = record.marks || {};
    const onPaper = new Set(record.paper_answers || []);
    const results = questions.map((q) => {
      const answer = record.answers[q.id];
      const state = answerState(q, answer, onPaper.has(q.id));
      const max = marksOf(q);
      let score = 0;
      let status = "fail";
      if (q.type === "mcq") {
        score = state === "full" && q.options[answer]?.correct ? 1 : 0;
      } else if (q.type === "sort") {
        score = SD.scoring.sortScore(q, Array.isArray(answer) ? answer : []).full ? 1 : 0;
      } else if (state !== "blank" && q.id in marks) {
        score = Math.max(0, Math.min(max, marks[q.id]));
      } else if (state !== "blank") {
        status = "mark";
      }
      if (status !== "mark" && score === max) status = "pass";
      return { qid: q.id, mid: q.mid, sid: q.section_ref, type: q.type, state, status, score, max };
    });
    const totals = tallyRow();
    for (const r of results) add(totals, r);
    return { results, ...totals, modules: tally(results, "mid"), sections: tally(results, "sid") };
  }

  // The sections where marks were lost, the most first (ties keep the order they first appear
  // in the paper): [{sid, lost}]. Questions still to mark are left out: nothing is known yet.
  function lostBySection(results) {
    const lost = new Map();
    for (const r of results) {
      if (r.status === "mark" || r.max <= r.score) continue;
      lost.set(r.sid, (lost.get(r.sid) || 0) + r.max - r.score);
    }
    return [...lost].map(([sid, marks]) => ({ sid, lost: marks })).sort((a, b) => b.lost - a.lost);
  }

  // The record with its summary fields (what Home and the attempts list read) brought up to date.
  function withTotals(record, questions) {
    const m = mark(questions, record);
    return { ...record, passed: m.passed, failed: m.failed, to_mark: m.toMark, score: m.score, max: m.max };
  }

  // ---- discarding a sitting

  // True when nothing was answered, typed or ticked as written on paper.
  function untouched(record, questions) {
    const onPaper = new Set(record.paper_answers || []);
    return questions.every((q) => answerState(q, record.answers[q.id], onPaper.has(q.id)) === "blank");
  }

  // What is kept of a sitting the student threw away: no answers, no progress recorded. The stub
  // stays in the list of attempts' storage (hidden) so that a synced copy of the sitting on
  // another device cannot bring it back.
  function discard(record, now) {
    const { id, paper, title, minutes, started } = record;
    return { id, paper, title, minutes, started, ended: now, status: "discarded" };
  }

  // ---- the list of attempts

  // The sitting in progress (the latest started, should there be more than one), or null.
  function running(exams) {
    const live = exams.filter((e) => e.status === "running");
    return live.length ? live.reduce((a, b) => (b.started > a.started ? b : a)) : null;
  }

  // Sittings to show, newest first (discarded ones are not shown).
  const newestFirst = (exams) =>
    exams.filter((e) => e.status !== "discarded").sort((a, b) => b.started - a.started);

  function lastDone(exams, paperId) {
    return newestFirst(exams).find((e) => e.paper === paperId && e.status === "done") || null;
  }

  // The first sitting of a paper that was handed in (the baseline), or null.
  function firstDone(exams, paperId) {
    return newestFirst(exams).reverse().find((e) => e.paper === paperId && e.status === "done") || null;
  }

  return {
    SAMPLE,
    BANK,
    BANK_SHAPE,
    marksOf,
    typeCounts,
    catalogue,
    buildBank,
    resit,
    start,
    questionsOf,
    deadline,
    timeLeft,
    expired,
    warning,
    finish,
    answerState,
    mark,
    lostBySection,
    withTotals,
    untouched,
    discard,
    running,
    newestFirst,
    lastDone,
    firstDone,
  };
})();
