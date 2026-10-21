// The build: build_cram.py --example into a temporary folder, the Artifact page rules, the failures
// that must stop a build (nothing is written then), validate_types.py, and a full build when all
// thirteen type files exist. Needs `uv` and the study-site folder.
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const CRAM = fileURLToPath(new URL("../", import.meta.url));
const SITE = join(CRAM, "..", "study-site");
const uv = spawnSync("uv", ["--version"]);
const skip = uv.status === 0 && existsSync(SITE) ? false : "needs uv and ../study-site";
const TIDS = [..."123456789"].map((n) => `S${n}`).concat(["P1", "P2", "P3", "P4"]);
const haveAll = TIDS.every((tid) => existsSync(join(CRAM, "types", `${tid}.json`)));
const skipFull = skip || (haveAll ? false : "needs types/S1..S9.json and P1..P4.json");

function uvRun(script, args) {
  return spawnSync("uv", ["run", "--project", SITE, "python", join(CRAM, script), ...args], { encoding: "utf8" });
}
const build = (args) => uvRun("build_cram.py", args);
const validate = (file) => uvRun("validate_types.py", [file]);

const scratch = () => mkdtempSync(join(tmpdir(), "cram-build-"));
const OFFLINE = "SWDev 6-Hour Cram (offline).html";
const example = (name) => JSON.parse(readFileSync(join(CRAM, "types", name), "utf8"));

function dataOf(out) {
  const html = readFileSync(join(out, "dist", "artifact.html"), "utf8");
  const blob = /<script type="application\/json" id="cram-data">(.*?)<\/script>/s.exec(html)[1];
  return { html, blob, data: JSON.parse(blob.replaceAll("<\\/", "</")) };
}

// A temporary types folder holding the given type objects as <tid>.json.
function typesDir(objects) {
  const dir = join(scratch(), "types");
  mkdirSync(dir);
  for (const obj of objects) writeFileSync(join(dir, `${obj.tid}.json`), JSON.stringify(obj));
  return dir;
}

test("--example builds both pages", { skip }, () => {
  const out = scratch();
  const r = build(["--example", "--out", out]);
  assert.equal(r.status, 0, r.stderr + r.stdout);
  assert.ok(existsSync(join(out, OFFLINE)));
  assert.ok(existsSync(join(out, "dist", "artifact.html")));
  assert.match(r.stdout, /not built \(no type file\): P1, P2, P3, P4, S1, S2, S4, S5, S6, S8, S9/);
  assert.match(r.stdout, /355 minutes/);
});

test("the artifact page has the publish shape and nothing external but Google Fonts", { skip }, () => {
  const out = scratch();
  assert.equal(build(["--example", "--out", out]).status, 0);
  const artifact = readFileSync(join(out, "dist", "artifact.html"), "utf8");
  assert.ok(artifact.startsWith("<title>SWDev 6-Hour Cram</title>\n<style>"), artifact.slice(0, 80));
  for (const tag of [/<!doctype/i, /<html[\s>]/i, /<head[\s>]/i, /<body[\s>]/i]) assert.ok(!tag.test(artifact), String(tag));
  assert.ok(!/<script[^>]*\ssrc=/i.test(artifact), "no external script");
  const hosts = new Set([...artifact.matchAll(/(?:href|src)="(https?:\/\/[^"/]+)/g)].map((m) => m[1]));
  assert.deepEqual([...hosts].sort(), ["https://fonts.googleapis.com", "https://fonts.gstatic.com"]);
  assert.ok(artifact.length < 16 * 1024 * 1024);
});

test("the offline page is a full document with the same content", { skip }, () => {
  const out = scratch();
  assert.equal(build(["--example", "--out", out]).status, 0);
  const offline = readFileSync(join(out, OFFLINE), "utf8");
  const artifact = readFileSync(join(out, "dist", "artifact.html"), "utf8");
  assert.ok(offline.startsWith("<!doctype html>"));
  assert.ok(offline.includes(artifact.trim().slice(0, 2000)));
  assert.ok(offline.includes('<meta name="viewport"'));
});

