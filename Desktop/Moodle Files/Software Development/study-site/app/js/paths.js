// The paths lab: a fixed tree (the expense-tracker under /home/alice/code), bash's cd with PWD
// and OLDPWD, and pwd, ls and echo for exploring. There are no symbolic links and no CDPATH, so
// bash's logical cd and the system's own walk agree: names are checked left to right, ".." goes
// up one level (and stays at / at the top), "." stays where it is.
SD.paths = (() => {
  const HOME = "/home/alice";
  const PROJECT = "/home/alice/code/expense-tracker";
  // Directories end in "/".
  const ENTRIES = [
    "/etc/",
    "/home/",
    "/home/alice/",
    "/home/alice/code/",
    `${PROJECT}/`,
    `${PROJECT}/.git/`,
    `${PROJECT}/.github/`,
    `${PROJECT}/.github/workflows/`,
    `${PROJECT}/.github/workflows/check.yml`,
    `${PROJECT}/README.md`,
    `${PROJECT}/expenses.csv`,
    `${PROJECT}/pyproject.toml`,
    `${PROJECT}/src/`,
    `${PROJECT}/src/expense_tracker/`,
    `${PROJECT}/src/expense_tracker/__init__.py`,
    `${PROJECT}/src/expense_tracker/cli.py`,
    `${PROJECT}/src/expense_tracker/report.py`,
    `${PROJECT}/tests/`,
    `${PROJECT}/tests/test_duplicates.py`,
    `${PROJECT}/tests/test_io.py`,
    `${PROJECT}/tests/test_report.py`,
    "/home/alice/code/project-template/",
    "/tmp/",
    "/usr/",
  ];
  const KIND = new Map([["/", "dir"]]);
  for (const entry of ENTRIES)
    KIND.set(entry.endsWith("/") ? entry.slice(0, -1) : entry, entry.endsWith("/") ? "dir" : "file");
  const ALL = [...KIND.keys()];
  const DIRS = ALL.filter((p) => KIND.get(p) === "dir");
  const FILES = ALL.filter((p) => KIND.get(p) === "file");

  // Where people stand when they work; drill tasks start from these.
  const PLACES = [
    "/",
    HOME,
    "/home/alice/code",
    PROJECT,
    `${PROJECT}/src`,
    `${PROJECT}/src/expense_tracker`,
    `${PROJECT}/tests`,
    `${PROJECT}/.github/workflows`,
    "/home/alice/code/project-template",
    "/tmp",
    "/etc",
  ];
  const REASON = { missing: "No such file or directory", file: "Not a directory" };

  const kind = (path) => KIND.get(path) || null;
  const parent = (path) => path.slice(0, path.lastIndexOf("/")) || "/";
  const join = (dir, name) => (dir === "/" ? `/${name}` : `${dir}/${name}`);
  const depth = (path) => path.split("/").filter(Boolean).length;
  // C-locale (byte) order, as the slide's ls shows it: dot names first, capitals before small.
  const byBytes = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  // A leading "//" (exactly two slashes) is left alone by POSIX and kept by bash.
  const DOUBLE = /^\/\/(?!\/)/;

  function children(dir) {
    return ALL.filter((p) => p !== "/" && parent(p) === dir)
      .map((p) => p.slice(p.lastIndexOf("/") + 1))
      .sort(byBytes);
  }

  // The tree as slide 8 draws it, one line per entry: {path, name, dir, prefix}.
  function treeLines() {
    const lines = [{ path: "/", name: "/", dir: true, prefix: "" }];
    const visit = (dir, indent) => {
      const names = children(dir);
      names.forEach((name, i) => {
        const last = i === names.length - 1;
        const path = join(dir, name);
        const isDir = kind(path) === "dir";
        lines.push({
          path,
          name: isDir ? `${name}/` : name,
          dir: isDir,
          prefix: indent + (last ? "└── " : "├── "),
        });
        if (isDir) visit(path, indent + (last ? "    " : "│   "));
      });
    };
    visit("/", "");
    return lines;
  }

  // Splits a typed line into words as the shell does for these simple cases: quotes group and
  // are removed. Each word is {text, raw, tilde}: tilde is true when it starts with an unquoted
  // "~" whose prefix (up to the first "/") holds no quotes, the only case the shell expands.
  function words(line) {
    const out = [];
    let word = null;
    let quote = null;
    for (const ch of String(line)) {
      if (quote) {
        if (ch === quote) quote = null;
        else word.text += ch;
        word.raw += ch;
        continue;
      }
      if (/\s/.test(ch)) {
        if (word) out.push(word);
        word = null;
        continue;
      }
      if (!word) word = { text: "", raw: "", tilde: ch === "~", quotedPrefix: false };
      word.raw += ch;
      if (ch === '"' || ch === "'") {
        quote = ch;
        if (!word.text.includes("/")) word.quotedPrefix = true;
      } else word.text += ch;
    }
    if (quote) return { error: "unmatched quote" };
    if (word) out.push(word);
    return { words: out.map((w) => ({ text: w.text, raw: w.raw, tilde: w.tilde && !w.quotedPrefix })) };
  }

  // Tilde expansion: ~ and ~/x are the home folder, and so is ~alice. Any other ~name is not a
  // user on this machine, so the word stays as it is.
  function expand(word) {
    if (!word.tilde) return word.text;
    const m = /^~([^/]*)(\/.*)?$/.exec(word.text);
    if (m[1] !== "" && m[1] !== "alice") return word.text;
    return HOME + (m[2] || "");
  }

  const plain = (text) => ({ text, raw: text, tilde: text.startsWith("~") });

  // Walks a path name by name. Returns {ok, path, steps: [{part, dir}], failed}; failed is
  // {part, at, reason}, reason "missing" (No such file or directory) or "file" (Not a directory).
  // wantDir: the last name must be a directory too (cd); ls accepts a file there.
  function walk(start, path, wantDir) {
    const absolute = path.startsWith("/");
    const double = DOUBLE.test(absolute ? path : start);
    let dir = absolute ? "/" : start.replace(DOUBLE, "/");
    const steps = [];
    const parts = path.split("/").filter(Boolean);
    for (let i = 0; i < parts.length; i += 1) {
      const part = parts[i];
      if (part === "..") dir = parent(dir);
      else if (part !== ".") {
        const next = join(dir, part);
        const k = kind(next);
        if (k === null) return { ok: false, path: null, steps, failed: { part, at: dir, reason: "missing" } };
        if (k === "file" && (wantDir || i < parts.length - 1)) {
          return { ok: false, path: null, steps, failed: { part, at: dir, reason: "file" } };
        }
        dir = next;
      }
      steps.push({ part, dir });
    }
    return { ok: true, path: double ? "/" + dir : dir, steps, failed: null };
  }

  // bash's cd. state = {pwd, oldpwd}; word = a word from words(), or null for plain "cd".
  // Returns {ok, state, out, err, from, target, steps, failed}. from says where the path came
  // from: "none" (no argument: $HOME), "oldpwd" (cd -), "tilde", "root" (absolute) or "pwd".
  function cd(state, word = null) {
    const fail = (err, extra = {}) => ({
      ok: false,
      state,
      out: null,
      err,
      target: null,
      steps: [],
      failed: null,
      ...extra,
    });
    let target;
    let from;
    if (word === null) {
      target = HOME;
      from = "none";
    } else if (word.text === "-") {
      if (!state.oldpwd) return fail("bash: cd: OLDPWD not set", { from: "oldpwd" });
      target = state.oldpwd;
      from = "oldpwd";
    } else {
      target = expand(word);
      from = target !== word.text ? "tilde" : target.startsWith("/") ? "root" : "pwd";
    }
    const result = walk(state.pwd, target, true);
    if (!result.ok) {
      const err = `bash: cd: ${target}: ${REASON[result.failed.reason]}`;
      return fail(err, { from, target, steps: result.steps, failed: result.failed });
    }
    const next = { pwd: result.path, oldpwd: state.pwd };
    const out = from === "oldpwd" ? next.pwd : null; // cd - prints where it went
    return { ok: true, state: next, out, err: null, from, target, steps: result.steps, failed: null };
  }

  function ls(state, args) {
    let all = false;
    const names = [];
    for (const w of args) {
      if (w.text.startsWith("-")) {
        if (w.text !== "-a") return { note: "This lab's ls knows one option: -a." };
        all = true;
      } else names.push(expand(w));
    }
    if (names.length > 1) return { note: "List one folder at a time in this lab." };
    const name = names.length ? names[0] : ".";
    const result = walk(state.pwd, name, false);
    if (!result.ok) return { err: [`ls: cannot access '${name}': ${REASON[result.failed.reason]}`] };
    const path = result.path.replace(DOUBLE, "/");
    if (kind(path) === "file") return { out: [name] };
    const list = children(path).filter((n) => all || !n.startsWith("."));
    const shown = all ? [".", "..", ...list] : list;
    return { out: shown.length ? [shown.join("  ")] : [] };
  }

  const VARS = { PWD: "pwd", OLDPWD: "oldpwd", HOME: "home" };

  // Runs one typed line in the explorer: cd, pwd, ls [-a] [path] and echo $PWD / $OLDPWD /
  // $HOME. Anything else gets a note rather than an invented shell message.
  // Returns {state, out: [lines], err: [lines], note, cd}.
  function exec(state, line) {
    const reply = (extra) => ({ state, out: [], err: [], note: null, cd: null, ...extra });
    const parsed = words(line);
    if (parsed.error) return reply({ note: "Close the quote: this terminal reads one line at a time." });
    const [cmd, ...args] = parsed.words;
    if (!cmd) return reply({});
    if (args.some((w) => w.text === "")) return reply({ note: "An empty argument is not part of this lab." });
    if (cmd.text === "cd") {
      if (args.length > 1) return reply({ err: ["bash: cd: too many arguments"] });
      const r = cd(state, args[0] || null);
      return reply({ state: r.state, out: r.out ? [r.out] : [], err: r.err ? [r.err] : [], cd: r });
    }
    if (cmd.text === "pwd") {
      if (args.length) return reply({ note: "Here pwd takes no arguments." });
      return reply({ out: [state.pwd] });
    }
    if (cmd.text === "ls") {
      const r = ls(state, args);
      return reply({ out: r.out || [], err: r.err || [], note: r.note || null });
    }
    const m =
      cmd.text === "echo" && args.length === 1 ? /^(["']?)\$(PWD|OLDPWD|HOME)\1$/.exec(args[0].raw) : null;
    if (m) {
      if (m[1] === "'") return reply({ out: [args[0].text] }); // single quotes: no expansion
      const value = m[2] === "HOME" ? HOME : state[VARS[m[2]]] || "";
      return reply({ out: [value] });
    }
    return reply({ note: "This terminal understands cd, pwd, ls, ls -a and echo $PWD, $OLDPWD or $HOME." });
  }

  // The relative path from one directory to another: "../tests", "src/expense_tracker", ".".
  function relative(from, to) {
    const a = from.split("/").filter(Boolean);
    const b = to.split("/").filter(Boolean);
    let same = 0;
    while (same < a.length && same < b.length && a[same] === b[same]) same += 1;
    const parts = [...a.slice(same).map(() => ".."), ...b.slice(same)];
    return parts.length ? parts.join("/") : ".";
  }

  const tildeForm = (path) =>
    path === HOME || path.startsWith(HOME + "/") ? "~" + path.slice(HOME.length) : null;

  // Realistic slips that point at nothing: the package folder's underscore, a missing "s",
  // a forgotten "code/".
  const SLIPS = [
    [/expense_tracker/, "expense-tracker"],
    [/expense-tracker/, "expense_tracker"],
    [/tests/, "test"],
    [/\/code\//, "/"],
    [/^src/, "scr"],
    [/workflows/, "workflow"],
  ];

  const { pick } = SD.util;
  const KINDS = [
    "down",
    "up",
    "across",
    "absolute",
    "dot",
    "home",
    "tilde",
    "dash",
    "missing",
    "file",
    "top",
    "sequence",
  ];
  const STEP_KINDS = ["down", "up", "across", "absolute", "tilde", "home", "dash"];

  // The argument for one kind of task from a state, as {arg} (arg null is a plain "cd"), or
  // null when that kind makes no sense here (nothing below a leaf folder, say).
  function argFor(k, { pwd, oldpwd }, random) {
    const others = PLACES.filter((p) => p !== pwd);
    const ups = (n) => Array.from({ length: n }, () => "..").join("/");
    switch (k) {
      case "down": {
        const below = DIRS.filter((d) => d.startsWith(join(pwd, "")) && d !== pwd && !d.includes("/.git"));
        return below.length ? { arg: plain(relative(pwd, pick(random, below))) } : null;
      }
      case "up":
        return depth(pwd) ? { arg: plain(ups(1 + Math.floor(random() * Math.min(depth(pwd), 3)))) } : null;
      case "across": {
        const ups2 = (rel) => rel.split("/").filter((s) => s === "..").length;
        const targets = others.filter((p) => {
          const rel = relative(pwd, p);
          return rel.startsWith("../") && !rel.endsWith("..") && ups2(rel) <= 2;
        });
        return targets.length ? { arg: plain(relative(pwd, pick(random, targets))) } : null;
      }
      case "absolute":
        return { arg: plain(pick(random, others)) };
      case "dot":
        return { arg: plain(".") };
      case "home":
        return { arg: random() < 0.5 ? plain("~") : null };
      case "tilde": {
        const inside = others.filter((p) => p.startsWith(HOME + "/"));
        return { arg: plain(tildeForm(pick(random, inside))) };
      }
      case "dash":
        return oldpwd && oldpwd !== pwd ? { arg: plain("-") } : null;
      case "missing": {
        for (let tries = 0; tries < 30; tries += 1) {
          const target = pick(
            random,
            others.filter((p) => p !== "/"),
          );
          const form = pick(random, [relative(pwd, target), target, tildeForm(target) || target]);
          const slips = SLIPS.filter(([re]) => re.test(form));
          if (!slips.length) continue;
          const [re, to] = pick(random, slips);
          const arg = plain(form.replace(re, to));
          if (!cd({ pwd, oldpwd }, arg).ok) return { arg };
        }
        return null;
      }
      case "file": {
        // A file near where you stand, the way the slip happens: "cd README.md", "cd ../cli.py".
        const near = FILES.filter((f) => {
          const rel = relative(pwd, f).split("/");
          return rel.length <= 3 && rel.filter((s) => s === "..").length <= 1;
        });
        return near.length ? { arg: plain(relative(pwd, pick(random, near))) } : null;
      }
      case "top":
        return { arg: plain(ups(depth(pwd) + 1)) };
      default:
        throw new Error(`unknown task kind ${k}`);
    }
  }

  // One drill task: {kind, start: {pwd, oldpwd}, args: [word | null, ...]} with one cd, or two
  // or three for "sequence" (where cd - often comes last, so OLDPWD has to be tracked).
  function task(random) {
    for (;;) {
      const kind = pick(random, KINDS);
      const pwd = kind === "top" && random() < 0.4 ? "/" : pick(random, PLACES);
      const start = {
        pwd,
        oldpwd: pick(
          random,
          PLACES.filter((p) => p !== pwd),
        ),
      };
      if (kind !== "sequence") {
        const got = argFor(kind, start, random);
        if (got) return { kind, start, args: [got.arg] };
        continue;
      }
      const n = 2 + Math.floor(random() * 2);
      const args = [];
      let state = start;
      for (let i = 0; i < n; i += 1) {
        const sub = i === n - 1 && random() < 0.6 ? "dash" : pick(random, STEP_KINDS);
        const got = argFor(sub, state, random);
        if (!got) continue;
        args.push(got.arg);
        state = cd(state, got.arg).state;
      }
      if (args.length >= 2) return { kind, start, args };
    }
  }

  // Runs cd arguments one after the other from a start: {state, results}.
  function run(start, args) {
    let state = start;
    const results = args.map((arg) => {
      const r = cd(state, arg);
      state = r.state;
      return r;
    });
    return { state, results };
  }

  // A typed prediction of what pwd prints. ok: the right directory; exact: written the way pwd
  // prints it (pwd never prints ~ or a trailing slash).
  function checkPrediction(expected, typed) {
    const raw = String(typed).trim();
    if (raw === expected) return { ok: true, exact: true };
    let path = raw.startsWith("~") ? expand(plain(raw)) : raw;
    if (path.length > 1) path = path.replace(/\/+$/, "");
    return { ok: path === expected, exact: false };
  }

  const commandText = (arg) => (arg === null ? "cd" : `cd ${arg.raw}`);

  // How one cd went, in sentences, from the state before it. Commands, names and paths are
  // wrapped in backticks.
  function explain(before, arg, r) {
    const q = (text) => `\`${text}\``;
    const cmd = q(commandText(arg));
    const out = [];
    if (r.from === "none") out.push(`${cmd} with no argument goes to your home folder, ${q(HOME)}.`);
    else if (r.from === "oldpwd") {
      if (!r.target) return [`${cmd} goes back to OLDPWD, but OLDPWD is not set: nowhere to go back to.`];
      out.push(`${cmd} goes back to OLDPWD, ${q(r.target)}, and prints it.`);
    } else if (r.from === "tilde")
      out.push(`The shell turns \`~\` into your home folder before cd runs, so the path is ${q(r.target)}.`);
    else if (r.from === "root")
      out.push(`${q(arg.text)} starts with \`/\`, so it is absolute: it starts at the root.`);
    else out.push(`${q(arg.text)} is relative: it starts in the current directory, ${q(before.pwd)}.`);
    const moves = r.steps.some((s) => s.part === "." || s.part === "..") || r.from === "pwd";
    if (moves && r.steps.length) {
      let here = r.from === "pwd" ? before.pwd.replace(/^\/\/(?!\/)/, "/") : "/";
      const parts = r.steps.map((s) => {
        let text;
        if (s.part === "..")
          text =
            here === "/" ? "`..` stays at `/` (the root is its own parent)" : `\`..\` goes up to ${q(s.dir)}`;
        else if (s.part === ".") text = `\`.\` stays in ${q(s.dir)}`;
        else text = `${q(s.part)} goes into ${q(s.dir)}`;
        here = s.dir;
        return text;
      });
      out.push(`Then ${parts.join(", ")}.`);
    }
    if (r.failed) {
      const where = q(r.failed.at);
      out.push(
        r.failed.reason === "file"
          ? `${q(r.failed.part)} in ${where} is a file, not a directory, so bash prints an error.`
          : `There is no ${q(r.failed.part)} in ${where}, so bash prints an error.`,
      );
      out.push("A failed cd changes nothing: pwd and OLDPWD stay as they were.");
      return out;
    }
    out.push(
      r.state.pwd === before.pwd
        ? `pwd still prints ${q(r.state.pwd)}, and OLDPWD becomes that same folder.`
        : `pwd now prints ${q(r.state.pwd)}, and OLDPWD becomes ${q(before.pwd)}.`,
    );
    return out;
  }

  return {
    HOME,
    PROJECT,
    PLACES,
    KINDS,
    kind,
    children,
    treeLines,
    words,
    expand,
    plain,
    walk,
    cd,
    exec,
    relative,
    task,
    run,
    checkPrediction,
    commandText,
    explain,
  };
})();
