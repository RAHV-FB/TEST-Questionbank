// tools/build.py end to end: builds into a temporary folder (dist/ is left alone) and checks the
// two pages against the Artifact rules and the data contract the views rely on.
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const SITE = fileURLToPath(new URL("..", import.meta.url));
const ROUTE = /^#[A-Za-z0-9._~-]+$/;
const hasRealContent = readdirSync(join(SITE, "content")).some(
  (name) => name.endsWith(".json") && !name.startsWith("_") && !["plan.json", "papers.json"].includes(name),
);

function build(...args) {
  const out = mkdtempSync(join(tmpdir(), "swdev-build-"));
  const run = spawnSync("uv", ["run", "python", "tools/build.py", ...args, "--out", out], {
    cwd: SITE,
    encoding: "utf8",
  });
  const read = (name) => readFileSync(join(out, name), "utf8");
  const result = { run, artifact: run.status === 0 ? read("artifact.html") : "", index: "" };
  if (run.status === 0) result.index = read("index.html");
  rmSync(out, { recursive: true, force: true });
  return result;
}

function blob(html) {
  const m = /<script type="application\/json" id="study-data">([\s\S]*?)<\/script>/.exec(html);
  assert.ok(m, "the page carries the study-data block");
  return JSON.parse(m[1]);
}

// Every key of every object, at any depth.
function keys(node, out = new Set()) {
  if (Array.isArray(node)) node.forEach((n) => keys(n, out));
  else if (node && typeof node === "object") {
    for (const [k, v] of Object.entries(node)) {
      out.add(k);
      keys(v, out);
    }
  }
  return out;
}

function checkPage({ run, artifact, index }) {
  assert.equal(run.status, 0, run.stderr);

  // The Artifact shape: <title> first, then <style>; no document tags.
  assert.match(artifact, /^<title>[^<]+<\/title>\n<style>\n/);
  assert.doesNotMatch(artifact, /<!doctype|<html[\s>]|<head[\s>]|<body[\s>]|<\/body>|<\/html>/i);
  // Only Google Fonts loads from outside; no external scripts.
  for (const [, url] of artifact.matchAll(/<(?:link|script|img|iframe)[^>]+(?:href|src)="([^"]+)"/g)) {
    assert.match(url, /^https:\/\/fonts\.(googleapis|gstatic)\.com/, url);
  }
  assert.doesNotMatch(artifact, /<script[^>]*\ssrc=/);
  // No dialogs, printing or download links.
  assert.doesNotMatch(artifact, /\b(alert|confirm|prompt)\s*\(|window\.print|\.print\(\)|<a[^>]*\sdownload[\s=>]/);
  // Every in-page link is a route the viewer passes.
  for (const [, href] of artifact.matchAll(/href="(#[^"]*)"/g)) assert.match(href, ROUTE, href);

  // index.html is the same page as a full document.
  assert.match(index, /^<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">/);
  assert.ok(index.includes(artifact.slice(0, 2000)), "index.html wraps the artifact page");
  assert.match(index, /<\/body>\n<\/html>\n$/);

  const data = blob(artifact);
  assert.deepEqual(Object.keys(data).sort(), ["glossary", "meta", "modules", "papers", "plan"]);
  assert.deepEqual(data.meta.exam, {
    date: "2026-10-22T14:00:00+02:00",
    minutes: 60,
    room: "108",
    weight: "30%",
    sessions: "1–10",
  });
  const all = keys(data);
  assert.ok(![...all].some((k) => k.endsWith("_md")), "every *_md key became *_html");
  for (const mod of data.modules) {
    assert.equal(typeof mod.summary_html, "string", mod.id);
    for (const s of mod.sections) {
      assert.ok(s.body_html.length > 0, s.id);
      assert.ok(Array.isArray(s.key_points) && s.key_points.every((k) => typeof k === "string"), s.id);
    }
  }
  for (const item of data.plan.flatMap((d) => d.items)) assert.match(item.link, ROUTE, item.id);
  const sorted = data.glossary.map((g) => g.term.replace(/[`"'‘’“”]/g, "").trim().toLowerCase());
  assert.deepEqual(sorted, [...sorted].sort(), "glossary is A–Z, symbols first");
  return data;
}

test("fixture build: the page shape, highlighted code and history diffs", () => {
  const data = checkPage(build("--fixture"));
  assert.equal(data.meta.fixture, true);
  assert.equal(data.papers.length, 2);

  const html = JSON.stringify(data);
  assert.match(html, /<div class=\\"code\\" data-lang=\\"python\\">/, "python is highlighted");
  assert.match(html, /<span class=\\"gp\\">\$ <\/span>/, "console prompts are marked to be dimmed");
  assert.match(html, /<span class=\\"dline d-add\\">/, "diff lines are classed");
  assert.doesNotMatch(html, /<script|<img|onerror=/i, "content never carries raw HTML");

  const history = data.modules.find((m) => m.id === "history");
  for (const commit of history.commits) {
    assert.match(commit.git.date, /^\d{4}-\d\d-\d\dT/);
    assert.ok(commit.git.files.length > 0, commit.hash);
    for (const file of commit.git.files) {
      assert.doesNotMatch(file.path, /(^|\/)(uv\.lock|expenses\.csv)$/, "excluded files stay out");
      assert.equal(typeof file.collapsed, "boolean");
    }
  }
  const first = history.commits.find((c) => c.hash === "3e0834f");
  assert.deepEqual(first.git.hidden, [{ path: "expenses.csv", added: 421, removed: 0 }]);
  const tagged = history.commits.find((c) => c.hash === "c746d38");
  assert.equal(tagged.git.tag_note, "The messy original, before any structure", "the tag's annotation from git");
  assert.equal(first.git.tag_note, undefined);
  // Diff lines carry the code highlighted from the whole file: + marker, then Python tokens.
  const typed = history.commits.find((c) => c.hash === "017f926").git.files[0].html;
  assert.match(typed, /<span class="dline d-add">\+<span class="kn">from<\/span>/);
  assert.match(typed, /<span class="dline d-hunk">@@ -1,5 \+1,6 @@<\/span>/);
  for (const commit of history.commits) {
    for (const file of commit.git.files) {
      const opened = (file.html.match(/<span\b/g) || []).length;
      assert.equal(opened, (file.html.match(/<\/span>/g) || []).length, `${commit.hash} ${file.path}: spans balance`);
    }
  }

  const pipes = data.modules.find((m) => m.id === "pipes-bash");
  assert.ok(Object.keys(pipes.sample_files).length > 0);
  assert.ok(pipes.pipelines.every((p) => p.stages.every((s) => typeof s.explain_html === "string")));
});

test("real content build", { skip: !hasRealContent && "no content modules yet" }, () => {
  const data = checkPage(build());
  assert.equal(data.meta.fixture, false);
  const history = data.modules.find((m) => m.id === "history");
  if (history) assert.equal(history.commits.length, 25);
});

test("an unknown option fails loudly", () => {
  const { run } = build("--no-such-option");
  assert.notEqual(run.status, 0);
  assert.match(run.stderr, /unrecognized arguments/);
});
