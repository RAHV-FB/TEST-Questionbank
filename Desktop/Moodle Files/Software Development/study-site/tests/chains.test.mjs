// SD.chains: parsing &&, || and ; (and scripts with set -e), evaluating them with given exit
// statuses, the explanations, the drills and the answer check. The last tests replay the drills
// in a real bash (and in dash, a plain POSIX sh) and compare which commands ran and $?.
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { load } from "./helpers/load.mjs";

const { chains, util } = load("util.js", "chains.js");

// Runs a text where each command is a letter and statuses are given by letter.
function run(text, statusByCommand) {
  const parsed = chains.parse(text);
  const statuses = parsed.commands.map((c) => {
    if (!(c in statusByCommand)) throw new Error(`no status for ${c}`);
    return statusByCommand[c];
  });
  const result = chains.evaluate(parsed, statuses);
  const ran = result.steps.filter((s) => s.ran).map((s) => parsed.commands[s.index]);
  return { parsed, result, ran, status: result.status };
}

test("parse: && and || join commands, ; and new lines separate lists", () => {
  const p = chains.parse("a && b || c; d");
  assert.deepEqual(p.commands, ["a", "b", "c", "d"]);
  assert.deepEqual(
    p.lists.map((l) => l.items.map((i) => i.op)),
    [[null, "&&", "||"], [null]],
  );
  assert.deepEqual(
    p.lists.map((l) => l.sep),
    [null, ";"],
  );
  assert.deepEqual(
    chains.parse("a\nb").lists.map((l) => l.sep),
    [null, "\n"],
  );
  assert.deepEqual(
    chains.parse("grep x f | wc -l && y").commands,
    ["grep x f | wc -l", "y"],
    "a pipe is part of a command",
  );
});

test("parse: quotes, comments, continuations and redirections", () => {
  assert.deepEqual(chains.parse("echo \"a && b; c\" || echo 'd || e'").commands, [
    'echo "a && b; c"',
    "echo 'd || e'",
  ]);
  assert.deepEqual(chains.parse('echo "say \\"hi\\" && go"').commands, ['echo "say \\"hi\\" && go"']);
  assert.deepEqual(chains.parse("echo a\\;b && c").commands, ["echo a\\;b", "c"], "an escaped ; is text");
  assert.deepEqual(chains.parse("#!/usr/bin/env bash\n# check\na # trailing\nb#c").commands, ["a", "b#c"]);
  const rubric =
    "uv run ruff check . && uv run ruff format --check . \\\n&& uv run mypy src tests && uv run pytest";
  const p = chains.parse(rubric);
  assert.equal(p.lists.length, 1, "a backslash before the new line continues the line");
  assert.deepEqual(p.commands, chains.CHECKS);
  assert.equal(chains.parse("a &&\n  b").lists.length, 1, "&& at the end of a line continues it");
  assert.deepEqual(chains.parse("cmd > out.txt 2>&1 && x &> log").commands, [
    "cmd > out.txt 2>&1",
    "x &> log",
  ]);
});

test("parse: set lines are settings, not commands", () => {
  const p = chains.parse(
    "#!/usr/bin/env bash\nset -euo pipefail\na\nset +e\nb\nset -o errexit\nc\nset -o pipefail\nd",
  );
  assert.deepEqual(p.commands, ["a", "b", "c", "d"]);
  assert.deepEqual(
    p.lists.map((l) => l.errexit),
    [true, false, true, true],
  );
  assert.equal(chains.parse("set -e\na").lists[0].errexit, true);
  assert.equal(chains.parse("a").lists[0].errexit, false);
});

test("parse: syntax errors fail loudly", () => {
  assert.throws(() => chains.parse("a && && b"), SyntaxError);
  assert.throws(() => chains.parse("&& a"), SyntaxError);
  assert.throws(() => chains.parse("a ||"), SyntaxError);
  assert.throws(() => chains.parse('echo "open'), SyntaxError);
  assert.throws(() => chains.parse("a & b"), SyntaxError);
});

test("&& runs on success, || on failure, ; always", () => {
  assert.deepEqual(run("a && b", { a: 0, b: 0 }).ran, ["a", "b"]);
  assert.deepEqual(run("a && b", { a: 1, b: 0 }).ran, ["a"]);
  assert.equal(run("a && b", { a: 1, b: 0 }).status, 1, "a skipped command leaves the status as it was");
  assert.deepEqual(run("a || b", { a: 0, b: 1 }).ran, ["a"]);
  assert.equal(run("a || b", { a: 0, b: 1 }).status, 0);
  assert.deepEqual(run("a || b", { a: 2, b: 0 }).ran, ["a", "b"]);
  assert.deepEqual(run("a; b", { a: 1, b: 0 }).ran, ["a", "b"]);
  assert.equal(
    run("a; b", { a: 1, b: 0 }).status,
    0,
    "; hides the failure: the line's status is the last command's",
  );
});

