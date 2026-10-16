// Exit codes and chains: commands with given exit statuses joined by &&, || and ;, on one line or
// in a script, with or without set -e. bash's rules: ";" and a new line separate lists; inside a
// list && and || have equal precedence and group from the left, so "a || b && c" is
// "(a || b) && c". A list's status is that of the last command that ran. With set -e the script
// stops at a failing command unless it is followed by && or || in its list (a non-final part).
SD.chains = (() => {
  const CHECKS = [
    "uv run ruff check .",
    "uv run ruff format --check .",
    "uv run mypy src tests",
    "uv run pytest",
  ];

  // Splits text into lists of commands. Quotes and backslash escapes are respected, a "#" that
  // starts a word comments out the rest of the line, a backslash before a new line continues
  // the line, and && or || at the end of a line continue into the next. A "set" line whose
  // options include e (set -e, set -euo pipefail) turns on errexit for the lists after it.
  // Returns {lists: [{errexit, sep, items: [{index, op}]}], commands: [text]}, where sep is what
  // came before the list (null for the first, ";" or a new line); throws on a syntax error.
  function parse(text) {
    const lists = [];
    const commands = [];
    let errexit = false;
    let items = [];
    let current = "";
    let op = null;
    let quote = null;
    let pendingOp = false;

    const endCommand = (nextOp) => {
      const cmd = current.trim();
      current = "";
      if (!cmd) {
        if (nextOp || op)
          throw new SyntaxError(`a command is missing ${nextOp ? `before ${nextOp}` : `after ${op}`}`);
        return;
      }
      if (/^set\s/.test(cmd) && items.length === 0 && !nextOp) {
        if (/(^|\s)-[a-z]*e|-o\s+errexit/.test(cmd)) errexit = true;
        if (/(^|\s)\+[a-z]*e|\+o\s+errexit/.test(cmd)) errexit = false;
        return;
      }
      items.push({ index: commands.length, op });
      commands.push(cmd);
      op = nextOp;
    };
    let sep = null;
    const endList = (next) => {
      endCommand(null);
      if (items.length) {
        lists.push({ errexit, sep, items });
        sep = next;
      }
      items = [];
      op = null;
    };

    const src = String(text);
    for (let i = 0; i < src.length; i += 1) {
      const ch = src[i];
      if (quote) {
        current += ch;
        if (ch === "\\" && quote === '"' && i + 1 < src.length) current += src[(i += 1)];
        else if (ch === quote) quote = null;
        continue;
      }
      if (ch === "\\" && src[i + 1] === "\n") {
        i += 1;
        current += " ";
        continue;
      }
      if (ch === "\\" && i + 1 < src.length) {
        current += ch + src[(i += 1)];
        continue;
      }
      if (ch === '"' || ch === "'") {
        quote = ch;
        current += ch;
        pendingOp = false;
        continue;
      }
      if (ch === "#" && (current === "" || /\s$/.test(current))) {
        while (i + 1 < src.length && src[i + 1] !== "\n") i += 1;
        continue;
      }
      const two = src.slice(i, i + 2);
      if (two === "&&" || two === "||") {
        endCommand(two);
        pendingOp = true;
        i += 1;
        continue;
      }
      if (ch === ";" || ch === "\n") {
        if (ch === "\n" && pendingOp && current.trim() === "") continue;
        endList(ch);
        pendingOp = false;
        continue;
      }
      // A lone & runs a command in the background; inside 2>&1 or &> it is a redirection.
      if (ch === "&" && !/[<>]$/.test(current) && src[i + 1] !== ">") {
        throw new SyntaxError("a single & (run in the background) is not part of this lab");
      }
      if (!/\s/.test(ch)) pendingOp = false;
      current += ch;
    }
    if (quote) throw new SyntaxError("a quote is not closed");
    if (op && current.trim() === "") throw new SyntaxError(`a command is missing after ${op}`);
    endList(null);
    return { lists, commands };
  }

  // Runs a parsed text with the status each command would exit with (statuses[index]).
  // Returns {steps, status, stoppedAt}. One step per command, in order:
  // {index, ran, status, why, before, beforeFrom, exitHere, ignored}; why is "first" (opens a
  // list), "and-run", "and-skip", "or-run", "or-skip" or "stopped" (set -e ended the script
  // earlier); before is the list's status when the command's turn came (null when it opens the
  // list) and beforeFrom the command that set it. status is $? at the end, which for a script
  // is its exit status; stoppedAt is the command where set -e stopped the script, or null.
  function evaluate(parsed, statuses) {
    const steps = [];
    let last = 0;
    let stoppedAt = null;
    for (const list of parsed.lists) {
      let status = null;
      let from = null;
      list.items.forEach((item, k) => {
        const step = {
          index: item.index,
          ran: false,
          status: null,
          why: "first",
          before: status,
          beforeFrom: from,
        };
        step.exitHere = false;
        step.ignored = false;
        steps.push(step);
        if (stoppedAt !== null) {
          step.why = "stopped";
          return;
        }
        if (k > 0) {
          const ok = status === 0;
          step.why = item.op === "&&" ? (ok ? "and-run" : "and-skip") : ok ? "or-skip" : "or-run";
          if (step.why.endsWith("skip")) return;
        }
        step.ran = true;
        step.status = statuses[item.index];
        status = step.status;
        from = item.index;
        if (list.errexit && status !== 0) {
          if (k === list.items.length - 1) {
            step.exitHere = true;
            stoppedAt = item.index;
          } else step.ignored = true;
        }
      });
      if (status !== null) last = status;
    }
    return { steps, status: last, stoppedAt };
  }

  const tick = (text) => `\`${text}\``;

  // Why a command ran or not, in one sentence; commands are wrapped in backticks.
  function explain(parsed, step) {
    const cmd = tick(parsed.commands[step.index]);
    const list = parsed.lists.find((l) => l.items.some((it) => it.index === step.index));
    const so =
      step.before === null
        ? ""
        : `the status so far is ${step.before}, from ${tick(parsed.commands[step.beforeFrom])}`;
    switch (step.why) {
      case "first":
        if (list.sep === ";") return `${cmd} comes after ;, which runs it whatever happened before.`;
        if (list.sep === "\n") {
          return list.errexit
            ? `${cmd} is on the next line and set -e has not stopped the script, so it runs.`
            : `${cmd} is on the next line, so it runs: without set -e a script goes on after a failure.`;
        }
        return `${cmd} comes first, so it runs.`;
      case "and-run":
        return `${cmd} runs: && runs it only after success, and ${so}.`;
      case "and-skip":
        return `${cmd} is skipped: && runs it only after success, and ${so}.`;
      case "or-run":
        return `${cmd} runs: || runs it only after a failure, and ${so}.`;
      case "or-skip":
        return `${cmd} is skipped: || runs it only after a failure, and ${so}.`;
      default:
        return `${cmd} never runs: set -e has already stopped the script.`;
    }
  }

  // What set -e did with a failing command, or null when it had nothing to do.
  function errexitNote(parsed, step) {
    const cmd = tick(parsed.commands[step.index]);
    if (step.exitHere) {
      return (
        `${cmd} failed as the last part of its list, so set -e stops the script here, with status ` +
        `${step.status}.`
      );
    }
    if (step.ignored) {
      return (
        `${cmd} failed, but it is followed by && or ||: set -e treats it as a test, not an error, and ` +
        `the script goes on.`
      );
    }
    return null;
  }

  // How bash groups a list that mixes && and ||: "a || b && c" -> "(a || b) && c". Null when
  // every operator is the same (the grouping changes nothing then).
  function grouped(parsed, list) {
    const ops = new Set(list.items.slice(1).map((it) => it.op));
    if (ops.size < 2) return null;
    let text = parsed.commands[list.items[0].index];
    list.items.slice(1).forEach((it, i) => {
      if (i > 0) text = `(${text})`;
      text = `${text} ${it.op} ${parsed.commands[it.index]}`;
    });
    return text;
  }

  // Why $? ends as it does, in one or two sentences.
  function finalNote(parsed, result) {
    const ran = result.steps.filter((s) => s.ran);
    const last = ran[ran.length - 1];
    const cmd = tick(parsed.commands[last.index]);
    if (result.stoppedAt !== null) {
      return `set -e stopped the script at ${cmd}, so the script exits with ${result.status}.`;
    }
    const after = result.steps.some((s) => s.index > last.index);
    return (
      `The last command that ran is ${cmd}, with status ${last.status}, so $? is ${result.status}.` +
      (after ? " The commands after it were skipped, and a skipped command leaves $? as it was." : "")
    );
  }

  // The course's own cases, with the statuses that make the point. lesson is shown after
  // checking.
  const EXAMPLES = [
    {
      mode: "line",
      title: "The rubric's check, formatting fails",
      text: CHECKS.join(" && "),
      statuses: [0, 1, 0, 0],
      lesson:
        "The first failing check stops the line, and the line exits with its status: mypy and pytest never ran.",
    },
    {
      mode: "line",
      title: "The same check written with ;",
      text: CHECKS.join("; "),
      statuses: [1, 0, 0, 0],
      lesson:
        "With ; every check runs and only the last status counts: a lint error followed by passing tests " +
        "exits 0, and anything that trusts the exit code sees green.",
    },
    {
      mode: "line",
      title: "Report ok, or report failed",
      text: 'uv run expenses report nosuch.csv && echo "report ok" || echo "report failed"',
      statuses: [1, 0, 0],
      lesson:
        "The report failed, so && skipped the first echo and || ran the second. The line ends with echo's 0.",
    },
    {
      mode: "line",
      title: "A fallback that hides the failure",
      text: 'uv run pytest || echo "tests failed"',
      statuses: [1, 0],
      lesson:
        "The message is honest but the status is not: echo succeeded, so the line exits 0 and CI would see green.",
    },
    {
      mode: "line",
      title: "false && x || y",
      text: 'false && echo "never" || echo "fallback"',
      statuses: [1, 0, 0],
      lesson:
        "It reads as (false && echo never) || echo fallback: the skipped echo leaves false's 1 in place, so || runs.",
    },
    {
      mode: "line",
      title: "a || b && c",
      text: 'grep clothing expenses.csv || echo "no clothing" && echo "done"',
      statuses: [1, 0, 0],
      lesson:
        "It reads as (grep || echo) && echo: grep found nothing (1), the fallback ran and succeeded, so done " +
        "runs too.",
    },
    {
      mode: "line",
      title: "Equal precedence",
      text: "uv run ruff check . || uv run ruff format --check . && uv run pytest",
      statuses: [0, 0, 1],
      lesson:
        "&& does not bind tighter than ||: the line is (ruff check || ruff format) && pytest, so pytest runs " +
        "after the passing lint and its failure is the line's status.",
    },
    {
      mode: "line",
      title: "&& then || is not if/else",
      text: 'uv run mypy src tests && uv run pytest || echo "checks failed"',
      statuses: [0, 1, 0],
      lesson:
        "|| answers whatever ran last, here pytest's failure, not mypy's success. The line exits 0 because echo did.",
    },
    {
      mode: "script",
      title: "check.sh, mypy fails",
      text: ["#!/usr/bin/env bash", "set -euo pipefail", "", ...CHECKS].join("\n"),
      statuses: [0, 0, 1, 0],
      lesson:
        "set -e gives the same stop at the first failure as the && chain: pytest never ran and the script exits 1.",
    },
    {
      mode: "script",
      title: "check.sh, all green",
      text: ["#!/usr/bin/env bash", "set -euo pipefail", "", ...CHECKS, 'echo "All checks passed"'].join(
        "\n",
      ),
      statuses: [0, 0, 0, 0, 0],
      lesson:
        "Every line ran and the last one, echo, exited 0. The message is only printed when every check passed.",
    },
    {
      mode: "script",
      title: "Two checks on one line",
      text: [
        "#!/usr/bin/env bash",
        "set -e",
        "",
        `${CHECKS[0]} && ${CHECKS[1]}`,
        CHECKS[2],
        CHECKS[3],
        'echo "All checks passed"',
      ].join("\n"),
      statuses: [1, 0, 0, 0, 0],
      lesson:
        "A failure followed by && is a test, not an error, so set -e lets the script go on: it prints All " +
        "checks passed and exits 0 with a lint error.",
    },
    {
      mode: "script",
      title: "The failing check ends its line",
      text: ["#!/usr/bin/env bash", "set -e", "", `${CHECKS[0]} && ${CHECKS[1]}`, CHECKS[3]].join("\n"),
      statuses: [0, 1, 0],
      lesson:
        "This time the failure is the last part of its list, so set -e stops the script there with status 1.",
    },
    {
      mode: "script",
      title: "A failure on the last line",
      text: ["#!/usr/bin/env bash", "set -e", "", CHECKS[2], `${CHECKS[0]} && ${CHECKS[3]}`].join("\n"),
      statuses: [0, 1, 0],
      lesson:
        "set -e does not stop a failure followed by &&, but nothing comes after it: the script ends with " +
        "that list's status, 1.",
    },
    {
      mode: "script",
      title: "No set -e",
      text: ["#!/usr/bin/env bash", "", ...CHECKS, 'echo "All checks passed"'].join("\n"),
      statuses: [1, 0, 0, 0, 0],
      lesson:
        "Without set -e a script runs every line whatever fails, and exits with the last command's status: 0.",
    },
    {
      mode: "script",
      title: "No match is an answer",
      text: ["#!/usr/bin/env bash", "set -e", "", "grep clothing expenses.csv || true", 'echo "done"'].join(
        "\n",
      ),
      statuses: [1, 0, 0],
      lesson:
        "grep's 1 means no match. Followed by || true it is no longer the end of its list, so set -e lets it pass.",
    },
  ];

  // ---------------------------------------------------------------- drills

  // Commands with the statuses they can really exit with in the course project: grep finds
  // dining (0) but no clothing (1) in expenses.csv, grep on a missing file is trouble (2), the
  // report on a missing file exits 1, and true, false and echo never vary.
  const POOL = {
    "uv run ruff check .": [0, 1],
    "uv run ruff format --check .": [0, 1],
    "uv run mypy src tests": [0, 1],
    "uv run pytest": [0, 1],
    "uv sync --locked": [0, 1],
    "uv run expenses report expenses.csv": [0],
    "uv run expenses report nosuch.csv": [1],
    "grep dining expenses.csv": [0],
    "grep clothing expenses.csv": [1],
    "grep dining nosuch.csv": [2],
    true: [0],
    false: [1],
    'echo "ok"': [0],
    'echo "failed"': [0],
    'echo "done"': [0],
    'echo "All checks passed"': [0],
  };
  const TOOLS = Object.keys(POOL).filter((c) => !/^(echo|true|false)\b/.test(c));
  const ANY = Object.keys(POOL).filter((c) => c !== 'echo "All checks passed"');

  const { pick } = SD.util;

  // Each shape returns the text of one line, filled from the pool.
  const LINE_SHAPES = [
    () => CHECKS.join(" && "),
    () => CHECKS.join("; "),
    (r) => `${pick(r, CHECKS)} || echo "failed"`,
    (r) => `${pick(r, TOOLS)} && echo "ok" || echo "failed"`,
    (r) => `${pick(r, TOOLS)} || ${pick(r, TOOLS)} && echo "done"`,
    (r) => `false && ${pick(r, TOOLS)} || echo "done"`,
    (r) => `${pick(r, CHECKS)} || ${pick(r, CHECKS)} && ${pick(r, CHECKS)}`,
    (r) => {
      let text = pick(r, TOOLS);
      const n = 3 + Math.floor(r() * 2);
      for (let i = 1; i < n; i += 1) {
        const op = pick(r, ["&&", "&&", "||", ";"]);
        text += `${op === ";" ? ";" : ` ${op}`} ${pick(r, ANY)}`;
      }
      return text;
    },
  ];

  // Each shape returns the lines of a script after its shebang.
  const SCRIPT_SHAPES = [
    () => ["set -e", ...CHECKS],
    () => ["set -euo pipefail", ...CHECKS, 'echo "All checks passed"'],
    () => ["set -e", `${CHECKS[0]} && ${CHECKS[1]}`, CHECKS[2], CHECKS[3], 'echo "All checks passed"'],
    () => [...CHECKS, 'echo "All checks passed"'],
    (r) => ["set -e", `${pick(r, TOOLS)} || true`, 'echo "done"'],
    (r) => ["set -e", `${pick(r, CHECKS)} || echo "failed"`, pick(r, CHECKS)],
    (r) => ["set -e", pick(r, CHECKS), `${pick(r, CHECKS)} && ${pick(r, CHECKS)}`],
  ];

  function statusesFor(parsed, random) {
    return parsed.commands.map((cmd) => {
      if (!POOL[cmd]) throw new Error(`no exit statuses known for ${cmd}`);
      return pick(random, POOL[cmd]);
    });
  }

  // A practice task: {mode: "line" | "script", text, parsed, statuses}.
  function drill(mode, random) {
    const shapes = mode === "script" ? SCRIPT_SHAPES : LINE_SHAPES;
    const raw = pick(random, shapes)(random);
    const text = mode === "script" ? ["#!/usr/bin/env bash", ...raw].join("\n") : raw;
    const parsed = parse(text);
    return { mode, text, parsed, statuses: statusesFor(parsed, random) };
  }

  // An answer {runs: [bool per command], status: typed text} against the evaluation.
  function check(result, answer) {
    const runs = result.steps.map((s) => Boolean(answer.runs[s.index]) === s.ran);
    const typed = String(answer.status ?? "").trim();
    const statusOk = /^\d+$/.test(typed) && Number(typed) === result.status;
    return { runs, statusOk, ok: statusOk && runs.every(Boolean) };
  }

  return { CHECKS, POOL, EXAMPLES, parse, evaluate, explain, errexitNote, grouped, finalNote, drill, check };
})();
