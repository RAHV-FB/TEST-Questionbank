// SD.paths: the fixed tree, bash's cd (PWD and OLDPWD), the explorer's commands and the drill.
// The last test replays hundreds of generated drills in a real bash on a copy of the tree.
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { load } from "./helpers/load.mjs";

const { paths, util } = load("util.js", "paths.js");
const P = paths.PROJECT;
const w = (text) => paths.words(text).words[0];
const at = (pwd, oldpwd = "/tmp") => ({ pwd, oldpwd });
const cd = (state, text) => paths.cd(state, text === null ? null : w(text));

test("the tree holds the project, the template and /etc, /tmp, /usr", () => {
  assert.equal(paths.kind("/"), "dir");
  assert.equal(paths.kind(`${P}/src/expense_tracker`), "dir");
  assert.equal(paths.kind(`${P}/src/expense_tracker/report.py`), "file");
  assert.equal(paths.kind(`${P}/.github/workflows/check.yml`), "file");
  assert.equal(paths.kind("/home/alice/code/project-template"), "dir");
  assert.equal(paths.kind(`${P}/src/expense-tracker`), null);
  assert.deepEqual(paths.children("/"), ["etc", "home", "tmp", "usr"]);
  assert.deepEqual(
    paths.children(P),
    [".git", ".github", "README.md", "expenses.csv", "pyproject.toml", "src", "tests"],
    "byte order: dot names, then capitals, then small letters (as the slide's ls)",
  );
  assert.deepEqual(paths.children(`${P}/tests`), ["test_duplicates.py", "test_io.py", "test_report.py"]);
});

test("treeLines draws the tree like slide 8", () => {
  const lines = paths.treeLines();
  assert.equal(lines[0].name, "/");
  assert.deepEqual(
    lines.slice(1, 4).map((l) => l.prefix + l.name),
    ["├── etc/", "├── home/", "│   └── alice/"],
  );
  assert.equal(lines.at(-1).prefix + lines.at(-1).name, "└── usr/");
  const report = lines.find((l) => l.path === `${P}/src/expense_tracker/report.py`);
  const last = "report.py is the last file in the package";
  assert.equal(report.prefix, "│           │   │       └── ", last);
  assert.equal(lines.length, 25);
});

test("relative and absolute paths, .. and .", () => {
  assert.equal(cd(at(P), "src").state.pwd, `${P}/src`);
  assert.equal(cd(at(P), "src/expense_tracker/").state.pwd, `${P}/src/expense_tracker`);
  assert.equal(cd(at(`${P}/src`), "../tests").state.pwd, `${P}/tests`, "the slide's cd ../tests");
  assert.equal(cd(at(`${P}/src/expense_tracker`), "../..").state.pwd, P);
  assert.equal(cd(at(P), "../project-template").state.pwd, "/home/alice/code/project-template");
  assert.equal(cd(at(P), "/etc").state.pwd, "/etc");
  assert.equal(
    cd(at(P), "/home/alice/code/./expense-tracker/../expense-tracker/tests").state.pwd,
    `${P}/tests`,
  );
  const dot = cd(at(P, "/tmp"), ".");
  assert.deepEqual(dot.state, { pwd: P, oldpwd: P }, "cd . succeeds, so OLDPWD becomes PWD");
});

test("every successful cd moves PWD to OLDPWD; a failed one changes nothing", () => {
  const ok = cd(at(P, "/tmp"), "src");
  assert.deepEqual(ok.state, { pwd: `${P}/src`, oldpwd: P });
  assert.equal(ok.out, null, "cd prints nothing");
  const bad = cd(at(P, "/tmp"), "test");
  assert.equal(bad.ok, false);
  assert.deepEqual(bad.state, { pwd: P, oldpwd: "/tmp" });
  assert.equal(bad.err, "bash: cd: test: No such file or directory");
  assert.deepEqual(bad.failed, { part: "test", at: P, reason: "missing" });
});

