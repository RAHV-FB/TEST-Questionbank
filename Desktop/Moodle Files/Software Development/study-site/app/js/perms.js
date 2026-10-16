// File permissions as session 9 teaches them: three classes (owner, group, others) times three
// rights (r, w, x); r = 4, w = 2, x = 1, added per class. A mode is a number from 0 to 0o777.
SD.perms = (() => {
  const WHO = ["owner", "group", "others"];
  const WHAT = ["r", "w", "x"];
  const VALUE = { r: 4, w: 2, x: 1 };
  const WORD = { r: "read", w: "write", x: "execute" };
  const SHIFT = { owner: 6, group: 3, others: 0 };

  // The four modes slide 21 names, with its words.
  const COMMON = [
    { mode: 0o644, use: "A normal file" },
    { mode: 0o755, use: "A script or a folder" },
    { mode: 0o600, use: "A private key" },
    { mode: 0o777, use: "Almost never the answer" },
  ];

  // Drill targets: modes a real ls -l shows, not arbitrary bit patterns.
  const DRILL_MODES = [
    0o644, 0o755, 0o600, 0o777, 0o700, 0o640, 0o664, 0o775, 0o750, 0o444, 0o400, 0o711, 0o660, 0o770, 0o555,
    0o744, 0o666, 0o500,
  ];
  const FORMS = ["number", "letters", "switches"];

  const bit = (who, what) => VALUE[what] << SHIFT[who];
  const has = (mode, who, what) => (mode & bit(who, what)) !== 0;
  const toggle = (mode, who, what) => mode ^ bit(who, what);
  const digit = (mode, who) => (mode >> SHIFT[who]) & 7;

  // 0o755 -> "755"
  function toOctal(mode) {
    return mode.toString(8).padStart(3, "0");
  }

  // "755" or "0755" -> 0o755; anything else -> null.
  function parseOctal(text) {
    const m = /^0?([0-7]{3})$/.exec(String(text).trim());
    return m ? parseInt(m[1], 8) : null;
  }

  // 0o755 -> "rwxr-xr-x"
  function toLetters(mode) {
    return WHO.map((who) => WHAT.map((what) => (has(mode, who, what) ? what : "-")).join("")).join("");
  }

  // As ls -l prints it: a type character (- file, d directory), then the nine letters.
  function toLs(mode, type = "-") {
    return type + toLetters(mode);
  }

  // "rwxr-xr-x" or "-rwxr-xr-x" or "drwxr-xr-x" -> {mode, type}; anything else -> null.
  // Each position holds its own letter or "-" (r w x, r w x, r w x).
  function parseLetters(text) {
    const raw = String(text).trim();
    const m = /^([-d]?)([-r][-w][-x][-r][-w][-x][-r][-w][-x])$/.exec(raw);
    if (!m) return null;
    let mode = 0;
    for (let i = 0; i < 9; i += 1) {
      if (m[2][i] !== "-") mode |= 1 << (8 - i);
    }
    return { mode, type: m[1] || null };
  }

  // The working for one class: "7 = 4 + 2 + 1", "5 = 4 + 1", "0".
  function sum(mode, who) {
    const parts = WHAT.filter((what) => has(mode, who, what)).map((what) => VALUE[what]);
    const total = digit(mode, who);
    return parts.length > 1 ? `${total} = ${parts.join(" + ")}` : String(total);
  }

  // "read, write, execute", "read", "nothing".
  function rights(mode, who) {
    const words = WHAT.filter((what) => has(mode, who, what)).map((what) => WORD[what]);
    return words.length ? words.join(", ") : "nothing";
  }

  const common = (mode) => COMMON.find((c) => c.mode === mode) || null;

  // A drill task: a target mode shown in one form, to be answered in another.
  function task(random, previous = null) {
    const pool = DRILL_MODES.filter((m) => m !== previous);
    const mode = SD.util.pick(random, pool);
    const from = SD.util.pick(random, FORMS);
    const to = SD.util.pick(random, FORMS.filter((f) => f !== from));
    return { mode, from, to };
  }

  // The mode an answer stands for, or null when it cannot be read in that form.
  // number: "640"; letters: "rw-r-----" or "-rw-r-----"; switches: a mode number already.
  function readAnswer(form, answer) {
    if (form === "number") return parseOctal(answer);
    if (form === "letters") return parseLetters(answer)?.mode ?? null;
    return Number.isInteger(answer) && answer >= 0 && answer <= 0o777 ? answer : null;
  }

  // Drill targets are files: letters that start with "d" describe a directory and are wrong
  // even when the nine rights match.
  function check(t, answer) {
    const given = readAnswer(t.to, answer);
    const directory = t.to === "letters" && parseLetters(answer)?.type === "d";
    return { ok: given === t.mode && !directory, given, readable: given !== null, directory };
  }

  return {
    WHO,
    WHAT,
    VALUE,
    WORD,
    COMMON,
    DRILL_MODES,
    FORMS,
    has,
    toggle,
    digit,
    toOctal,
    parseOctal,
    toLetters,
    toLs,
    parseLetters,
    sum,
    rights,
    common,
    task,
    readAnswer,
    check,
  };
})();