test("the data block holds the route, the three papers, the sample blocks and his answers", { skip }, () => {
  const out = scratch();
  assert.equal(build(["--example", "--out", out]).status, 0);
  const { html, blob, data } = dataOf(out);
  assert.equal(data.route.length, 18);
  assert.equal(data.route.reduce((n, s) => n + s.minutes, 0), 355);
  assert.deepEqual(data.papers.map((p) => p.id), ["sample", "paper-a", "paper-b"], "Papers C and D are left out");
  assert.equal(data.papers[0].questions.length, 9);
  assert.deepEqual(Object.keys(data.types), ["S3", "S7"]);
  for (const t of Object.values(data.types)) for (const id of t.practice) assert.ok(data.questions[id], id);
  for (const p of data.papers) for (const id of p.questions) assert.ok(data.questions[id], id);
  const total = data.types.S3.basics.reduce((n, b) => n + b.checks.length, 0);
  assert.equal(total, 2, "every check follows a basics block");
  // the sample blocks
  const s3 = data.types.S3.sample;
  assert.equal(s3.kind, "mcq");
  assert.equal(s3.options.length, 4);
  assert.equal(s3.answer, 1);
  assert.match(s3.his_answer_html, /The error says the value can be None/);
  assert.match(s3.decoded_html, /<li>/);
  const s7 = data.types.S7.sample;
  assert.equal(s7.kind, "open");
  assert.equal(s7.parts.length, 3);
  assert.match(s7.his_answer_html, /<ol>/);
  // short answers sit on the open practice questions, one for each part
  for (const id of data.types.S7.practice) {
    const q = data.questions[id];
    if (q.type !== "open") assert.equal(q.short_answers_html, undefined);
    else assert.deepEqual(Object.keys(q.short_answers_html).sort(), q.parts.map((p) => p.label).sort(), id);
  }
  // his official answers come from his own file, on the nine originals only
  assert.match(data.questions["sample-paper-q01"].teacher_answer_html, /The error names the file and the line/);
  assert.deepEqual(Object.keys(data.questions["sample-paper-q07"].teacher_parts_html), ["1", "2", "3"]);
  assert.match(data.questions["sample-paper-q09"].teacher_parts_html["1"], /Any leaks in/);
  assert.equal(data.questions["sample-paper-q10"], undefined, "the variants are not in the sample paper");
  assert.equal(data.questions["sample-paper-q03"].tid, "S3");
  // his marking guide, word for word
  assert.deepEqual(data.intro.marking.items.map((i) => i.label), ["Full marks", "Partial marks", "No marks"]);
  assert.equal(data.intro.marking.items[0].text, 'the right idea, with a reason (the "because").');
  assert.equal(data.intro.plan.reduce((n, p) => n + p.minutes, 0), 60);
  // every markdown field became HTML: no *_md keys remain
  assert.ok(!/"[a-z_]+_md"\s*:/.test(blob));
  assert.ok(blob.includes('class=\\"code\\"'), "code is highlighted at build time");
  assert.ok(html.includes("swdev-cram6-v1"));
  assert.ok(!html.includes("swdev-cram-v1"));
});

test("a full build stops when type files are missing, and writes nothing", { skip }, () => {
  const out = scratch();
  const types = join(scratch(), "types");
  mkdirSync(types);
  const r = build(["--out", out, "--types", types]);
  assert.equal(r.status, 1);
  assert.match(r.stderr, /missing type files/);
  assert.ok(!existsSync(join(out, OFFLINE)));
});

test("a bad practice id, answer index or sample copy stops a partial build, naming the problem", { skip }, () => {
  const out = scratch();
  const bad = structuredClone(example("_example6.json"));
  bad.practice[0] = "refactor-types-q999";
  bad.checks[0].answer = 9;
  bad.sample.answer = 2;
  bad.sample.options[2] = "Change the return type";
  bad.sample.his_answer_md = "**c.** Anything goes.";
  const r = build(["--partial", "--out", out, "--types", typesDir([bad])]);
  assert.equal(r.status, 1);
  assert.match(r.stderr, /refactor-types-q999 is not in the question bank/);
  assert.match(r.stderr, /answer 9 is not a valid option index/);
  assert.match(r.stderr, /his answer to Q3 is b/);
  assert.match(r.stderr, /the options are not his/);
  assert.match(r.stderr, /his reason is not copied verbatim/);
  assert.ok(!existsSync(join(out, OFFLINE)));
});