test("home: no argument, ~, ~/x, ~alice; a quoted ~ is a plain name", () => {
  assert.equal(cd(at("/tmp"), null).state.pwd, "/home/alice");
  assert.equal(cd(at("/tmp"), null).from, "none");
  assert.equal(cd(at("/tmp"), "~").state.pwd, "/home/alice");
  assert.equal(cd(at("/tmp"), "~/code/expense-tracker/src").state.pwd, `${P}/src`);
  assert.equal(cd(at("/tmp"), "~/code/expense-tracker/src").from, "tilde");
  assert.equal(cd(at("/tmp"), "~alice/code").state.pwd, "/home/alice/code");
  assert.equal(cd(at("/tmp"), "~/").state.pwd, "/home/alice");
  assert.equal(cd(at("/tmp"), '"~"').err, "bash: cd: ~: No such file or directory");
  assert.equal(cd(at("/tmp"), "~bob").err, "bash: cd: ~bob: No such file or directory");
  assert.equal(
    cd(at("/tmp"), '~/"code"').state.pwd,
    "/home/alice/code",
    "the ~ before the slash is unquoted",
  );
  assert.equal(
    cd(at("/tmp"), "~/nosuch").err,
    "bash: cd: /home/alice/nosuch: No such file or directory",
    "bash shows the expanded word",
  );
});

test("cd - goes to OLDPWD and prints it; twice comes back", () => {
  const first = cd(at(`${P}/src`, "/etc"), "-");
  assert.deepEqual(first.state, { pwd: "/etc", oldpwd: `${P}/src` });
  assert.equal(first.out, "/etc");
  const second = paths.cd(first.state, w("-"));
  assert.deepEqual(second.state, { pwd: `${P}/src`, oldpwd: "/etc" });
  assert.equal(second.out, `${P}/src`);
  assert.equal(cd(at(P, null), "-").err, "bash: cd: OLDPWD not set");
  assert.equal(cd(at(P, "/tmp"), '"-"').state.pwd, "/tmp", "quotes are removed before cd sees the -");
});

test("cd .. at / stays at /, however many", () => {
  assert.deepEqual(cd(at("/", "/tmp"), "..").state, { pwd: "/", oldpwd: "/" });
  assert.equal(cd(at("/home/alice"), "../../../..").state.pwd, "/");
  assert.equal(cd(at("/tmp"), "/..").state.pwd, "/");
});

test("a file is not a directory, before or at the end", () => {
  assert.equal(cd(at(P), "README.md").err, "bash: cd: README.md: Not a directory");
  assert.equal(cd(at(P), "README.md/..").err, "bash: cd: README.md/..: Not a directory");
  assert.equal(
    cd(at(P), "nosuch/..").err,
    "bash: cd: nosuch/..: No such file or directory",
    "names are checked before .. removes them",
  );
  assert.equal(cd(at(P), "src/nosuch/../expense_tracker").ok, false);
});

test("a leading // is kept, as bash keeps it; three or more slashes are /", () => {
  assert.equal(cd(at(P), "//").state.pwd, "//");
  assert.equal(cd(at(P), "//tmp").state.pwd, "//tmp");
  assert.equal(cd(at(P), "///").state.pwd, "/");
  assert.equal(cd(at(P), "///tmp").state.pwd, "/tmp");
});

test("words: quotes group and are removed; tilde only when unquoted", () => {
  assert.deepEqual(paths.words("cd  src "), {
    words: [
      { text: "cd", raw: "cd", tilde: false },
      { text: "src", raw: "src", tilde: false },
    ],
  });
  assert.deepEqual(paths.words("cd 'my dir'").words[1], { text: "my dir", raw: "'my dir'", tilde: false });
  assert.equal(paths.words('cd "~"').words[1].tilde, false);
  assert.equal(paths.words("cd ~/x").words[1].tilde, true);
  assert.deepEqual(paths.words('cd "unclosed'), { error: "unmatched quote" });
  assert.deepEqual(paths.words("   "), { words: [] });
});

