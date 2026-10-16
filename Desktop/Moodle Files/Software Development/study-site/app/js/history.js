// The history view's logic: commits grouped by tag, the --stat split into its parts, the four
// messages to choose from in "Guess the message", and which commit to guess next.
SD.history = (() => {
  // Commits are oldest first. A tag closes a group: the commits after the previous tag, up to and
  // including the tagged one. Commits after the last tag form a group with tag null.
  function groups(commits) {
    const out = [];
    let current = [];
    for (const commit of commits) {
      current.push(commit);
      if (commit.tag) {
        out.push({ tag: commit.tag, note: commit.git?.tag_note || "", commits: current });
        current = [];
      }
    }
    if (current.length) out.push({ tag: null, note: "", commits: current });
    return out;
  }

  // One --stat line: " src/report.py | 13 +++---" -> {lead, plus, minus}; the summary line and
  // anything else come back whole in lead.
  function statRows(stat) {
    return String(stat)
      .split("\n")
      .filter((line) => line.trim() !== "")
      .map((line) => {
        const m = /^(.*\|\s+\d+ )(\+*)(-*)$/.exec(line);
        return m ? { lead: m[1], plus: m[2], minus: m[3] } : { lead: line, plus: "", minus: "" };
      });
  }

  // Every path a commit touches, renames counted under both names.
  function touched(commit) {
    const git = commit.git || { files: [], hidden: [] };
    return new Set(
      [...git.files.flatMap((f) => [f.path, f.old_path]), ...git.hidden.map((f) => f.path)].filter(Boolean),
    );
  }

  // The real message and up to three others from this history, shuffled by seed. Others are the
  // closest commits: the ones touching the same files first, then the nearest in time, with a
  // little seeded jitter so another attempt can bring others. Returns [{hash, message, real}].
  function candidates(commits, hash, seed) {
    const target = commits.find((c) => c.hash === hash);
    const at = commits.indexOf(target);
    const files = touched(target);
    const random = SD.util.seededRandom(seed);
    const seen = new Set([target.message]);
    const ranked = commits
      .filter((c) => c !== target)
      .map((c, i) => {
        const shared = [...touched(c)].filter((p) => files.has(p)).length;
        return { c, score: shared * 10 - Math.abs(commits.indexOf(c) - at) + random() * 3, i };
      })
      .sort((a, b) => b.score - a.score || a.i - b.i);
    const others = [];
    for (const { c } of ranked) {
      if (others.length === 3) break;
      if (seen.has(c.message)) continue;
      seen.add(c.message);
      others.push({ hash: c.hash, message: c.message, real: false });
    }
    return SD.util.shuffled([{ hash: target.hash, message: target.message, real: true }, ...others], seed);
  }

  // Session 8's test for a subject line: it completes "If applied, this commit will ...".
  // An ordinary capitalised first word is lowered ("Add" -> "add"); "README" or "CI" stay.
  function ifApplied(message) {
    const text = String(message).trim();
    const first = /^[A-Z][a-z]+\b/.test(text) ? text[0].toLowerCase() + text.slice(1) : text;
    return `If applied, this commit will ${first}${/[.!?]$/.test(first) ? "" : "."}`;
  }

  // The next commit to guess: one not tried yet, else one guessed wrong, else any; never the
  // one just shown. record: {[hash]: "right" | "wrong" | "written"}.
  function next(commits, record, random, current = null) {
    const pool = commits.filter((c) => c.hash !== current);
    const fresh = pool.filter((c) => !record[c.hash]);
    const wrong = pool.filter((c) => record[c.hash] === "wrong");
    const from = fresh.length ? fresh : wrong.length ? wrong : pool;
    return from.length ? SD.util.pick(random, from).hash : current;
  }

  // {tried, right, written} over the commits in this build.
  function tally(commits, record) {
    const marks = commits.map((c) => record[c.hash]).filter(Boolean);
    return {
      tried: marks.length,
      right: marks.filter((m) => m === "right").length,
      written: marks.filter((m) => m === "written").length,
    };
  }

  return { groups, statRows, touched, candidates, ifApplied, next, tally };
})();
