// SD.perms: rwx switches <-> octal <-> ls -l letters, and the drill.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

const { perms, util } = load("util.js", "perms.js");

test("the slide's four modes in letters", () => {
  assert.equal(perms.toLetters(0o644), "rw-r--r--");
  assert.equal(perms.toLetters(0o755), "rwxr-xr-x");
  assert.equal(perms.toLetters(0o600), "rw-------");
  assert.equal(perms.toLetters(0o777), "rwxrwxrwx");
  assert.equal(perms.toLetters(0), "---------");
  assert.deepEqual(
    perms.COMMON.map((c) => [perms.toOctal(c.mode), c.use]),
    [
      ["644", "A normal file"],
      ["755", "A script or a folder"],
      ["600", "A private key"],
      ["777", "Almost never the answer"],
    ],
  );
});

test("ls -l strings carry the type character", () => {
  assert.equal(perms.toLs(0o755), "-rwxr-xr-x");
  assert.equal(perms.toLs(0o775, "d"), "drwxrwxr-x", "the slide's src folder");
  assert.equal(perms.toLs(0o664), "-rw-rw-r--", "the slide's README.md");
});

test("octal: three digits, an optional leading 0, nothing else", () => {
  assert.equal(perms.toOctal(0o755), "755");
  assert.equal(perms.toOctal(0o7), "007");
  assert.equal(perms.toOctal(0), "000");
  assert.equal(perms.parseOctal("755"), 0o755);
  assert.equal(perms.parseOctal(" 0644 "), 0o644);
  assert.equal(perms.parseOctal("000"), 0);
  for (const bad of ["75", "7555", "758", "rwx", "", "+x", "0o755", "00755"]) {
    assert.equal(perms.parseOctal(bad), null, bad);
  }
});

test("letters: each position holds its own letter or a dash", () => {
  assert.deepEqual(perms.parseLetters("rwxr-xr-x"), { mode: 0o755, type: null });
  assert.deepEqual(perms.parseLetters("-rw-r--r--"), { mode: 0o644, type: "-" });
  assert.deepEqual(perms.parseLetters("drwxrwxr-x"), { mode: 0o775, type: "d" });
  assert.deepEqual(perms.parseLetters("---------"), { mode: 0, type: null });
  for (const bad of [
    "rwx",
    "xwrr-xr-x",
    "rwxr-xr-xx",
    "lrwxrwxrwx",
    "RWXR-XR-X",
    "rwx r-x r-x",
    "-rw-r--r--@",
  ]) {
    assert.equal(perms.parseLetters(bad), null, bad);
  }
});

test("every mode round-trips through letters and octal", () => {
  for (let mode = 0; mode <= 0o777; mode += 1) {
    assert.equal(perms.parseLetters(perms.toLetters(mode)).mode, mode);
    assert.equal(perms.parseOctal(perms.toOctal(mode)), mode);
  }
});

test("switches: has, toggle and the digit per class", () => {
  assert.ok(perms.has(0o640, "owner", "w"));
  assert.ok(!perms.has(0o640, "group", "w"));
  assert.ok(perms.has(0o640, "group", "r"));
  assert.ok(!perms.has(0o640, "others", "r"));
  assert.equal(perms.toggle(0o644, "owner", "x"), 0o744);
  assert.equal(perms.toggle(0o744, "owner", "x"), 0o644);
  assert.equal(perms.toggle(0o600, "others", "r"), 0o604);
  assert.equal(perms.digit(0o751, "owner"), 7);
  assert.equal(perms.digit(0o751, "group"), 5);
  assert.equal(perms.digit(0o751, "others"), 1);
});

test("the working: r = 4, w = 2, x = 1 added per class", () => {
  assert.equal(perms.sum(0o751, "owner"), "7 = 4 + 2 + 1");
  assert.equal(perms.sum(0o751, "group"), "5 = 4 + 1");
  assert.equal(perms.sum(0o751, "others"), "1");
  assert.equal(perms.sum(0o640, "others"), "0");
  assert.equal(perms.sum(0o620, "group"), "2");
  assert.equal(perms.sum(0o360, "owner"), "3 = 2 + 1");
  assert.equal(perms.rights(0o751, "owner"), "read, write, execute");
  assert.equal(perms.rights(0o751, "group"), "read, execute");
  assert.equal(perms.rights(0o750, "others"), "nothing");
});

test("common finds the slide's typical use", () => {
  assert.equal(perms.common(0o600).use, "A private key");
  assert.equal(perms.common(0o640), null);
});

test("drill tasks: a realistic mode, two different forms, no immediate repeat", () => {
  const random = util.seededRandom(9);
  let previous = null;
  const seen = new Set();
  for (let i = 0; i < 400; i += 1) {
    const t = perms.task(random, previous);
    assert.ok(perms.DRILL_MODES.includes(t.mode));
    assert.notEqual(t.mode, previous);
    assert.ok(perms.FORMS.includes(t.from) && perms.FORMS.includes(t.to));
    assert.notEqual(t.from, t.to);
    seen.add(`${t.from}>${t.to}`);
    previous = t.mode;
  }
  assert.equal(seen.size, 6, "every pair of forms comes up");
  const a = perms.task(util.seededRandom(3));
  assert.deepEqual(perms.task(util.seededRandom(3)), a, "stable for one seed");
});

test("drill answers are read in the asked form", () => {
  const t = { mode: 0o640, from: "number", to: "letters" };
  assert.deepEqual(perms.check(t, "rw-r-----"), { ok: true, given: 0o640, readable: true, directory: false });
  assert.equal(perms.check(t, "-rw-r-----").ok, true);
  assert.equal(perms.check(t, "rw-r--r--").ok, false);
  assert.equal(perms.check(t, "640").readable, false, "a number is not letters");
  const dir = perms.check(t, "drw-r-----");
  assert.equal(dir.ok, false, "d is a directory, the target is a file");
  assert.equal(dir.directory, true);
  assert.equal(dir.given, 0o640);

  const n = { mode: 0o755, from: "letters", to: "number" };
  assert.equal(perms.check(n, "755").ok, true);
  assert.equal(perms.check(n, "0755").ok, true);
  assert.equal(perms.check(n, "775").ok, false);
  assert.equal(perms.check(n, "rwxr-xr-x").readable, false);

  const s = { mode: 0o600, from: "number", to: "switches" };
  assert.equal(perms.check(s, 0o600).ok, true);
  assert.equal(perms.check(s, 0o644).ok, false);
  assert.equal(perms.check(s, "600").readable, false, "switches answer with a mode number");
});
