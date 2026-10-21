// The route clock: when each stop of the route starts and ends from the start time you
// set, how far you are, and whether you are on pace. Pure; stops are {id, minutes}, `done` is the
// state's {[stopId]: {d: bool, last}} map.
CR.clock = (() => {
  const MIN = CR.util.MINUTE;
  const TOLERANCE = 5; // minutes either way that still count as "on pace"

  const isDone = (done, id) => Boolean(done && done[id] && done[id].d);

  const totalMinutes = (stops) => stops.reduce((sum, s) => sum + s.minutes, 0);

  // Each stop laid end to end from the start: [{id, start, end}].
  function schedule(stops, start) {
    let at = start;
    return stops.map((s) => {
      const row = { id: s.id, start: at, end: at + s.minutes * MIN };
      at = row.end;
      return row;
    });
  }

  function doneMinutes(stops, done) {
    return stops.filter((s) => isDone(done, s.id)).reduce((sum, s) => sum + s.minutes, 0);
  }

  function progress(stops, done) {
    const count = stops.filter((s) => isDone(done, s.id)).length;
    const minutes = doneMinutes(stops, done);
    const total = totalMinutes(stops);
    return {
      count,
      total: stops.length,
      minutes,
      totalMinutes: total,
      remaining: total - minutes,
      percent: CR.util.percent(minutes, total),
    };
  }

  // The first stop not done yet, or -1 when every stop is done.
  const nextIndex = (stops, done) => stops.findIndex((s) => !isDone(done, s.id));

  // The stop to go to after `stopId`: the next one not done, looking forward first, then from the top.
  function after(stops, done, stopId) {
    const at = stops.findIndex((s) => s.id === stopId);
    return (
      stops.slice(at + 1).find((s) => !isDone(done, s.id)) ||
      stops.find((s) => s.id !== stopId && !isDone(done, s.id)) ||
      null
    );
  }

  // Where the student stands against the plan. `before`: the start time is still ahead.
  // Otherwise the minutes of work done are set against the minutes elapsed: more done than
  // elapsed means ahead. `finished`: every stop is done.
  function pace(stops, done, start, now) {
    if (nextIndex(stops, done) === -1) return { state: "finished", minutes: 0 };
    if (now < start) return { state: "before", minutes: Math.ceil((start - now) / MIN) };
    const diff = doneMinutes(stops, done) - (now - start) / MIN;
    if (Math.abs(diff) <= TOLERANCE) return { state: "on", minutes: Math.round(Math.abs(diff)) };
    return { state: diff > 0 ? "ahead" : "behind", minutes: Math.round(Math.abs(diff)) };
  }

  // When the plan ends if the stops run back to back from the start.
  const plannedEnd = (stops, start) => start + totalMinutes(stops) * MIN;

  // When the work ends if what is left starts now and runs back to back.
  const projectedEnd = (stops, done, now) => now + progress(stops, done).remaining * MIN;

  // "07:40", or "05:50 +1" when it falls on a later day than `base`.
  function label(ts, base) {
    const days = CR.util.dayDiff(ts, base);
    return CR.util.timeOfDay(ts) + (days > 0 ? ` +${days}` : "");
  }

  // The start the page proposes when none is set: now, to the minute.
  const defaultStart = (now) => now - (now % MIN);

  return {
    TOLERANCE,
    isDone,
    totalMinutes,
    schedule,
    doneMinutes,
    progress,
    nextIndex,
    after,
    pace,
    plannedEnd,
    projectedEnd,
    label,
    defaultStart,
  };
})();