test("the explorer runs cd, pwd, ls and echo, and says when it cannot", () => {
  const s = at(P, "/home/alice");
  assert.deepEqual(paths.exec(s, "pwd").out, [P]);
  assert.deepEqual(paths.exec(s, "ls").out, ["README.md  expenses.csv  pyproject.toml  src  tests"]);
  assert.deepEqual(paths.exec(s, "ls -a").out, [
    ".  ..  .git  .github  README.md  expenses.csv  pyproject.toml  src  tests",
  ]);
  assert.deepEqual(paths.exec(s, "ls src/expense_tracker").out, ["__init__.py  cli.py  report.py"]);
  assert.deepEqual(paths.exec(s, "ls README.md").out, ["README.md"]);
  assert.deepEqual(paths.exec(s, "ls /home/alice/code/project-template").out, []);
  assert.deepEqual(paths.exec(s, "ls expenses").err, [
    "ls: cannot access 'expenses': No such file or directory",
  ]);
  assert.match(paths.exec(s, "ls -l").note, /one option/);
  assert.deepEqual(paths.exec(s, "echo $OLDPWD").out, ["/home/alice"]);
  assert.deepEqual(paths.exec(s, 'echo "$PWD"').out, [P]);
  assert.deepEqual(paths.exec(s, "echo '$HOME'").out, ["$HOME"], "single quotes stop expansion");
  assert.deepEqual(paths.exec(at(P, null), "echo $OLDPWD").out, [""]);
  assert.deepEqual(paths.exec(s, "cd src tests").err, ["bash: cd: too many arguments"]);
  assert.deepEqual(paths.exec(s, "cd src tests").state, s);
  const moved = paths.exec(s, "cd -");
  assert.deepEqual(moved.out, ["/home/alice"]);
  assert.deepEqual(moved.state, { pwd: "/home/alice", oldpwd: P });
  assert.match(paths.exec(s, "rm -r src").note, /understands cd, pwd, ls/);
  assert.deepEqual(paths.exec(s, "").out, []);
});

test("relative paths between directories", () => {
  assert.equal(paths.relative(`${P}/tests`, `${P}/src/expense_tracker`), "../src/expense_tracker");
  assert.equal(paths.relative(P, `${P}/src`), "src");
  assert.equal(paths.relative(`${P}/src`, P), "..");
  assert.equal(paths.relative(P, P), ".");
  assert.equal(paths.relative("/", "/tmp"), "tmp");
  assert.equal(paths.relative("/tmp", "/"), "..");
});

test("predictions: pwd prints full paths without a trailing slash", () => {
  assert.deepEqual(paths.checkPrediction(`${P}/src`, ` ${P}/src `), { ok: true, exact: true });
  assert.deepEqual(paths.checkPrediction(`${P}/src`, `${P}/src/`), { ok: true, exact: false });
  assert.deepEqual(paths.checkPrediction(`${P}/src`, "~/code/expense-tracker/src"), {
    ok: true,
    exact: false,
  });
  assert.deepEqual(paths.checkPrediction("/", "/"), { ok: true, exact: true });
  assert.deepEqual(paths.checkPrediction(`${P}/src`, "src"), { ok: false, exact: false });
  assert.deepEqual(paths.checkPrediction("/home/alice", "~"), { ok: true, exact: false });
});

test("the drill: stable per seed, every kind, each task means what its kind says", () => {
  const first = paths.task(util.seededRandom(5));
  assert.deepEqual(paths.task(util.seededRandom(5)), first);
  const random = util.seededRandom(11);
  const kinds = new Set();
  for (let i = 0; i < 1500; i += 1) {
    const t = paths.task(random);
    kinds.add(t.kind);
    assert.ok(paths.PLACES.includes(t.start.pwd));
    assert.notEqual(t.start.oldpwd, t.start.pwd);
    const { state, results } = paths.run(t.start, t.args);
    const last = results.at(-1);
    if (t.kind === "sequence") assert.ok(t.args.length >= 2 && t.args.length <= 3);
    else assert.equal(t.args.length, 1);
    if (t.kind === "missing")
      assert.match(last.err, /No such file or directory$/, paths.commandText(t.args[0]));
    else if (t.kind === "file") assert.match(last.err, /Not a directory$/);
    else
      assert.ok(
        results.every((r) => r.ok),
        `${t.kind}: ${t.args.map(paths.commandText).join("; ")}`,
      );
    if (t.kind === "top") assert.equal(state.pwd, "/");
    if (t.kind === "dot") assert.deepEqual(state, { pwd: t.start.pwd, oldpwd: t.start.pwd });
    if (t.kind === "dash") assert.deepEqual(state, { pwd: t.start.oldpwd, oldpwd: t.start.pwd });
    if (t.kind === "home") assert.equal(state.pwd, "/home/alice");
    if (t.kind === "up" || t.kind === "across" || t.kind === "down")
      assert.ok(!t.args[0].raw.startsWith("/"));
  }
  assert.deepEqual([...kinds].sort(), [...paths.KINDS].sort());
});

