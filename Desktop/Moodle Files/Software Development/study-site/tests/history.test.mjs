// SD.history: tag groups, the --stat rows, "Guess the message" candidates and the next commit.
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { fixture, load } from "./helpers/load.mjs";

const { history, util } = load("util.js", "history.js");

const commit = (hash, message, tag, paths, extra = {}) => ({
  hash,
  message,
  tag,
  git: {
    files: paths.map((path) => ({ path, old_path: null })),
    hidden: [],
    tag_note: tag ? `note ${tag}` : undefined,
  },
  ...extra,
});

const COMMITS = [
  commit("3e0834f", "Add a script that totals expenses by category", null, ["tracker.py"]),
  commit("6efdf9d", "Filter by category and ignore small amounts", null, ["tracker.py"]),
  commit("c746d38", "Print the largest expense", "v0.0", ["tracker.py"]),
  commit("a953d05", "Turn the script into a uv package", null, [".gitignore", "pyproject.toml"]),
  {
    ...commit("2ecad20", "Move the report into the package behind a typer CLI", null, ["pyproject.toml"]),
    git: {
      files: [
        { path: "pyproject.toml", old_path: null },
        { path: "src/expense_tracker/report.py", old_path: "tracker.py" },
      ],
      hidden: [{ path: "uv.lock", added: 91, removed: 0 }],
    },
  },
  commit("89afbe1", "Add a README and the MIT licence", "v0.1", ["LICENSE", "README.md", "pyproject.toml"]),
  commit("5e9466d", "Replace magic numbers with named constants", null, ["src/expense_tracker/report.py"]),
  commit("f3bb801", "Rename calculate_totals to total_by_category", null, ["src/expense_tracker/report.py"]),
  commit("9d6c607", "Separate reading and printing from the calculation", null, [
    "src/expense_tracker/report.py",
  ]),
];

test("groups: a tag closes the commits since the previous tag", () => {
  const g = history.groups(COMMITS);
  assert.deepEqual(
    g.map((x) => [x.tag, x.note, x.commits.map((c) => c.hash)]),
    [
      ["v0.0", "note v0.0", ["3e0834f", "6efdf9d", "c746d38"]],
      ["v0.1", "note v0.1", ["a953d05", "2ecad20", "89afbe1"]],
      [null, "", ["5e9466d", "f3bb801", "9d6c607"]],
    ],
  );
  assert.deepEqual(history.groups([]), []);
});

test(
  "groups on the real history: six tags, 3 + 4 + 5 + 2 + 6 + 5 commits",
  { skip: !existsSync(new URL("../content/history.json", import.meta.url)) && "no history module yet" },
  () => {
    const mod = JSON.parse(readFileSync(new URL("../content/history.json", import.meta.url), "utf8"));
    const g = history.groups(mod.commits);
    assert.deepEqual(
      g.map((x) => x.tag),
      ["v0.0", "v0.1", "v0.2", "v0.3", "v0.4", "v0.5"],
    );
    assert.deepEqual(
      g.map((x) => x.commits.length),
      [3, 4, 5, 2, 6, 5],
    );
  },
);

test("groups on the fixture's three commits", () => {
  const mod = fixture().modules.find((m) => m.id === "history");
  assert.deepEqual(
    history.groups(mod.commits).map((x) => [x.tag, x.commits.length]),
    [
      ["v0.0", 2],
      [null, 1],
    ],
  );
});

test("statRows splits each file line into its count and its bar", () => {
  const stat = [
    " pyproject.toml                              |  6 +-",
    " tracker.py => src/expense_tracker/report.py | 13 ---",
    " README.md                                   |  0",
    " uv.lock                                     | 91 +++++++++++++++++++++",
    " 5 files changed, 114 insertions(+), 17 deletions(-)",
  ].join("\n");
  assert.deepEqual(history.statRows(stat), [
    { lead: " pyproject.toml                              |  6 ", plus: "+", minus: "-" },
    { lead: " tracker.py => src/expense_tracker/report.py | 13 ", plus: "", minus: "---" },
    { lead: " README.md                                   |  0", plus: "", minus: "" },
    { lead: " uv.lock                                     | 91 ", plus: "+++++++++++++++++++++", minus: "" },
    { lead: " 5 files changed, 114 insertions(+), 17 deletions(-)", plus: "", minus: "" },
  ]);
  const joined = history
    .statRows(stat)
    .map((r) => r.lead + r.plus + r.minus)
    .join("\n");
  assert.equal(joined, stat, "nothing is lost");
});

test("touched counts both names of a moved file and the hidden ones", () => {
  assert.deepEqual([...history.touched(COMMITS[4])].sort(), [
    "pyproject.toml",
    "src/expense_tracker/report.py",
    "tracker.py",
    "uv.lock",
  ]);
});

test("candidates: the real message and three others, close ones first, stable per seed", () => {
  const c = history.candidates(COMMITS, "f3bb801", 1);
  assert.equal(c.length, 4);
  assert.equal(c.filter((x) => x.real).length, 1);
  assert.equal(c.find((x) => x.real).message, "Rename calculate_totals to total_by_category");
  assert.equal(new Set(c.map((x) => x.message)).size, 4, "no message twice");
  const others = c
    .filter((x) => !x.real)
    .map((x) => x.hash)
    .sort();
  assert.deepEqual(others, ["2ecad20", "5e9466d", "9d6c607"], "the commits that touch report.py");
  assert.deepEqual(history.candidates(COMMITS, "f3bb801", 1), c);
  const positions = new Set();
  for (let seed = 0; seed < 40; seed += 1) {
    positions.add(history.candidates(COMMITS, "f3bb801", seed).findIndex((x) => x.real));
  }
  assert.equal(positions.size, 4, "the real message lands in every position");
});

test("candidates with fewer commits give fewer options", () => {
  const three = COMMITS.slice(0, 3);
  const c = history.candidates(three, "6efdf9d", 3);
  assert.equal(c.length, 3);
  assert.equal(c.filter((x) => x.real).length, 1);
});

test("ifApplied: the subject completes the sentence", () => {
  assert.equal(
    history.ifApplied("Add a README and the MIT licence"),
    "If applied, this commit will add a README and the MIT licence.",
  );
  assert.equal(history.ifApplied("README tweaks"), "If applied, this commit will README tweaks.");
  assert.equal(
    history.ifApplied("Fix stuff in loader."),
    "If applied, this commit will fix stuff in loader.",
  );
  assert.equal(history.ifApplied("  Use dict.fromkeys  "), "If applied, this commit will use dict.fromkeys.");
});

test("next: untried first, then wrong ones, never the current one", () => {
  const random = util.seededRandom(1);
  const record = Object.fromEntries(COMMITS.slice(0, 8).map((c) => [c.hash, "right"]));
  assert.equal(history.next(COMMITS, record, random), "9d6c607", "the one not tried");
  record["9d6c607"] = "right";
  record["6efdf9d"] = "wrong";
  assert.equal(history.next(COMMITS, record, random), "6efdf9d");
  assert.notEqual(history.next(COMMITS, record, random, "6efdf9d"), "6efdf9d");
  assert.equal(history.next([COMMITS[0]], {}, random, "3e0834f"), "3e0834f", "nothing else to show");
});

test("tally counts tries, right picks and written messages", () => {
  const record = { "3e0834f": "right", "6efdf9d": "wrong", c746d38: "written", gone: "right" };
  assert.deepEqual(history.tally(COMMITS, record), { tried: 3, right: 1, written: 1 });
});
