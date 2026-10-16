// SD.lab10 (the solved Lab 10 page's logic) and the walkthrough content it shows: every question
// of the lab is covered, ids are unique, and each step's pipeline really prints its output when
// replayed in bash on the course's expenses.csv.
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { copyFileSync, existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { load } from "./helpers/load.mjs";

const SITE = fileURLToPath(new URL("..", import.meta.url));
const { lab10 } = load("util.js", "lab10.js");

const walk = {
  summary_intro_html: "intro",
  summary_steps: [{ id: "sum-q1" }, { id: "sum-q2" }],
  exercises: [
    { id: "ex1", title: "Exercise 1 — Look at the file", intro_html: "i1", steps: [{ id: "ex1-q1" }] },
    { id: "stretch", title: "Stretch — one awk line", steps: [{ id: "st-q1" }, { id: "st-q2" }] },
  ],
};

test("groups: the checklist first, then each exercise, with a short name for the jump buttons", () => {
  const g = lab10.groups(walk);
  assert.deepEqual(g.map((b) => b.id), ["summary", "ex1", "stretch"]);
  assert.deepEqual(g.map((b) => b.short), ["Checklist", "Exercise 1", "Stretch"]);
  assert.equal(g[0].title, "What done looks like");
  assert.equal(g[0].intro_html, "intro");
  assert.equal(g[2].intro_html, "", "a block without an intro has an empty one");
});

test("steps: every step in page order, numbered within its block", () => {
  const all = lab10.steps(walk);
  assert.deepEqual(all.map((s) => s.step.id), ["sum-q1", "sum-q2", "ex1-q1", "st-q1", "st-q2"]);
  assert.deepEqual(all.map((s) => [s.group.id, s.number, s.of]), [
    ["summary", 1, 2],
    ["summary", 2, 2],
    ["ex1", 1, 1],
    ["stretch", 1, 2],
    ["stretch", 2, 2],
  ]);
  assert.equal(lab10.stepLabel(3, 8), "Question 3 of 8");
});

test("a step is remembered under its own draft key, as {s, p}", () => {
  assert.equal(lab10.draftKey("ex2-q1a"), "labs.lab10.ex2-q1a");
  assert.deepEqual(lab10.write({ shown: true, prediction: "420" }), { s: true, p: "420" });
  assert.deepEqual(lab10.read({ s: true, p: "420" }), { shown: true, prediction: "420" });
  assert.deepEqual(lab10.read(lab10.write({ shown: false, prediction: "a\nb" })), {
    shown: false,
    prediction: "a\nb",
  });
});

test("read: nothing yet, or a damaged value, means not shown and no prediction", () => {
  const blank = { shown: false, prediction: "" };
  for (const bad of [null, undefined, 5, "yes", [], { s: "true" }, { s: 1, p: 7 }, { p: null }]) {
    assert.deepEqual(lab10.read(bad), blank, JSON.stringify(bad));
  }
  assert.deepEqual(lab10.read({ s: true, p: 7 }), { shown: true, prediction: "" });
});

test("a long prediction is cut, not refused", () => {
  const long = "x".repeat(10000);
  assert.equal(lab10.write({ shown: false, prediction: long }).p.length, 4000);
  assert.equal(lab10.read({ s: false, p: long }).prediction.length, 4000);
});

test("tally counts the answers shown and says so", () => {
  const state = { "sum-q1": { shown: true }, "st-q2": { shown: true } };
  const read = (id) => state[id] || { shown: false };
  const t = lab10.tally(walk, read);
  assert.deepEqual(t, { shown: 2, total: 5 });
  assert.equal(lab10.tallyText(t), "2 of 5 answers shown");
  assert.equal(lab10.tallyText({ shown: 0, total: 5 }), "No answers shown yet");
  assert.equal(lab10.tallyText({ shown: 1, total: 1 }), "1 of 1 answer shown");
});

test("isTrimmed spots the line that stands for lines left out", () => {
  assert.equal(lab10.isTrimmed("a\n(… 412 more lines)\nb"), true);
  assert.equal(lab10.isTrimmed("a\n(… 1 more line)"), true);
  assert.equal(lab10.isTrimmed("a\nb"), false);
  assert.equal(lab10.isTrimmed(""), false);
  assert.equal(lab10.isTrimmed("(… all of it)"), false);
});

// ---------------------------------------------------------------- the content

const module = JSON.parse(readFileSync(join(SITE, "content", "pipes-bash.json"), "utf8"));
const lab = module.lab_walkthrough;

// Every numbered question of labs/10-wrangling.md (the first line of each is its question), the
// five "done" questions and the stretch. A question that needs two commands has one step each.
const LAB_STEPS = [
  "sum-q1", "sum-q2", "sum-q3", "sum-q4", "sum-q5",
  "ex1-q1", "ex1-q2",
  "ex2-q1a", "ex2-q1b", "ex2-q1c", "ex2-q1d", "ex2-q2", "ex2-q3", "ex2-q4",
  "ex3-q1", "ex3-q2", "ex3-q3",
  "ex4-q1", "ex4-q2", "ex4-q3", "ex4-q4",
  "ex5-q1", "ex5-q2", "ex5-q3",
  "ex6-q1", "ex6-q2", "ex6-q3", "ex6-q4",
  "ex7-q1a", "ex7-q1b", "ex7-q1c", "ex7-q2",
  "st-q1", "st-q2", "st-q3",
];

test("the walkthrough covers every question of the lab, once, in the lab's order", () => {
  assert.equal(lab.id, "lab10");
  assert.equal(lab.source, "labs/10-wrangling.md");
  assert.deepEqual(lab10.steps(lab).map((s) => s.step.id), LAB_STEPS);
  assert.deepEqual(lab.exercises.map((e) => e.id), ["ex1", "ex2", "ex3", "ex4", "ex5", "ex6", "ex7", "stretch"]);
  assert.equal(lab.summary_steps.length, 5);
  const ids = [...lab10.steps(lab).map((s) => s.step.id), ...lab.exercises.map((e) => e.id)];
  assert.equal(new Set(ids).size, ids.length, "ids are unique");
});

test("every step has its question, pipeline, output and answer; the lab's own commands are used", () => {
  for (const { step } of lab10.steps(lab)) {
    for (const key of ["prompt_md", "pipeline", "output", "answer_md"]) {
      assert.equal(typeof step[key], "string", `${step.id}.${key}`);
    }
    assert.ok(step.prompt_md && step.pipeline && step.answer_md, step.id);
    assert.ok(step.output !== "" || />/.test(step.pipeline.split("\n").pop()), `${step.id} prints nothing`);
  }
  const by = Object.fromEntries(lab10.steps(lab).map((s) => [s.step.id, s.step]));
  assert.equal(by["ex5-q1"].pipeline, "tail -n +2 expenses.csv | sort -t, -k4 -rn | head -n 5");
  assert.equal(by["ex6-q1"].pipeline, "tail -n +2 expenses.csv | sort | uniq -d");
  assert.equal(by["ex7-q1b"].pipeline, "grep ',groceries,' expenses.csv | cut -d, -f4 | paste -sd+ | bc");
  assert.match(by["st-q1"].pipeline, /^awk -F, 'NR>1 \{sum\[\$3\]\+=\$4\} END \{for \(c in sum\) printf "%s %\.2f\\n", c, sum\[c\]\}' expenses\.csv \| sort -k2 -rn$/);
  assert.equal(by["ex6-q4"].pipeline.split("\n")[1], "tail -n +2 expenses.csv | sort -u > clean.csv", "> in place of >>");
  assert.match(by["ex2-q4"].pipeline, /cut -d, -f3 \| uniq -c \| sort -rn$/, "no sort in the middle");
  assert.match(by["ex5-q2"].pipeline, / -k4 -r \|/, "-n dropped");
});

test("the answers the lab is after, as GNU prints them", () => {
  const out = Object.fromEntries(lab10.steps(lab).map((s) => [s.step.id, s.step.output]));
  assert.equal(out["sum-q1"], "420", "expenses");
  assert.equal(out["sum-q2"], "    119 groceries", "uniq -c in a 7-wide field");
  assert.equal(out["sum-q3"], "33", "distinct merchants");
  assert.equal(out["ex1-q2"], "421 expenses.csv\n420", "wc -l with a file name, then bare");
  assert.equal(out["ex3-q3"], "     23 transport", "Repsol");
  assert.equal(out["ex4-q1"], "86");
  assert.equal(out["ex4-q2"], "67", "September 2025");
  assert.equal(out["ex4-q3"], "11", "dining in December 2025");
  assert.equal(out["ex4-q4"].split("\n")[0], "     85 2025-11", "busiest month");
  assert.equal(out["ex5-q1"].split("\n")[0], "2025-11-17,Ferreteria Mas,home,296.49");
  assert.equal(out["ex5-q3"].split("\n").length, 5);
  assert.equal(out["ex6-q1"].split("\n").length, 6, "six duplicate rows");
  assert.equal(out["ex6-q2"], "415 clean.csv");
  assert.equal(out["ex6-q3"], "414");
  assert.equal(out["ex6-q4"], "414 clean.csv\n2025-07-01,Cabify,transport,36.25", "the header is gone");
  assert.match(out["ex7-q1a"], /TOTAL {18}6401\.78/, "the tracker");
  assert.equal(out["ex7-q1b"], "6401.78", "the shell");
  assert.equal(out["ex7-q2"], "6156.31", "without the duplicates");
  assert.equal(out["st-q1"].split("\n")[0], "groceries 6401.78");
  assert.equal(out["st-q3"].split("\n")[0], "home 143.43");
});

test("long outputs keep the first and last lines and say how many are left out", () => {
  const marked = lab10.steps(lab).filter((s) => lab10.isTrimmed(s.step.output));
  assert.deepEqual(marked.map((s) => s.step.id), ["ex2-q1a", "ex2-q1b", "ex2-q4"]);
  for (const { step } of marked) {
    const rows = step.output.split("\n");
    assert.equal(rows.filter((r) => /^\(… \d+ more lines\)$/.test(r)).length, 1, step.id);
    assert.ok(rows.length <= 12, step.id);
  }
  assert.match(lab.exercises[1].steps[0].output, /\(… 412 more lines\)/, "420 lines, 8 shown");
  assert.match(lab.exercises[1].steps[6].output, /\(… 325 more lines\)/, "333 lines, 8 shown");
});

// Replay every command of the walkthrough in bash, in page order in one sandbox copy (Exercise 6
// builds clean.csv for the question after it), and compare with the stored output. Spacing is
// ignored because macOS pads `wc -l` and `uniq -c` differently from GNU. Only needs the course's
// expenses.csv next to the study site; the tracker run is left out.
const DATA = join(SITE, "..", "_repos", "expense-tracker", "expenses.csv");
const haveBc = spawnSync("bc", ["--version"]).status === 0;

test("replayed in bash on the course's expenses.csv, every pipeline prints its stored output", { skip: !existsSync(DATA) && "no expenses.csv beside the site" }, () => {
  const box = mkdtempSync(join(tmpdir(), "swdev-lab10-"));
  try {
    copyFileSync(DATA, join(box, "expenses.csv"));
    const norm = (text) => text.split("\n").map((l) => l.trim().replace(/\s+/g, " ")).join("\n");
    let replayed = 0;
    for (const { step } of lab10.steps(lab)) {
      if (/^cd ~|uv run/m.test(step.pipeline) || (!haveBc && /\| bc\b/.test(step.pipeline))) continue;
      // macOS paste wants "-" to read standard input; GNU accepts it too.
      const script = step.pipeline.replace(/paste -sd\+(?= \||$)/gm, "paste -sd+ -");
      const run = spawnSync("bash", ["-c", script], { cwd: box, encoding: "utf8", env: { LC_ALL: "C", PATH: process.env.PATH } });
      assert.equal(run.status, 0, `${step.id}: ${run.stderr}`);
      const real = run.stdout.replace(/\n$/, "");
      let shown = step.output;
      let actual = real;
      const cut = /^\(… (\d+) more lines\)$/m.exec(shown);
      if (cut) {
        const rows = shown.split("\n");
        const at = rows.findIndex((r) => r === cut[0]);
        const all = real.split("\n");
        assert.equal(all.length, rows.length - 1 + Number(cut[1]), `${step.id}: the count of lines left out`);
        shown = [...rows.slice(0, at), ...rows.slice(at + 1)].join("\n");
        actual = [...all.slice(0, at), ...all.slice(all.length - (rows.length - 1 - at))].join("\n");
      }
      assert.equal(norm(actual), norm(shown), step.id);
      replayed += 1;
    }
    assert.ok(replayed >= 30, `replayed ${replayed} steps`);
  } finally {
    rmSync(box, { recursive: true, force: true });
  }
});
