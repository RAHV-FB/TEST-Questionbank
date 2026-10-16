// tools/validate.py on a module's `lab_walkthrough`: the shape of the solved lab, unique ids, and
// the GNU conventions of brief/VERIFY.md for outputs. Each case runs Python against the validator.
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const SITE = fileURLToPath(new URL("..", import.meta.url));

function py(code) {
  const run = spawnSync(
    "uv",
    ["run", "python", "-c", `import sys, json, copy\nsys.path.insert(0, "tools")\nimport validate\n${code}`],
    { cwd: SITE, encoding: "utf8" },
  );
  return { status: run.status, out: run.stdout.trim(), err: run.stderr };
}

const SETUP = `
def step(sid, pipeline="tail -n +2 expenses.csv | wc -l", output="420"):
    return {"id": sid, "prompt_md": "How many?", "pipeline": pipeline, "output": output,
            "answer_md": "420, because \`tail -n +2\` skips the header."}
GOOD = {
    "id": "lab10", "title": "Lab", "source": "labs/10-wrangling.md",
    "file_note_md": "The file has 421 lines.",
    "summary_steps": [step("sum-q1")],
    "exercises": [{"id": "ex1", "title": "Exercise 1", "intro_md": "Look.", "steps": [step("ex1-q1")]}],
}
def errors(change):
    w = copy.deepcopy(GOOD)
    change(w)
    rep = validate.Report("t")
    validate.validate_walkthrough(rep, w)
    return rep.errors
def first(change):
    e = errors(change)
    return e[0] if e else ""
`;

test("a well-formed walkthrough passes", () => {
  const r = py(`${SETUP}\nprint(errors(lambda w: None))`);
  assert.equal(r.status, 0, r.err);
  assert.equal(r.out, "[]");
});

test("missing or repeated pieces are errors", () => {
  const r = py(`${SETUP}
cases = {
  "no exercises": lambda w: w.__setitem__("exercises", []),
  "no summary": lambda w: w.__setitem__("summary_steps", []),
  "no file note": lambda w: w.pop("file_note_md"),
  "no answer": lambda w: w["summary_steps"][0].pop("answer_md"),
  "no prompt": lambda w: w["summary_steps"][0].__setitem__("prompt_md", ""),
  "no pipeline": lambda w: w["summary_steps"][0].__setitem__("pipeline", " "),
  "output not a string": lambda w: w["summary_steps"][0].__setitem__("output", 420),
  "same step id twice": lambda w: w["exercises"][0]["steps"][0].__setitem__("id", "sum-q1"),
  "step id like an exercise": lambda w: w["exercises"][0]["steps"][0].__setitem__("id", "ex1"),
  "bad step id": lambda w: w["summary_steps"][0].__setitem__("id", "Sum Q1"),
  "exercise without steps": lambda w: w["exercises"][0].__setitem__("steps", []),
}
print(json.dumps({k: bool(errors(f)) for k, f in cases.items()}))
`);
  assert.equal(r.status, 0, r.err);
  const got = JSON.parse(r.out);
  for (const [name, flagged] of Object.entries(got)) assert.equal(flagged, true, name);
});

test("an output may be empty only when the last command redirects it", () => {
  const r = py(`${SETUP}
set_ = lambda pipeline, output: (lambda w: w["summary_steps"][0].update(pipeline=pipeline, output=output))
print(json.dumps([
  first(set_("head -n 1 expenses.csv > clean.csv", "")),
  first(set_("head -n 1 expenses.csv >> clean.csv", "")),
  first(set_("awk '$4>1' expenses.csv", "")),
  first(set_("wc -l expenses.csv", "")),
]))
`);
  assert.equal(r.status, 0, r.err);
  const [redirect, append, quoted, plain] = JSON.parse(r.out);
  assert.equal(redirect, "");
  assert.equal(append, "");
  assert.match(quoted, /empty output/, "a > inside quotes is not a redirection");
  assert.match(plain, /empty output/);
});

test("outputs follow the GNU format: bare wc counts, uniq -c in 7 columns, trimmed with a marker", () => {
  const r = py(`${SETUP}
set_ = lambda pipeline, output: (lambda w: w["summary_steps"][0].update(pipeline=pipeline, output=output))
print(json.dumps([
  first(set_("wc -l < expenses.csv", "     420")),
  first(set_("sort | uniq -c", "    119 groceries")),
  first(set_("sort | uniq -c", "  119 groceries")),
  first(set_("sort | uniq -c | wc -l", "8")),
  first(set_("cut -d, -f3 expenses.csv", "a\\nb\\n")),
  first(set_("cut -d, -f3 expenses.csv", "a\\n(… 412 more lines)\\nb")),
  first(set_("cut -d, -f3 expenses.csv", "a\\n(… lots more)\\nb")),
  first(set_("cut -d, -f3 expenses.csv", "(… 3 more lines)\\nb")),
]))
`);
  assert.equal(r.status, 0, r.err);
  const [padded, wide, narrow, plain, newline, marker, badMarker, firstMarker] = JSON.parse(r.out);
  assert.match(padded, /padded count/);
  assert.equal(wide, "", "a count right-aligned to 7 columns is GNU's");
  assert.match(narrow, /7 columns/);
  assert.equal(plain, "");
  assert.match(newline, /ends with a newline/);
  assert.equal(marker, "");
  assert.match(badMarker, /trim marker/);
  assert.match(firstMarker, /first line/);
});

test("the prose rules apply to every Markdown field of the walkthrough", () => {
  const r = py(`${SETUP}
print(json.dumps([
  first(lambda w: w["summary_steps"][0].__setitem__("answer_md", "Let's count the rows.")),
  first(lambda w: w["exercises"][0].__setitem__("intro_md", "\`\`\`\\nno language\\n\`\`\`")),
  first(lambda w: w.__setitem__("file_note_md", "It is a crucial file.")),
  first(lambda w: w["summary_steps"][0].__setitem__("prompt_md", "<b>How many?</b>")),
]))
`);
  assert.equal(r.status, 0, r.err);
  const [banned, fence, crucial, html] = JSON.parse(r.out);
  assert.match(banned, /banned phrase/);
  assert.match(fence, /without a language tag/);
  assert.match(crucial, /banned phrase/);
  assert.match(html, /raw HTML/);
});

test("a walkthrough that is not an object is an error", () => {
  const r = py(`${SETUP}
rep = validate.Report("t")
validate.validate_walkthrough(rep, [1, 2])
print(rep.errors)
`);
  assert.equal(r.status, 0, r.err);
  assert.match(r.out, /must be an object/);
});