test("explain walks through a cd the way the lesson does", () => {
  const show = (state, text) => {
    const arg = text === null ? null : w(text);
    return paths.explain(state, arg, paths.cd(state, arg));
  };
  assert.deepEqual(show(at(`${P}/src`, "/etc"), "../tests"), [
    `\`../tests\` is relative: it starts in the current directory, \`${P}/src\`.`,
    `Then \`..\` goes up to \`${P}\`, \`tests\` goes into \`${P}/tests\`.`,
    `pwd now prints \`${P}/tests\`, and OLDPWD becomes \`${P}/src\`.`,
  ]);
  assert.deepEqual(show(at(P, "/etc"), "test").slice(1), [
    `There is no \`test\` in \`${P}\`, so bash prints an error.`,
    "A failed cd changes nothing: pwd and OLDPWD stay as they were.",
  ]);
  assert.match(show(at(P), "README.md")[1], /is a file, not a directory/);
  assert.deepEqual(show(at(P, "/etc"), "-"), [
    "`cd -` goes back to OLDPWD, `/etc`, and prints it.",
    `pwd now prints \`/etc\`, and OLDPWD becomes \`${P}\`.`,
  ]);
  assert.equal(show(at(P), null)[0], "`cd` with no argument goes to your home folder, `/home/alice`.");
  assert.match(show(at(P), "~/code")[0], /turns `~` into your home folder/);
  assert.deepEqual(show(at("/", "/etc"), "..").slice(1), [
    "Then `..` stays at `/` (the root is its own parent).",
    "pwd still prints `/`, and OLDPWD becomes that same folder.",
  ]);
  assert.equal(show(at(P), "/etc").length, 2, "a plain absolute path needs no step list");
  assert.match(show(at(P, null), "-")[0], /OLDPWD is not set/);
});

const BASH = "/bin/bash";

test(
  "generated drills match a real bash on a copy of the tree",
  { skip: !existsSync(BASH) && "no bash" },
  () => {
    const root = realpathSync(mkdtempSync(join(tmpdir(), "swdev-paths-")));
    try {
      for (const line of paths.treeLines().slice(1)) {
        const where = root + line.path;
        if (line.dir) mkdirSync(where, { recursive: true });
        else writeFileSync(where, "");
      }
      const random = util.seededRandom(2026);
      const cases = [];
      while (cases.length < 300) {
        const t = paths.task(random);
        // bash cannot climb above the copy's root the way it stays at the real /: leave those out.
        const { results } = paths.run(t.start, t.args);
        let climbs = false;
        let dir = t.start.pwd;
        results.forEach((r, i) => {
          let here = r.target && r.target.startsWith("/") ? "/" : dir;
          for (const step of r.steps) {
            if (step.part === ".." && here === "/") climbs = true;
            here = step.dir;
          }
          dir = r.state.pwd;
        });
        if (!climbs) cases.push(t);
      }
      const q = (s) => `'${s.replace(/'/g, "'\\''")}'`;
      const arg = (a) => {
        if (a === null) return "cd";
        if (a.raw.startsWith("/")) return `cd ${q(root)}${q(a.raw)}`;
        return `cd ${a.raw}`;
      };
      const script = cases
        .map(
          (t, i) =>
            `echo "## ${i}"; ( HOME=${q(root + "/home/alice")}; cd ${q(root + t.start.pwd)} && OLDPWD=${q(
              root + t.start.oldpwd,
            )}; ${t.args.map(arg).join("; ")}; echo "PWD=$PWD"; echo "OLDPWD=$OLDPWD" ) 2>&1`,
        )
        .join("\n");
      const run = spawnSync(BASH, ["--norc", "--noprofile", "-c", script], {
        encoding: "utf8",
        env: { PATH: "/usr/bin:/bin" },
      });
      assert.equal(run.status, 0, run.stderr);
      const unroot = (s) => (s.split(root).join("") || "/").replace(/^(PWD=|OLDPWD=)$/, "$1/");
      const blocks = run.stdout.split(/^## \d+\n/m).slice(1);
      assert.equal(blocks.length, cases.length);
      cases.forEach((t, i) => {
        const got = blocks[i]
          .trimEnd()
          .split("\n")
          .map((line) => unroot(line.replace(/^.*?: line \d+: /, "bash: ")));
        const { state, results } = paths.run(t.start, t.args);
        const want = [
          ...results.flatMap((r) => [r.out, r.err].filter(Boolean)),
          `PWD=${state.pwd}`,
          `OLDPWD=${state.oldpwd}`,
        ];
        assert.deepEqual(
          got,
          want,
          `${t.kind} from ${t.start.pwd}: ${t.args.map(paths.commandText).join("; ")}`,
        );
      });
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  },
);
