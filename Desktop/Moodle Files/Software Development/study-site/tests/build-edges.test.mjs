// tools/build.py on bad input: it must stop with a clear message (never a Python traceback), reject
// a repeated line in app/js/ORDER, check plan links against the router's grammar, and set curly
// quotes in prose only. Each case runs a few lines of Python against the build module.
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const SITE = fileURLToPath(new URL("..", import.meta.url));

function py(code) {
  const run = spawnSync("uv", ["run", "python", "-c", `import sys, json\nsys.path.insert(0, "tools")\nimport build\n${code}`], {
    cwd: SITE,
    encoding: "utf8",
  });
  return { status: run.status, out: run.stdout.trim(), err: run.stderr };
}

test("a line repeated in app/js/ORDER stops the build", () => {
  const r = py(`
import shutil, tempfile
from pathlib import Path
tmp = Path(tempfile.mkdtemp())
shutil.copytree("app", tmp / "app")
order = tmp / "app" / "js" / "ORDER"
order.write_text(order.read_text() + "\\nview-more.js\\n")
build.APP = tmp / "app"
try:
    build.js_bundle()
    print("accepted")
except build.BuildError as exc:
    print(exc)
`);
  assert.equal(r.status, 0, r.err);
  assert.match(r.out, /files listed twice \['view-more\.js'\]/);
});

test("plan.json that is not an object, or papers.json without a list, is a build error, not a traceback", () => {
  const r = py(`
import tempfile
from pathlib import Path
tmp = Path(tempfile.mkdtemp())
(tmp / "plan.json").write_text("[]")
(tmp / "papers.json").write_text('{"papers": 5}')
build.CONTENT = tmp
for name in ("plan.json", "papers.json"):
    try:
        build.read_list(tmp / name, "days" if name == "plan.json" else "papers")
        print(name, "accepted")
    except build.BuildError as exc:
        print(exc)
(tmp / "plan.json").unlink()
print(build.read_list(tmp / "plan.json", "days"))
`);
  assert.equal(r.status, 0, r.err);
  const lines = r.out.split("\n");
  assert.match(lines[0], /plan\.json must be an object with a "days" list/);
  assert.match(lines[1], /papers\.json must be an object with a "papers" list/);
  assert.equal(lines[2], "[]", "an absent plan.json is an empty plan");
});

test("an empty plan is a warning; a malformed day is an error and not a crash", () => {
  const r = py(`
known = build.Known([], [])
print(json.dumps(build.check_plan([], known)))
print(json.dumps(build.check_plan("nope", known)[0]))
print(json.dumps(build.check_plan([5, {"id": "d", "date": "2026-10-14", "label": "x", "title": "t", "items": [7]}], known)[0]))
`);
  assert.equal(r.status, 0, r.err);
  const [empty, text, bad] = r.out.split("\n").map((l) => JSON.parse(l));
  assert.deepEqual(empty[0], []);
  assert.match(empty[1][0], /empty/);
  assert.match(text[0], /must hold a "days" list/);
  assert.ok(bad.some((e) => /every day must be an object/.test(e)) && bad.some((e) => /every item must be an object/.test(e)));
});

test("a module without sections and a paper that is not an object do not crash the paper checks", () => {
  const r = py(`
mods = [{"id": "m1"}, {"id": "m2", "sections": [{"id": "m2-s1"}]}]
papers = [7, {"id": "paper-a", "kind": "realistic", "minutes": 60, "title": "A", "questions": [3, {"id": "paper-a-q01", "module_ref": "m1", "type": "mcq"}]}]
errors = build.check_papers(papers, mods, True)
print(len(errors) > 0)
`);
  assert.equal(r.status, 0, r.err);
  assert.equal(r.out, "True");
});

test("plan links follow the router's grammar and name things in the build", () => {
  const r = py(`
mods = [
  {"id": "scrum", "sections": [{"id": "scrum-s1"}], "questions": [{"id": "scrum-q01"}]},
  {"id": "pipes-bash", "sections": [{"id": "pipes-bash-s1"}], "pipelines": [{"id": "p1"}]},
  {"id": "history", "sections": [], "commits": [{"hash": "3e0834f"}]},
  {"id": "sample-paper", "sections": [{"id": "sample-paper-s1"}]},
]
papers = [{"id": "paper-a", "questions": [{"id": "paper-a-q01"}]}]
known = build.Known(mods, papers)
good = ["#home", "#plan", "#more", "#learn", "#learn.scrum", "#learn.scrum.s1", "#learn.scrum.end",
        "#practice", "#practice.weak", "#practice.next10.scrum", "#practice.weak.all.open",
        "#practice.next10.scrum-s1", "#practice.sample", "#q.scrum-q01", "#q.paper-a-q01",
        "#cards", "#cards.scrum", "#exam", "#exam.sample", "#exam.bank", "#exam.paper-a",
        "#history", "#history.guess", "#history.3e0834f", "#history.guess.3e0834f",
        "#labs", "#labs.perms", "#labs.chains", "#labs.lab10", "#labs.pipes", "#labs.pipes.p1", "#glossary"]
bad = ["#learn.nope", "#learn.scrum.s9", "#learn.scrum.s1.x", "#practice.bogus", "#practice.next10.nope",
       "#practice.next10.scrum.weird", "#q.nope", "#cards.nope", "#exam.paper-z", "#exam.a.b",
       "#history.deadbee", "#labs.nothing", "#labs.pipes.nope", "#labs.lab10.x", "#home.x", "#nowhere"]
print(json.dumps([[l for l in good if not build.plan_link_known(l, known)],
                  [l for l in bad if build.plan_link_known(l, known)]]))
`);
  assert.equal(r.status, 0, r.err);
  assert.deepEqual(JSON.parse(r.out), [[], []], "[good links wrongly rejected, bad links wrongly accepted]");
});

test("prose gets curly quotes; code, flags and the other typography stay as written", () => {
  const r = py(`
print(json.dumps(build.md_html('"A test that passes proves it works." It\\'s \`--strict\` -- 3... (c)')))
print(json.dumps(build.md_html('\`\`\`console\\n$ echo "hi"\\n\`\`\`')))
`);
  assert.equal(r.status, 0, r.err);
  const [prose, fence] = r.out.split("\n").map((l) => JSON.parse(l));
  assert.equal(prose, "“A test that passes proves it works.” It’s <code>--strict</code> -- 3... (c)");
  assert.match(fence, /echo[^\n]*"hi"/, "straight quotes inside code");
  assert.doesNotMatch(fence, /“|”/);
});
