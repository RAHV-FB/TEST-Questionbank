// Loads app/js files the way the page does: plain scripts that add members to one global CR. They
// run in this realm (not a separate vm context), so assert.deepStrictEqual can compare the arrays
// and objects they return. Each test file runs in its own process, so the global is fresh.
import { readFileSync } from "node:fs";
import vm from "node:vm";

const JS = new URL("../../app/js/", import.meta.url);

// load("util.js", "clock.js") -> CR with CR.util and CR.clock. core.js always comes first.
export function load(...files) {
  for (const name of ["core.js", ...files]) {
    const source = readFileSync(new URL(name, JS), "utf8");
    vm.runInThisContext(`"use strict";${source}`, { filename: `app/js/${name}` });
  }
  return globalThis.CR;
}

// A fake storage object: a Map behind getItem / setItem, with a switch to make writes throw.
export function fakeStorage({ blocked = false } = {}) {
  const map = new Map();
  return {
    map,
    getItem(key) {
      if (blocked) throw new Error("blocked");
      return map.has(key) ? map.get(key) : null;
    },
    setItem(key, value) {
      if (blocked) throw new Error("blocked");
      map.set(key, String(value));
    },
  };
}

// Minimal question objects for tests.
export const MCQ = (id, correct = 1, tid = "T07") => ({
  id,
  type: "mcq",
  tid,
  options: [0, 1, 2, 3].map((i) => ({ correct: i === correct })),
});

export const OPEN = (id, tid = "T12") => ({
  id,
  type: "open",
  tid,
  parts: [
    { label: "1", marks: 1, rubric: ["a", "b"] },
    { label: "2", marks: 2, rubric: ["a", "b", "c"] },
  ],
});
