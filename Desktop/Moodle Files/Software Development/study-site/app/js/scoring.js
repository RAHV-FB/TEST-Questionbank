// Pure scoring: multiple choice, rubric self-marking, sorting, and the pytest-style summary line.
SD.scoring = (() => {
  // ticks: {partLabel: [rubric indexes the student ticked]}. A part scores one mark per point
  // made, capped at its marks: score = min(marks, ticked).
  function openScore(q, ticks) {
    const parts = q.parts.map((part) => {
      const valid = new Set(
        (ticks[part.label] || []).filter(
          (i) => Number.isInteger(i) && i >= 0 && i < part.rubric.length,
        ),
      );
      return { label: part.label, score: Math.min(part.marks, valid.size), max: part.marks };
    });
    const score = parts.reduce((sum, p) => sum + p.score, 0);
    const max = parts.reduce((sum, p) => sum + p.max, 0);
    return { score, max, parts, full: score === max };
  }

  // answers: the category id chosen for each item, in item order (null when not placed).
  function sortScore(q, answers) {
    const items = q.items.map((item, i) => answers[i] === item.category);
    const correct = items.filter(Boolean).length;
    return { correct, total: items.length, items, full: correct === items.length };
  }

  // {passed, failed, toMark, ms} -> segments for "14 passed, 3 failed, 2 to mark in 52m10s".
  function pytestSummary({ passed = 0, failed = 0, toMark = 0, ms = null }) {
    const segments = [];
    if (passed) segments.push({ text: `${passed} passed`, kind: "pass" });
    if (failed) segments.push({ text: `${failed} failed`, kind: "fail" });
    if (toMark) segments.push({ text: `${toMark} to mark`, kind: "warn" });
    if (segments.length === 0) segments.push({ text: "no answers", kind: "none" });
    return { segments, tail: ms === null ? "" : `in ${SD.util.duration(ms)}` };
  }

  return { openScore, sortScore, pytestSummary };
})();