test("an id used by two stops stops the build", { skip }, () => {
  const out = scratch();
  const good = example("_example6.json");
  const other = structuredClone(good);
  other.tid = "P4";
  other.name = "Tests and project setup";
  other.minutes = 20;
  delete other.sample;
  for (const key of ["basics", "checks"]) for (const item of other[key]) item.id = item.id.replace("S3", "P4");
  const r = build(["--partial", "--out", out, "--types", typesDir([good, other])]);
  assert.equal(r.status, 1);
  assert.match(r.stderr, /is also used by (S3|P4)/);
});

test("validate_types.py passes both examples and the files that exist", { skip }, () => {
  assert.equal(validate(join(CRAM, "types", "_example6.json")).status, 0);
  assert.equal(validate(join(CRAM, "types", "_example6_open.json")).status, 0);
});

test("validate_types.py fails a broken file with the rules of the spec", { skip }, () => {
  const dir = scratch();
  const bad = structuredClone(example("_example6.json"));
  bad.method = ["only one step"];
  bad.basics[0].body_md += "\n```\nuntagged\n```\n";
  bad.practice = ["sample-paper-q03", "refactor-types-q13", "refactor-types-q30", "refactor-types-q30", "clean-code-q17"];
  bad.sample.question_md = bad.sample.question_md.replace("expense_id: int", "expense_id: str");
  const file = join(dir, "S3.json");
  writeFileSync(file, JSON.stringify(bad));
  const r = validate(file);
  assert.equal(r.status, 1);
  assert.match(r.stdout, /method: 1 items \(want 3–5\)/);
  assert.match(r.stdout, /code fence without a language tag/);
  assert.match(r.stdout, /sample-paper-q03 is one of his nine samples/);
  assert.match(r.stdout, /refactor-types-q13 is level 'hard'/);
  assert.match(r.stdout, /refactor-types-q30 is listed twice/);
  assert.match(r.stdout, /a code block of his Q3 is missing or changed/);
  assert.match(r.stdout, /short_answers: missing; needed for \['clean-code-q17'\]/);
  assert.match(r.stdout, /RESULT: FAIL/);
});

test("validate_types.py checks short answers, the sample's shape and the open practice mix", { skip }, () => {
  const dir = scratch();
  const bad = structuredClone(example("_example6_open.json"));
  delete bad.short_answers["clean-code-q03"]["2"];
  bad.short_answers["clean-code-q17"]["9"] = "A part that does not exist in the question.";
  bad.short_answers["clean-code-q17"]["1"] = "Yes.";
  bad.sample.parts[1] = "Name two problems.";
  bad.sample.his_answer_md = bad.sample.his_answer_md.replace("Move the print out", "Move the output");
  bad.practice.push("clean-code-q24");
  const file = join(dir, "S7.json");
  writeFileSync(file, JSON.stringify(bad));
  const r = validate(file);
  assert.equal(r.status, 1);
  assert.match(r.stdout, /clean-code-q03: part 2 has no short answer/);
  assert.match(r.stdout, /part 9 does not exist in clean-code-q17/);
  assert.match(r.stdout, /1 words \(a full-marks answer at his length is 1–2 sentences\)/);
  assert.match(r.stdout, /the prompts are not his/);
  assert.match(r.stdout, /his words are missing/);
  assert.match(r.stdout, /clean-code-q24: missing/);
});

test("validate_types.py refuses to file Returning Any under types disagree", { skip }, () => {
  const dir = scratch();
  const bad = structuredClone(example("_example6.json"));
  bad.traps[0] = "`Returning Any from function declared to return float` is the types disagree kind.";
  const file = join(dir, "S3.json");
  writeFileSync(file, JSON.stringify(bad));
  const r = validate(file);
  assert.equal(r.status, 1);
  assert.match(r.stdout, /files an Any error under 'types disagree'/);
});

