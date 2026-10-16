// SD.route: hash routes made of dot-separated tokens (the Artifact viewer passes only
// #[A-Za-z0-9._~-]+).
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

const { route } = load("route.js");

test("parse splits a hash into view and arguments", () => {
  assert.deepEqual(route.parse("#learn.testing-tdd.s3"), {
    view: "learn",
    args: ["testing-tdd", "s3"],
    route: "learn.testing-tdd.s3",
  });
  assert.deepEqual(route.parse("exam.paper-b"), { view: "exam", args: ["paper-b"], route: "exam.paper-b" });
  assert.deepEqual(route.parse("#history.04d699f").args, ["04d699f"]);
});

test("an empty hash is home; empty tokens are dropped", () => {
  assert.equal(route.parse("").view, "home");
  assert.equal(route.parse("#").view, "home");
  assert.equal(route.parse(null).view, "home");
  assert.equal(route.parse("#learn..scrum.").route, "learn.scrum");
});

test("a hash with characters the viewer would not pass is rejected", () => {
  assert.equal(route.parse("#learn/scrum"), null);
  assert.equal(route.parse("#a b"), null);
  assert.equal(route.parse("#q=1"), null);
  assert.equal(route.parse("#é"), null);
});

test("build and href join tokens and refuse bad ones", () => {
  assert.equal(route.build("learn", "scrum", "s2"), "learn.scrum.s2");
  assert.equal(route.href("practice", "next10", "all"), "#practice.next10.all");
  assert.throws(() => route.build("learn", "a.b"), TypeError, "a dot inside a token");
  assert.throws(() => route.build("learn", ""), TypeError);
  assert.throws(() => route.build("q", "x y"), TypeError);
});

test("every route built from valid tokens parses back to the same tokens", () => {
  const tokens = ["practice", "weak", "testing-tdd-s3", "open"];
  const parsed = route.parse(route.href(...tokens));
  assert.deepEqual([parsed.view, ...parsed.args], tokens);
});
