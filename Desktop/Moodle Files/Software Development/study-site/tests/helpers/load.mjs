// Loads app/js files the way the page does: plain scripts that add members to one global SD.
// They run in this realm (not a separate vm context), so assert.deepStrictEqual can compare the
// arrays and objects they return. Each test file runs in its own process, so the global is fresh.
import { readFileSync } from "node:fs";
import vm from "node:vm";

const JS = new URL("../../app/js/", import.meta.url);

// load("util.js", "progress.js") -> SD with SD.util and SD.progress. sd.js always comes first.
export function load(...files) {
  for (const name of ["sd.js", ...files]) {
    const source = readFileSync(new URL(name, JS), "utf8");
    vm.runInThisContext(`"use strict";${source}`, { filename: `app/js/${name}` });
  }
  return globalThis.SD;
}

// The parsed fixture (content/_fixture.json): {modules, papers}.
export function fixture() {
  return JSON.parse(readFileSync(new URL("../../content/_fixture.json", import.meta.url), "utf8"));
}