test("&& and || have equal precedence and group from the left", () => {
  // a || b && c is (a || b) && c
  let r = run("a || b && c", { a: 0, b: 1, c: 1 });
  assert.deepEqual(r.ran, ["a", "c"], "c runs although b was skipped: the status so far is a's 0");
  assert.equal(r.status, 1);
  r = run("a || b && c", { a: 1, b: 1, c: 0 });
  assert.deepEqual(r.ran, ["a", "b"]);
  assert.equal(r.status, 1);
  r = run("true || false && false", { true: 0, false: 1 });
  assert.equal(r.status, 1, "in C-like precedence this would be 0");
  // false && x || y is (false && x) || y
  r = run("false && x || y", { false: 1, x: 0, y: 0 });
  assert.deepEqual(r.ran, ["false", "y"]);
  assert.equal(r.status, 0);
  const skip = r.result.steps[1];
  assert.equal(skip.why, "and-skip");
  const y = r.result.steps[2];
  assert.deepEqual([y.why, y.before, y.beforeFrom], ["or-run", 1, 0], "y sees false's status, x never ran");
  r = run("a && b || c", { a: 0, b: 0, c: 0 });
  assert.deepEqual(r.ran, ["a", "b"]);
  r = run("a && b || c", { a: 0, b: 1, c: 5 });
  assert.deepEqual(r.ran, ["a", "b", "c"], "&& ... || is not if/else: c runs when b fails too");
  assert.equal(r.status, 5);
});

test("the rubric's check chain stops at the first failing check", () => {
  const line = chains.CHECKS.join(" && ");
  const p = chains.parse(line);
  let r = chains.evaluate(p, [0, 1, 0, 0]);
  assert.deepEqual(
    r.steps.map((s) => s.ran),
    [true, true, false, false],
  );
  assert.equal(r.status, 1);
  r = chains.evaluate(p, [0, 0, 0, 0]);
  assert.equal(r.status, 0);
  r = chains.evaluate(chains.parse(chains.CHECKS.join("; ")), [1, 0, 0, 0]);
  assert.deepEqual(
    r.steps.map((s) => s.ran),
    [true, true, true, true],
  );
  assert.equal(r.status, 0, "with ; a lint error followed by passing tests exits 0");
});

test("set -e stops at a failing command that ends its list", () => {
  const script = (body) => `#!/usr/bin/env bash\nset -e\n${body}`;
  let r = run(script("a\nb\nc"), { a: 0, b: 1, c: 0 });
  assert.deepEqual(r.ran, ["a", "b"]);
  assert.equal(r.status, 1);
  assert.equal(r.result.stoppedAt, 1);
  assert.equal(r.result.steps[2].why, "stopped");
  r = run(script("a\nb\nc"), { a: 0, b: 2, c: 0 });
  assert.equal(r.status, 2, "the script exits with the failing command's status");
  // a failing command followed by && is not an error for set -e
  r = run(script("a && b\nc"), { a: 1, b: 0, c: 0 });
  assert.deepEqual(r.ran, ["a", "c"]);
  assert.equal(r.status, 0);
  assert.equal(r.result.stoppedAt, null);
  assert.equal(r.result.steps[0].ignored, true);
  // ... but the last part of the list is
  r = run(script("a && b\nc"), { a: 0, b: 1, c: 0 });
  assert.deepEqual(r.ran, ["a", "b"]);
  assert.equal(r.result.steps[1].exitHere, true);
  // the same failure on the last line: no stop, yet the script still exits 1
  r = run(script("c\na && b"), { a: 1, b: 0, c: 0 });
  assert.deepEqual(r.ran, ["c", "a"]);
  assert.deepEqual([r.result.stoppedAt, r.status], [null, 1]);
  // || true makes a failure an expected answer
  r = run(script("a || true\nc"), { a: 1, true: 0, c: 0 });
  assert.deepEqual(r.ran, ["a", "true", "c"]);
  assert.equal(r.status, 0);
  // || in the last position still stops when it fails
  r = run(script("a || b\nc"), { a: 1, b: 1, c: 0 });
  assert.deepEqual(r.ran, ["a", "b"]);
  assert.equal(r.status, 1);
});

test("without set -e a script runs every line", () => {
  const r = run("#!/usr/bin/env bash\na\nb\nc", { a: 0, b: 1, c: 0 });
  assert.deepEqual(r.ran, ["a", "b", "c"]);
  assert.equal(r.status, 0);
});

