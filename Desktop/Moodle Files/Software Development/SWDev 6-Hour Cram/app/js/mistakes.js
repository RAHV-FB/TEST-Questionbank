// Pure attempt records, the mistakes queue and practice sessions. An attempt record is
// {a: attempts, c: correct, w: wrong, last: ts, ok: verdict of the latest attempt}; the mistakes
// are the questions whose latest attempt was wrong, so a wrong answer redone right leaves the list.
CR.mistakes = (() => {
  const isWrong = (entry) => Boolean(entry) && entry.ok === false;

  // One more attempt at a question. Mutates qState (the page's store does this inside update()).
  function record(qState, id, ok, now) {
    const e = qState[id] || { a: 0, c: 0, w: 0, last: 0, ok: false };
    qState[id] = {
      a: e.a + 1,
      c: e.c + (ok ? 1 : 0),
      w: e.w + (ok ? 0 : 1),
      last: now,
      ok: Boolean(ok),
    };
    return qState[id];
  }

  // Correct the verdict of the latest attempt without counting a new one (an open answer whose
  // mark is recorded again after the ticks changed). Unknown question: it counts as an attempt.
  function amend(qState, id, ok, now) {
    const e = qState[id];
    if (!e) return record(qState, id, ok, now);
    if (e.ok === Boolean(ok)) {
      qState[id] = { ...e, last: now };
    } else if (ok) {
      qState[id] = { ...e, c: e.c + 1, w: Math.max(0, e.w - 1), ok: true, last: now };
    } else {
      qState[id] = { ...e, c: Math.max(0, e.c - 1), w: e.w + 1, ok: false, last: now };
    }
    return qState[id];
  }

  // Ids to redo: latest attempt wrong, the question missed most often first, then the one wrong
  // longest ago. `known` (a Set of ids) leaves out questions this build does not hold.
  function queue(qState, known = null) {
    return Object.keys(qState)
      .filter((id) => isWrong(qState[id]) && (!known || known.has(id)))
      .sort((a, b) => qState[b].w - qState[a].w || qState[a].last - qState[b].last || (a < b ? -1 : 1));
  }

  // How a list of questions stands: never tried, latest right, latest wrong.
  function counts(qState, ids) {
    let right = 0;
    let wrong = 0;
    for (const id of ids) {
      const e = qState[id];
      if (!e) continue;
      if (e.ok) right += 1;
      else wrong += 1;
    }
    return { total: ids.length, tried: right + wrong, right, wrong, fresh: ids.length - right - wrong };
  }

  // Ids grouped by a key, in order of first appearance: [[key, [ids]]].
  function groupBy(ids, keyOf) {
    const groups = new Map();
    for (const id of ids) {
      const key = keyOf(id);
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(id);
    }
    return [...groups];
  }

  // ---- practice sessions: one list of question ids, answered one at a time. {ids, i, res, last};
  // `i` is the position of the current question, `res[id]` is true, false or null (skipped).

  const newSession = (ids, now) => ({ ids: [...ids], i: 0, res: {}, last: now });

  const sessionCurrent = (s) => (s.i < s.ids.length ? s.ids[s.i] : null);

  const sessionFinished = (s) => s.i >= s.ids.length;

  const sessionAnswered = (s) => {
    const id = sessionCurrent(s);
    return id !== null && id in s.res;
  };

  // The current question got a verdict (true, false) or was skipped (null).
  function sessionAnswer(s, ok, now) {
    const id = sessionCurrent(s);
    if (id === null || id in s.res) return s;
    return { ...s, res: { ...s.res, [id]: ok === null ? null : Boolean(ok) }, last: now };
  }

  // Move on to the next question; only once the current one has a verdict or was skipped.
  const sessionNext = (s, now) => (sessionAnswered(s) ? { ...s, i: s.i + 1, last: now } : s);

  function sessionSummary(s) {
    const verdicts = s.ids.filter((id) => id in s.res);
    return {
      total: s.ids.length,
      answered: verdicts.filter((id) => s.res[id] !== null).length,
      right: verdicts.filter((id) => s.res[id] === true).length,
      wrong: s.ids.filter((id) => s.res[id] === false),
      skipped: s.ids.filter((id) => s.res[id] === null),
      finished: sessionFinished(s),
    };
  }

  // A new session over what was wrong or skipped in this one.
  function sessionRedo(s, now) {
    const sum = sessionSummary(s);
    return newSession([...sum.wrong, ...sum.skipped], now);
  }

  return {
    isWrong,
    record,
    amend,
    queue,
    counts,
    groupBy,
    newSession,
    sessionCurrent,
    sessionFinished,
    sessionAnswered,
    sessionAnswer,
    sessionNext,
    sessionSummary,
    sessionRedo,
  };
})();