test("route.json: kinds, refs, order and minutes are as in the spec", { skip }, () => {
  const stops = JSON.parse(readFileSync(join(CRAM, "route.json"), "utf8")).stops;
  const kinds = new Set(["intro", "baseline", "type", "break", "paper", "review", "mistakes", "final"]);
  for (const s of stops) {
    assert.ok(kinds.has(s.kind), s.kind);
    assert.ok(Number.isInteger(s.minutes) && s.minutes > 0);
    assert.ok(s.title && s.note && /^[A-Za-z0-9_~-]+$/.test(s.ref));
  }
  assert.deepEqual(stops.filter((s) => s.kind === "type").map((s) => s.ref), TIDS);
  assert.deepEqual(stops.map((s) => s.minutes), [10, 15, 15, 15, 15, 15, 15, 25, 25, 25, 10, 20, 20, 20, 20, 60, 25, 5]);
  assert.deepEqual(stops.map((s) => `${s.kind}-${s.ref}`).filter((id) => !id.startsWith("type-")), [
    "intro-intro", "break-break1", "paper-paper-a", "review-paper-a", "final-say",
  ]);
  assert.equal(stops.reduce((n, s) => n + s.minutes, 0), 355);
});

test("exam_intro.json carries his marking guide word for word", { skip }, () => {
  const code = [
    "import sys, json",
    "sys.dont_write_bytecode = True",
    `sys.path.insert(0, ${JSON.stringify(CRAM)})`,
    "import official",
    "o = official.load()",
    `mine = json.load(open(${JSON.stringify(join(CRAM, "exam_intro.json"))}))["marking"]["items"]`,
    "print(json.dumps([[m['label'], m['text']] for m in mine] == [list(x) for x in o['marking']]))",
    "print(len(o['questions']), len(o['answers']))",
  ].join("\n");
  const r = spawnSync("uv", ["run", "--project", SITE, "python", "-I", "-c", code], { encoding: "utf8" });
  assert.equal(r.status, 0, r.stderr);
  assert.equal(r.stdout.trim(), "true\n9 9");
});

test("a full build holds all thirteen stops, every practice id, and unbulleted lettered options", { skip: skipFull }, () => {
  const out = scratch();
  const r = build(["--out", out]);
  assert.equal(r.status, 0, r.stderr + r.stdout);
  const { data } = dataOf(out);
  assert.equal(data.meta.mode, "full");
  assert.deepEqual(Object.keys(data.types).sort(), [...TIDS].sort());
  for (const t of Object.values(data.types)) {
    const kinds = t.practice.map((id) => data.questions[id].type);
    assert.ok(t.practice.length >= 4 && t.practice.length <= 8, `${t.tid} practice ${t.practice.length}`);
    assert.ok(t.basics.length >= 1 && t.basics.length <= 3, `${t.tid} basics`);
    if (["S7", "S8", "S9"].includes(t.tid)) {
      const opens = kinds.filter((k) => k === "open").length;
      assert.ok(opens >= 2 && opens <= 3, `${t.tid} has ${opens} open questions`);
    }
    for (const id of t.practice) {
      const q = data.questions[id];
      assert.ok(q, `${t.tid}: ${id} missing from the data`);
      assert.ok(["core", "exam"].includes(q.level), `${id} is ${q.level}`);
      assert.notEqual(q.origin, "teacher-sample", `${id} is a sample original`);
      assert.equal(q.tid, t.tid);
      if (q.type === "open") for (const p of q.parts) assert.ok(q.short_answers_html[p.label], `${id} part ${p.label}`);
    }
    if (/^S\d$/.test(t.tid)) {
      assert.ok(t.sample, `${t.tid} has a sample block`);
      assert.equal(t.sample.qnum, `Q${t.tid.slice(1)}`);
    } else assert.equal(t.sample, null, `${t.tid} has no sample block`);
  }
  const all = Object.values(data.types).flatMap((t) => t.practice);
  assert.equal(new Set(all).size, all.length, "no question is practised by two stops");
  assert.ok(data.types.S1.sample.options.length === 4);
  assert.ok(data.questions["sample-paper-q07"].teacher_parts_html["3"]);
  assert.ok(data.types.S1.sample.question_html.includes("code"), "the question's code is highlighted");
});
