// SD.pipes: the command line up to a stage, and predictions compared with real output.
import { test } from "node:test";
import assert from "node:assert/strict";
import { fixture, load } from "./helpers/load.mjs";

const { pipes } = load("pipes.js");
const stages = [
  { cmd: "tail -n +2 expenses.csv" },
  { cmd: "| cut -d, -f3" },
  { cmd: "| sort" },
  { cmd: " | uniq -c " },
];

test("upTo builds the pipeline stage by stage", () => {
  assert.equal(pipes.upTo(stages, 0), "tail -n +2 expenses.csv");
  assert.equal(pipes.upTo(stages, 1), "tail -n +2 expenses.csv | cut -d, -f3");
  assert.equal(pipes.upTo(stages, 3), "tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq -c");
});

test("upTo works on every fixture pipeline", () => {
  const mod = fixture().modules.find((m) => m.id === "pipes-bash");
  for (const p of mod.pipelines) {
    const full = pipes.upTo(p.stages, p.stages.length - 1);
    assert.ok(full.startsWith(p.stages[0].cmd), p.id);
    assert.equal(full.split(" | ").length, p.stages.length, p.id);
  }
});

test("lines: no trailing empty line, an empty output has none", () => {
  assert.deepEqual(pipes.lines("a\nb\n"), ["a", "b"]);
  assert.deepEqual(pipes.lines("a\r\nb"), ["a", "b"]);
  assert.deepEqual(pipes.lines(""), []);
  assert.deepEqual(pipes.lines("\n\n"), []);
  assert.deepEqual(pipes.lines("5"), ["5"]);
});

test("an exact prediction, spacing aside", () => {
  const out = "      5 dining\n      4 groceries";
  const r = pipes.compare("5 dining\n4  groceries\n\n", out);
  assert.equal(r.exact, true);
  assert.equal(r.matched, 2);
  assert.equal(r.total, 2);
  assert.deepEqual(r.rows, [
    { kind: "same", text: "      5 dining" },
    { kind: "same", text: "      4 groceries" },
  ]);
  assert.equal(pipes.compare("5", "5").exact, true);
  assert.equal(pipes.compare("", "").exact, true, "predicting no output for no output");
});

test("a wrong line shows as expected-but-absent and present-but-unexpected", () => {
  const r = pipes.compare("3", "2");
  assert.equal(r.exact, false);
  assert.deepEqual(r.rows, [
    { kind: "extra", text: "3" },
    { kind: "missing", text: "2" },
  ]);
});

test("order matters: the same lines unsorted match only in part", () => {
  const r = pipes.compare("b\na\nc", "a\nb\nc");
  assert.equal(r.exact, false);
  assert.equal(r.matched, 2);
  assert.deepEqual(
    r.rows.map((x) => x.kind),
    ["extra", "same", "missing", "same"],
  );
});

test("missing and extra lines, and an empty prediction", () => {
  const out =
    "date,merchant,category,amount\n2025-07-01,Cabify,transport,36.25\n2025-07-01,Lidl,groceries,56.77";
  const r = pipes.compare("2025-07-01,Cabify,transport,36.25\n2025-07-01,Lidl,groceries,56.77", out);
  assert.equal(r.matched, 2);
  assert.equal(r.total, 3);
  assert.deepEqual(
    r.rows[0],
    { kind: "missing", text: "date,merchant,category,amount" },
    "the header the prediction forgot",
  );
  const none = pipes.compare("", "x\ny");
  assert.deepEqual([none.matched, none.total, none.exact], [0, 2, false]);
  const extra = pipes.compare("x\ny", "");
  assert.deepEqual(
    extra.rows.map((x) => x.kind),
    ["extra", "extra"],
  );
});
