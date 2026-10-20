// CR.route: hash routes use only [A-Za-z0-9._~-], and every stop of the route has a link.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { load } from "./helpers/load.mjs";

const { route } = load("route.js");

test("parse splits a route into view and arguments", () => {
  assert.deepEqual(route.parse("#type.T07.practice"), { view: "type", args: ["T07", "practice"], route: "type.T07.practice" });
  assert.deepEqual(route.parse(""), { view: "home", args: [], route: "home" });
  assert.equal(route.parse("#sit.paper-a-1760600000000").view, "sit");
});

test("parse refuses a hash with other characters", () => {
  for (const bad of ["#type/T07", "#a b", "#x?y=1", "#é", "#a:b"]) assert.equal(route.parse(bad), null, bad);
});

test("build refuses a bad token", () => {
  assert.equal(route.build("paper", "paper-a"), "paper.paper-a");
  assert.throws(() => route.build("paper", "a.b"), TypeError);
  assert.throws(() => route.build("type", "T 7"), TypeError);
  assert.equal(route.href("mistakes"), "#mistakes");
});

test("every stop of route.json opens a route the router can parse", () => {
  const stops = JSON.parse(readFileSync(new URL("../route.json", import.meta.url), "utf8")).stops;
  const seen = new Set();
  for (const stop of stops) {
    const r = route.stopRoute(stop);
    assert.ok(route.parse(r), `${stop.kind}-${stop.ref} -> ${r}`);
    seen.add(`${stop.kind}-${stop.ref}`);
  }
  assert.equal(seen.size, stops.length, "stop ids are unique");
});

test("stop links", () => {
  assert.equal(route.stopHref({ kind: "intro", ref: "intro" }), "#start");
  assert.equal(route.stopHref({ kind: "baseline", ref: "sample" }), "#paper.sample");
  assert.equal(route.stopHref({ kind: "type", ref: "T10" }), "#type.T10");
  assert.equal(route.stopHref({ kind: "review", ref: "paper-a" }), "#review.paper-a");
  assert.equal(route.stopHref({ kind: "mistakes", ref: "redo" }), "#mistakes");
  assert.throws(() => route.stopRoute({ kind: "party", ref: "x" }), RangeError);
});
