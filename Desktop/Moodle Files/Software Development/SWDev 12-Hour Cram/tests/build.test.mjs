// The build: build_cram.py --example into a temporary folder, the Artifact page rules, and the
// failures that must stop a build (nothing is written then). Needs `uv` and the study-site folder.
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

function build(args) {
  return spawnSync("uv", ["run", "--project", SITE, "python", join(CRAM, "build_cram.py"), ...args], { encoding: "utf8" });
}

const scratch = () => mkdtempSync(join(tmpdir(), "cram-build-"));
const OFFLINE = "SWDev 12-Hour Cram (offline).html";

test("--example builds both pages", { skip }, () => {
  const out = scratch();
  const r = build(["--example", "--out", out]);
  assert.equal(r.status, 0, r.stderr + r.stdout);
  assert.ok(existsSync(join(out, OFFLINE)));
  assert.ok(existsSync(join(out, "dist", "artifact.html")));
  assert.match(r.stdout, /not built \(no type file\): T01/);
});

test("the artifact page has the publish shape and nothing external but Google Fonts", { skip }, () => {
  const out = scratch();
  assert.equal(build(["--example", "--out", out]).status, 0);
  const artifact = readFileSync(join(out, "dist", "artifact.html"), "utf8");
  assert.ok(artifact.startsWith("<title>SWDev 12-Hour Cram</title>\n<style>"), artifact.slice(0, 80));
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

test("the data block parses and holds what the page needs", { skip }, () => {
  const out = scratch();
  assert.equal(build(["--example", "--out", out]).status, 0);
  const html = readFileSync(join(out, "dist", "artifact.html"), "utf8");
  const blob = /<script type="application\/json" id="cram-data">(.*?)<\/script>/s.exec(html)[1];
  const data = JSON.parse(blob.replaceAll("<\\/", "</"));
  assert.equal(data.route.length, 23);
  assert.equal(data.papers.length, 5);
  assert.equal(data.papers[0].id, "sample");
  assert.equal(data.papers[0].questions.length, 9);
  assert.deepEqual(Object.keys(data.types), ["T07"]);
  for (const t of Object.values(data.types)) for (const id of t.practice) assert.ok(data.questions[id], id);
  for (const p of data.papers) for (const id of p.questions) assert.ok(data.questions[id], id);
  const block = data.types.T07.basics.map((b) => b.checks.length);
  assert.equal(block.reduce((a, b) => a + b, 0), 4, "every check follows a basics block");
  // every markdown field became HTML: no *_md keys remain
  assert.ok(!/"[a-z_]+_md"\s*:/.test(blob));
  assert.ok(blob.includes('class=\\"code\\"'), "code is highlighted at build time");
  assert.ok(html.includes("swdev-cram-v1"));
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

test("a bad practice id or answer index stops a partial build, naming the problem", { skip }, () => {
  const out = scratch();
  const types = join(scratch(), "types");
  mkdirSync(types);
  const good = JSON.parse(readFileSync(join(CRAM, "types", "_example.json"), "utf8"));
  const bad = structuredClone(good);
  bad.practice[0] = "testing-tdd-q999";
  bad.checks[0].answer = 9;
  writeFileSync(join(types, "T07.json"), JSON.stringify(bad));
  const r = build(["--partial", "--out", out, "--types", types]);
  assert.equal(r.status, 1);
  assert.match(r.stderr, /testing-tdd-q999 is not in pools.json/);
  assert.match(r.stderr, /answer 9 is not a valid option index/);
  assert.ok(!existsSync(join(out, OFFLINE)));
});

test("an id used by two types stops the build", { skip }, () => {
  const out = scratch();
  const types = join(scratch(), "types");
  mkdirSync(types);
  const good = JSON.parse(readFileSync(join(CRAM, "types", "_example.json"), "utf8"));
  writeFileSync(join(types, "T07.json"), JSON.stringify(good));
  const other = structuredClone(good);
  other.tid = "T05";
  other.name = "mypy errors and the right fix";
  for (const key of ["basics", "checks"]) {
    for (const item of other[key]) item.id = item.id.replace("T07", "T05");
  }
  writeFileSync(join(types, "T05.json"), JSON.stringify(other));
  const r = build(["--partial", "--out", out, "--types", types]);
  assert.equal(r.status, 1);
  assert.match(r.stderr, /is also used by T0[57]/);
});

test("validate_types.py passes the example and fails a broken file", { skip }, () => {
  const run = (file) =>
    spawnSync("uv", ["run", "--project", SITE, "python", join(CRAM, "validate_types.py"), file], { encoding: "utf8" });
  assert.equal(run(join(CRAM, "types", "_example.json")).status, 0);
  const dir = scratch();
  const bad = JSON.parse(readFileSync(join(CRAM, "types", "_example.json"), "utf8"));
  bad.method = ["only one step"];
  bad.basics[0].body_md += "\n```\nuntagged\n```\n";
  const file = join(dir, "T07.json");
  writeFileSync(file, JSON.stringify(bad));
  const r = run(file);
  assert.equal(r.status, 1);
  assert.match(r.stdout, /method: 1 items \(want 3–6\)/);
  assert.match(r.stdout, /code fence without a language tag/);
  assert.match(r.stdout, /RESULT: FAIL/);
});

test("route.json: kinds, refs and minutes are valid", { skip }, () => {
  const stops = JSON.parse(readFileSync(join(CRAM, "route.json"), "utf8")).stops;
  const kinds = new Set(["intro", "baseline", "type", "break", "paper", "review", "mistakes", "final"]);
  for (const s of stops) {
    assert.ok(kinds.has(s.kind), s.kind);
    assert.ok(Number.isInteger(s.minutes) && s.minutes > 0);
    assert.ok(s.title && s.note && /^[A-Za-z0-9_~-]+$/.test(s.ref));
  }
  assert.deepEqual(stops.filter((s) => s.kind === "type").map((s) => s.ref), ["T10", "T01", "T02", "T03", "T04", "T05", "T06", "T07", "T11", "T12", "T08", "T09"]);
});

test("a full build holds the twelve types, every practice id, and unbulleted lettered options", { skip }, () => {
  const out = scratch();
  const r = build(["--out", out]);
  assert.equal(r.status, 0, r.stderr + r.stdout);
  const html = readFileSync(join(out, "dist", "artifact.html"), "utf8");
  const blob = /<script type="application\/json" id="cram-data">(.*?)<\/script>/s.exec(html)[1];
  const data = JSON.parse(blob.replaceAll("<\\/", "</"));
  assert.equal(data.meta.mode, "full");
  assert.deepEqual(Object.keys(data.types).sort(), Array.from({ length: 12 }, (_, i) => `T${String(i + 1).padStart(2, "0")}`));
  for (const t of Object.values(data.types)) {
    assert.ok(t.practice.length >= 10 && t.practice.length <= 14, `${t.tid} practice ${t.practice.length}`);
    for (const id of t.practice) assert.ok(data.questions[id], `${t.tid}: ${id} missing from the data`);
  }
  assert.ok(data.types.T01.worked[0].question_html.includes('<ul class="lettered">'));
});