test("explanations name the rule and the status that decided", () => {
  const { parsed, result } = run("false && x || y; z", { false: 1, x: 0, y: 0, z: 0 });
  assert.deepEqual(
    result.steps.map((s) => chains.explain(parsed, s)),
    [
      "`false` comes first, so it runs.",
      "`x` is skipped: && runs it only after success, and the status so far is 1, from `false`.",
      "`y` runs: || runs it only after a failure, and the status so far is 1, from `false`.",
      "`z` comes after ;, which runs it whatever happened before.",
    ],
  );
  const s = run("set -e\na && b\nc\nd", { a: 1, b: 0, c: 3, d: 0 });
  const lines = s.result.steps.map((st) => [chains.explain(s.parsed, st), chains.errexitNote(s.parsed, st)]);
  assert.match(lines[0][1], /followed by && or \|\|: set -e treats it as a test/);
  assert.match(lines[2][0], /next line and set -e has not stopped the script/);
  assert.match(lines[2][1], /set -e stops the script here, with status 3/);
  assert.equal(lines[3][0], "`d` never runs: set -e has already stopped the script.");
  assert.equal(lines[3][1], null);
  const o = run("a || b", { a: 0, b: 0 });
  assert.equal(
    chains.explain(o.parsed, o.result.steps[1]),
    "`b` is skipped: || runs it only after a failure, and the status so far is 0, from `a`.",
  );
});

test("drills: stable per seed, real statuses, every shape parses", () => {
  for (const mode of ["line", "script"]) {
    const a = chains.drill(mode, util.seededRandom(4));
    assert.deepEqual(chains.drill(mode, util.seededRandom(4)), a);
    const random = util.seededRandom(mode === "line" ? 21 : 22);
    const texts = new Set();
    let stops = 0;
    for (let i = 0; i < 400; i += 1) {
      const d = chains.drill(mode, random);
      texts.add(
        d.text.split("\n").length > 1 ? d.text.split("\n").slice(0, 3).join("|") : d.text.slice(0, 20),
      );
      assert.equal(d.statuses.length, d.parsed.commands.length);
      d.parsed.commands.forEach((cmd, k) => assert.ok(chains.POOL[cmd].includes(d.statuses[k]), cmd));
      if (mode === "script") assert.ok(d.text.startsWith("#!/usr/bin/env bash\n"));
      if (chains.evaluate(d.parsed, d.statuses).stoppedAt !== null) stops += 1;
    }
    assert.ok(texts.size > 20, `${mode} drills vary (${texts.size})`);
    if (mode === "script") assert.ok(stops > 50 && stops < 350, `set -e sometimes stops a script (${stops})`);
  }
});

test("check: every tick and the status must match", () => {
  const p = chains.parse("a && b || c");
  const r = chains.evaluate(p, [1, 0, 0]);
  assert.deepEqual(chains.check(r, { runs: [true, false, true], status: "0" }), {
    runs: [true, true, true],
    statusOk: true,
    ok: true,
  });
  assert.deepEqual(chains.check(r, { runs: [true, true, true], status: " 0 " }), {
    runs: [true, false, true],
    statusOk: true,
    ok: false,
  });
  assert.equal(chains.check(r, { runs: [true, false, true], status: "1" }).ok, false);
  assert.equal(chains.check(r, { runs: [true, false, true], status: "" }).statusOk, false);
  assert.equal(chains.check(r, { runs: [true, false, true], status: "0x" }).statusOk, false);
});

test("grouped shows how bash reads a mixed list", () => {
  const show = (text) => {
    const p = chains.parse(text);
    return chains.grouped(p, p.lists[0]);
  };
  assert.equal(show("a || b && c"), "(a || b) && c");
  assert.equal(show("a && b || c && d"), "((a && b) || c) && d");
  assert.equal(show("a && b && c"), null, "one operator: grouping changes nothing");
  assert.equal(show("a"), null);
});

test("finalNote says which command set $? and why", () => {
  const line = run("a && b || c", { a: 1, b: 0, c: 4 });
  assert.equal(
    chains.finalNote(line.parsed, line.result),
    "The last command that ran is `c`, with status 4, so $? is 4.",
  );
  const skipped = run("a && b", { a: 1, b: 0 });
  assert.equal(
    chains.finalNote(skipped.parsed, skipped.result),
    "The last command that ran is `a`, with status 1, so $? is 1. The commands after it were skipped, and a " +
      "skipped command leaves $? as it was.",
  );
  const stop = run("set -e\na\nb", { a: 2, b: 0 });
  assert.equal(
    chains.finalNote(stop.parsed, stop.result),
    "set -e stopped the script at `a`, so the script exits with 2.",
  );
});

