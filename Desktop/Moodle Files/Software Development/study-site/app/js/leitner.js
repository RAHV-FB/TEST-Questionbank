// Pure Leitner scheduling for flashcards: boxes 1–5, each box waits longer before a card is due.
SD.leitner = (() => {
  const WAIT_DAYS = [0, 1, 2, 4, 7]; // box 1 is due at once; box 5 comes back after a week
  const STEP = { good: 1, easy: 2 };
  const GRADES = ["again", "good", "easy"];
  const DAY = 24 * 60 * 60 * 1000;

  function nextBox(entry, grade) {
    if (!GRADES.includes(grade)) throw new RangeError(`unknown grade ${grade}`);
    if (grade === "again") return 1;
    return Math.min(5, (entry ? entry.box : 1) + STEP[grade]);
  }

  // When a card in `box` is due, reviewed now. A long wait is cut short so that every card comes
  // back before the exam eve (examStart is the exam's start; null leaves the waits as they are),
  // but never sooner than tomorrow.
  function dueAfter(box, now, examStart) {
    const days = WAIT_DAYS[box - 1];
    if (days === 0) return now;
    const due = SD.util.addDays(now, days);
    if (examStart === null || examStart === undefined) return due;
    return Math.min(due, Math.max(SD.util.addDays(now, 1), SD.util.addDays(examStart, -1)));
  }

  // Days until the card is due again after this grade: 0 means later in this session.
  function waitDays(entry, grade, now = Date.now(), examStart = null) {
    const due = dueAfter(nextBox(entry, grade), now, examStart);
    return due === now ? 0 : Math.round((due - SD.util.addDays(now, 0)) / DAY);
  }

  // A new card counts as box 1: "good" moves it to box 2, due tomorrow.
  function review(entry, grade, now, examStart = null) {
    const box = nextBox(entry, grade);
    return { box, due: dueAfter(box, now, examStart), last: now, n: (entry ? entry.n : 0) + 1 };
  }

  function isDue(entry, now) {
    return Boolean(entry) && entry.due <= now;
  }

  // Due cards first (lowest box, then oldest due date), then cards never seen, in course order
  // (unless newCards is false: only what is due).
  function queue(cardIds, fcState, now, limit, newCards = true) {
    const due = cardIds
      .filter((id) => isDue(fcState[id], now))
      .sort((a, b) => fcState[a].box - fcState[b].box || fcState[a].due - fcState[b].due);
    const fresh = newCards ? cardIds.filter((id) => !fcState[id]) : [];
    return [...due, ...fresh].slice(0, limit);
  }

  function counts(cardIds, fcState, now) {
    const boxes = [0, 0, 0, 0, 0];
    let due = 0;
    let fresh = 0;
    for (const id of cardIds) {
      const entry = fcState[id];
      if (!entry) {
        fresh += 1;
        continue;
      }
      boxes[entry.box - 1] += 1;
      if (isDue(entry, now)) due += 1;
    }
    return { due, fresh, boxes, total: cardIds.length };
  }

  return { GRADES, review, waitDays, isDue, queue, counts };
})();
