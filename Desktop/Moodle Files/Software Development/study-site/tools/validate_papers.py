"""Validate content/papers.json (the mock exam papers) against the modules.

Usage:
    uv run python tools/validate_papers.py

Every paper question follows the module question rules (see brief/SCHEMA.md) and additionally
names the module it tests (`module_ref`) and a real section of that module (`section_ref`).
Prints errors and warnings, then RESULT: PASS or RESULT: FAIL.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from validate import (
    LEVELS,
    NON_MODULES,
    ORIGINS,
    SKILLS,
    VERIFIED,
    Report,
    check_md,
    strip_code,
    words,
)

SITE = Path(__file__).resolve().parent.parent
KINDS = {"realistic", "worst-case", "beyond"}
SHAPES = {
    "realistic": {"mcq": (10, 14), "open": (3, 3)},
    "worst-case": {"mcq": (14, 16), "open": (4, 4)},
    "beyond": {"mcq": (10, 14), "open": (3, 3)},
}


def load_modules() -> dict[str, dict[str, Any]]:
    mods: dict[str, dict[str, Any]] = {}
    for p in sorted((SITE / "content").glob("*.json")):
        if p.name.startswith("_") or p.name in NON_MODULES:
            continue
        mod = json.loads(p.read_text())
        mods[mod["id"]] = mod
    return mods


def check_question(rep: Report, q: dict[str, Any], sections: set[str]) -> None:
    qid = q["id"]
    qt = q.get("type")
    if qt not in {"mcq", "open", "sort"}:
        rep.err(qid, f"type {qt!r}")
        return
    if q.get("level") not in LEVELS:
        rep.err(qid, f"level must be one of {LEVELS}")
    sk = q.get("skills")
    if not isinstance(sk, list) or not 1 <= len(sk) <= 3 or not set(sk) <= SKILLS:
        rep.err(qid, f"skills must be 1–3 of {sorted(SKILLS)}")
    check_md(rep, f"{qid}.stem_md", q.get("stem_md"))
    check_md(rep, f"{qid}.explanation_md", q.get("explanation_md"))
    if words(q.get("explanation_md") or "") < 25:
        rep.err(qid, "explanation_md under 25 words")
    if q.get("section_ref") not in sections:
        rep.err(
            qid, f"section_ref {q.get('section_ref')!r} is not a section of {q.get('module_ref')}"
        )
    if q.get("origin") not in ORIGINS:
        rep.err(qid, f"origin must be one of {ORIGINS}")
    if q.get("verified_by") not in VERIFIED:
        rep.err(qid, f"verified_by must be one of {VERIFIED}")
    stem = q.get("stem_md") or ""
    if (re.search(r"```(text|console)", stem) or "error:" in stem) and q.get(
        "verified_by"
    ) == "reasoning":
        rep.err(qid, "shows tool output but verified_by is 'reasoning'")
    if not q.get("source_ref"):
        rep.err(qid, "missing source_ref")
    if qt == "mcq":
        opts = q.get("options")
        if not isinstance(opts, list) or len(opts) != 4:
            rep.err(qid, "mcq needs exactly 4 options")
            return
        if sum(1 for o in opts if o.get("correct") is True) != 1:
            rep.err(qid, "mcq needs exactly 1 correct option")
        for j, o in enumerate(opts):
            check_md(rep, f"{qid}.option[{'abcd'[j]}].text_md", o.get("text_md"))
            check_md(rep, f"{qid}.option[{'abcd'[j]}].why_md", o.get("why_md"))
            txt = (o.get("text_md") or "").lower()
            if re.search(r"all of the above|none of the above|both (a|b|c)\b", txt):
                rep.err(qid, "option refers to other options")
        lens = [len(strip_code(o.get("text_md") or "")) for o in opts]
        ok = next((j for j, o in enumerate(opts) if o.get("correct")), None)
        if ok is not None and lens[ok] == max(lens) and lens[ok] > 1.6 * sorted(lens)[-2]:
            rep.warn(qid, "correct option is much longer than the others")
    elif qt == "open":
        parts = q.get("parts")
        if not isinstance(parts, list) or not 2 <= len(parts) <= 4:
            rep.err(qid, "open needs 2–4 parts")
            return
        total = 0
        for j, p in enumerate(parts):
            pw = f"{qid}.part[{j}]"
            for f in ("prompt_md", "model_answer_md", "weak_answers_md"):
                check_md(rep, f"{pw}.{f}", p.get(f))
            if "```" in (p.get("model_answer_md") or ""):
                rep.err(pw, "model answer contains code")
            m = p.get("marks")
            if not isinstance(m, int) or not 1 <= m <= 3:
                rep.err(pw, "marks must be an int 1–3")
                m = 0
            total += m
            rub = p.get("rubric")
            if not isinstance(rub, list) or len(rub) < max(1, m):
                rep.err(pw, "rubric needs at least `marks` points")
        if not 3 <= total <= 8:
            rep.err(qid, f"total marks {total} (want 3–8)")
        if not q.get("lines"):
            rep.err(qid, "missing lines")
    else:
        cats = q.get("categories") or []
        items = q.get("items") or []
        ids = {c.get("id") for c in cats}
        if not 2 <= len(cats) <= 5 or not 4 <= len(items) <= 10:
            rep.err(qid, "sort needs 2–5 categories and 4–10 items")
        for it in items:
            check_md(rep, f"{qid}.item.text_md", it.get("text_md"))
            check_md(rep, f"{qid}.item.why_md", it.get("why_md"))
            if it.get("category") not in ids:
                rep.err(qid, f"item category {it.get('category')!r} undefined")


def main() -> int:
    path = SITE / "content" / "papers.json"
    rep = Report(path.name)
    if not path.exists():
        print("ERROR   content/papers.json not found\nRESULT: FAIL")
        return 1
    data = json.loads(path.read_text())
    mods = load_modules()
    sections = {mid: {s["id"] for s in m["sections"]} for mid, m in mods.items()}
    bank_stems = {
        re.sub(r"\s+", " ", strip_code(q.get("stem_md", "")).lower()).strip()
        for m in mods.values()
        for q in m["questions"]
    }
    papers = data.get("papers")
    if not isinstance(papers, list) or not papers:
        rep.err("papers", "papers must be a non-empty list")
        papers = []
    seen: Counter[str] = Counter()
    for paper in papers:
        pid = paper.get("id", "?")
        if not re.fullmatch(r"paper-[a-z]", pid):
            rep.err(pid, "paper id must be paper-<letter>")
        kind = paper.get("kind")
        if kind not in KINDS:
            rep.err(pid, f"kind must be one of {KINDS}")
            continue
        if paper.get("minutes") != 60:
            rep.err(pid, "minutes must be 60")
        if not paper.get("title"):
            rep.err(pid, "missing title")
        check_md(rep, f"{pid}.intro_md", paper.get("intro_md"))
        qs = paper.get("questions") or []
        types = Counter(q.get("type") for q in qs)
        for t, (lo, hi) in SHAPES[kind].items():
            if not lo <= types.get(t, 0) <= hi:
                rep.err(pid, f"{types.get(t, 0)} {t} questions (want {lo}–{hi} for {kind})")
        if types.get("sort"):
            rep.err(pid, "papers contain only mcq and open questions (as on the real exam)")
        mods_hit = Counter(q.get("module_ref") for q in qs)
        for q in qs:
            qid = q.get("id", "?")
            if not re.fullmatch(rf"{pid}-q\d\d", qid):
                rep.err(qid, f"question id must be {pid}-qNN")
            seen[qid] += 1
            if q.get("module_ref") not in mods:
                rep.err(qid, f"module_ref {q.get('module_ref')!r} is not a module")
                continue
            check_question(rep, q, sections[q["module_ref"]])
            stem = re.sub(r"\s+", " ", strip_code(q.get("stem_md", "")).lower()).strip()
            if stem in bank_stems:
                rep.err(qid, "stem duplicates a question already in the practice bank")
        m1 = sum(n for m, n in mods_hit.items() if m in {"sdlc-agile", "scrum", "project-anatomy"})
        m3 = sum(n for m, n in mods_hit.items() if m in {"terminal-files", "pipes-bash"})
        if m1 < 3 or m3 < 2:
            rep.warn(pid, f"thin coverage: M1 {m1}, M3 {m3} questions")
    dupes = [i for i, n in seen.items() if n > 1]
    if dupes:
        rep.err("papers", f"duplicate ids {dupes}")
    for line in rep.errors + rep.warnings:
        print("  " + line)
    print("RESULT: FAIL" if rep.errors else "RESULT: PASS")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