test("the course examples parse, carry a status per command, and teach what they say", () => {
  assert.ok(chains.EXAMPLES.length >= 12);
  const outcome = {};
  for (const ex of chains.EXAMPLES) {
    const parsed = chains.parse(ex.text);
    assert.equal(ex.statuses.length, parsed.commands.length, ex.title);
    assert.equal(
      parsed.lists.some((l) => l.errexit),
      ex.mode === "script" && ex.text.includes("set -e"),
      ex.title,
    );
    const r = chains.evaluate(parsed, ex.statuses);
    outcome[ex.title] = [r.steps.map((st) => (st.ran ? 1 : 0)).join(""), r.status, r.stoppedAt];
  }
  assert.deepEqual(outcome, {
    "The rubric's check, formatting fails": ["1100", 1, null],
    "The same check written with ;": ["1111", 0, null],
    "Report ok, or report failed": ["101", 0, null],
    "A fallback that hides the failure": ["11", 0, null],
    "false && x || y": ["101", 0, null],
    "a || b && c": ["111", 0, null],
    "Equal precedence": ["101", 1, null],
    "&& then || is not if/else": ["111", 0, null],
    "check.sh, mypy fails": ["1110", 1, 2],
    "check.sh, all green": ["11111", 0, null],
    "Two checks on one line": ["10111", 0, null],
    "The failing check ends its line": ["110", 1, 1],
    "A failure on the last line": ["110", 1, null],
    "No set -e": ["11111", 0, null],
    "No match is an answer": ["111", 0, null],
  });
});

// The same structure with each command replaced by "r <index> <status>", which prints that it
// ran and returns the status.
function shellText(parsed) {
  let errexit = false;
  const out = ['r() { echo "ran $1"; return $2; }'];
  parsed.lists.forEach((list) => {
    if (list.errexit !== errexit) out.push(list.errexit ? "set -e" : "set +e");
    errexit = list.errexit;
    out.push(list.items.map((it) => `${it.op ? `${it.op} ` : ""}r ${it.index} \${S${it.index}}`).join(" "));
  });
  return out.join("\n") + "\n";
}

function replay(shell, cases) {
  const dir = mkdtempSync(join(tmpdir(), "swdev-chains-"));
  try {
    const lines = [];
    cases.forEach((c, i) => {
      const file = join(dir, `s${i}.sh`);
      writeFileSync(file, shellText(c.parsed));
      const vars = c.statuses.map((s, k) => `S${k}=${s}`).join(" ");
      // A line runs in the shell itself; a script in its own process, as ./check.sh would.
      const body = c.mode === "line" ? `. '${file}'` : `${shell} '${file}'`;
      lines.push(
        `echo "## ${i}"; ( ${vars}; export ${c.statuses.map((_, k) => `S${k}`).join(" ")}; ${body}; echo ` +
          `"status=$?" )`,
      );
    });
    const res = spawnSync(shell, ["-c", lines.join("\n")], {
      encoding: "utf8",
      env: { PATH: "/usr/bin:/bin" },
    });
    assert.equal(res.status, 0, res.stderr);
    return res.stdout.split(/^## \d+\n/m).slice(1);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

for (const shell of ["/bin/bash", "/bin/dash"]) {
  test(`drills and the tricky cases match ${shell}`, { skip: !existsSync(shell) && `no ${shell}` }, () => {
    const cases = [];
    const add = (mode, text, statuses) => cases.push({ mode, text, parsed: chains.parse(text), statuses });
    add("line", "a || b && c", [0, 1, 1]);
    add("line", "a || b && c", [1, 1, 0]);
    add("line", "false && x || y", [1, 0, 0]);
    add("line", "true || false && false", [0, 1, 1]);
    add("script", "set -e\na && b\nc", [1, 0, 0]);
    add("script", "set -e\na && b\nc", [0, 1, 0]);
    add("script", "set -e\nc\na && b", [0, 1, 0]);
    add("script", "set -e\na || true\nc", [1, 0, 0]);
    add("script", "set -e\na\nb\nc", [0, 2, 0]);
    for (const ex of chains.EXAMPLES) add(ex.mode, ex.text, ex.statuses);
    for (const mode of ["line", "script"]) {
      const random = util.seededRandom(mode === "line" ? 7 : 8);
      for (let i = 0; i < 250; i += 1) cases.push(chains.drill(mode, random));
    }
    const blocks = replay(shell, cases);
    assert.equal(blocks.length, cases.length);
    cases.forEach((c, i) => {
      const r = chains.evaluate(c.parsed, c.statuses);
      const want = [...r.steps.filter((s) => s.ran).map((s) => `ran ${s.index}`), `status=${r.status}`];
      assert.deepEqual(blocks[i].trimEnd().split("\n"), want, `${c.text} with ${c.statuses.join(",")}`);
    });
  });
}
