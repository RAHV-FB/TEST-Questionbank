// The pipeline stepper's logic: the command line up to a stage, and a typed prediction compared
// line by line with the real output (as a diff: lines you expected that are not there, lines
// that are there and you did not expect).
SD.pipes = (() => {
  // Stage commands as the content stores them: the first is a whole command, the rest start
  // with "| ". upTo(stages, 1) -> "grep dining expenses.csv | wc -l".
  function upTo(stages, i) {
    return stages
      .slice(0, i + 1)
      .map((s) => s.cmd.trim())
      .join(" ");
  }

  // Output text -> lines; an empty output has no lines.
  function lines(text) {
    const out = String(text).replace(/\r\n?/g, "\n").replace(/\n+$/, "");
    return out === "" ? [] : out.split("\n");
  }

  // Spacing is not what a prediction is about: uniq -c pads its counts, so "5 dining" and
  // "      5 dining" are the same line here.
  const norm = (line) => line.trim().replace(/\s+/g, " ");

  // Compares a prediction with the real output. Blank lines in the prediction are ignored.
  // Returns {exact, matched, total, rows}: rows is a diff in output order, each row
  // {kind: "same" | "missing" | "extra", text} (missing: in the output, not predicted; extra:
  // predicted, not in the output), text as the output or the prediction wrote it.
  function compare(predicted, actual) {
    const want = lines(actual);
    const got = lines(predicted).filter((l) => l.trim() !== "");
    const a = want.map(norm);
    const b = got.map(norm);
    // Longest common subsequence, filled from the end so the walk below reads forwards.
    const lcs = Array.from({ length: a.length + 1 }, () => new Array(b.length + 1).fill(0));
    for (let i = a.length - 1; i >= 0; i -= 1) {
      for (let j = b.length - 1; j >= 0; j -= 1) {
        lcs[i][j] = a[i] === b[j] ? lcs[i + 1][j + 1] + 1 : Math.max(lcs[i + 1][j], lcs[i][j + 1]);
      }
    }
    const rows = [];
    let i = 0;
    let j = 0;
    while (i < a.length || j < b.length) {
      if (i < a.length && j < b.length && a[i] === b[j]) {
        rows.push({ kind: "same", text: want[i] });
        i += 1;
        j += 1;
      } else if (j < b.length && (i === a.length || lcs[i][j + 1] >= lcs[i + 1][j])) {
        rows.push({ kind: "extra", text: got[j] });
        j += 1;
      } else {
        rows.push({ kind: "missing", text: want[i] });
        i += 1;
      }
    }
    const matched = lcs[0][0];
    return { exact: matched === a.length && matched === b.length, matched, total: a.length, rows };
  }

  return { upTo, lines, compare };
})();
