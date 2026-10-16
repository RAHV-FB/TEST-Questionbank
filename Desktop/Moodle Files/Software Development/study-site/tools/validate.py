"""Validate study-site content modules against brief/SCHEMA.md and brief/STYLE.md.

Usage:
    uv run python tools/validate.py content/<id>.json [more.json ...]
    uv run python tools/validate.py --all          # every content/*.json, plus cross-module checks

Prints errors and warnings, then RESULT: PASS or RESULT: FAIL.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SITE = Path(__file__).resolve().parent.parent
REPO = SITE.parent / "_repos" / "expense-tracker"

MODULE_KINDS = {"M1", "M2", "M3", "X"}
LEVELS = ("core", "exam", "hard", "beyond")
SKILLS = {
    "concept",
    "read-code",
    "read-tool-output",
    "read-diff",
    "compare",
    "judgement",
    "predict-output",
}
ORIGINS = {"teacher-sample", "teacher-variant", "slides", "lab", "history", "predicted"}
VERIFIED = {"run", "source", "reasoning"}
CARD_KINDS = {"concept", "distinction", "reading", "recall"}
COMMIT_KINDS = {"feature", "refactor", "test", "build", "docs", "fix", "ci"}
NON_MODULES = {"plan.json", "papers.json"}
FENCE_LANGS = {"python", "toml", "bash", "console", "text", "diff", "yaml", "ini"}

BANNED = [
    r"\bdelve",
    r"\bcrucial",
    r"\bvital\b",
    r"\bleverag",
    r"\brobust",
    r"\bseamless",
    r"\bjourney\b",
    r"\bunlock",
    r"\bempower",
    r"game[- ]changer",
    r"\bdive into\b",
    r"it'?s worth noting",
    r"it is important to note",
    r"worth mentioning",
    r"\bin today'?s\b",
    r"plays a key role",
    r"a testament to",
    r"not only\b.{0,60}\bbut also",
    r"honest caveat",
    r"\blet['’]s\b",
    r"\bin summary\b",
    r"\bin conclusion\b",
]
AMERICAN = {
    r"\bbehavior": "behaviour",
    r"\borganiz": "organis-",
    r"\brecogniz": "recognis-",
    r"\bfavorite": "favourite",
    r"\bcolor\b": "colour",
    r"\banalyz": "analys-",
    r"\bcategoriz": "categoris-",
    r"\bprioritiz": "prioritis-",
    r"\bsummariz": "summaris-",
    r"\bartifacts? \(": "",
}
EMOJI = re.compile("[\U0001f300-\U0001faff☀-➿⭐✅❌]")
HTML_TAG = re.compile(
    r"<(/?)(div|span|p|br|b|i|em|strong|a|img|ul|li|table|code|pre)\b", re.IGNORECASE
)
WORD = re.compile(r"[A-Za-z0-9'’_-]+")
SLUG = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
ROUTE_TOKEN = re.compile(r"[A-Za-z0-9_~-]+")
MORE_LINES = re.compile(r"\(… \d+ more lines?\)")
QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")
COUNT_LINE = re.compile(r"( *)(\d+) ")
LONG_OUTPUT = 40


class Report:
    def __init__(self, name: str) -> None:
        self.name = name
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, where: str, msg: str) -> None:
        self.errors.append(f"ERROR   {where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"warning {where}: {msg}")


def strip_code(md: str) -> str:
    md = re.sub(r"```.*?```", " ", md, flags=re.DOTALL)
    md = re.sub(r"`[^`\n]*`", " ", md)
    return md


def words(md: str) -> int:
    return len(WORD.findall(strip_code(md)))


def check_md(rep: Report, where: str, md: Any, *, required: bool = True) -> None:
    if md is None or md == "":
        if required:
            rep.err(where, "missing or empty markdown")
        return
    if not isinstance(md, str):
        rep.err(where, "markdown field must be a string")
        return
    fences = re.findall(r"^\s*```(.*)$", md, flags=re.MULTILINE)
    if len(fences) % 2:
        rep.err(where, "unbalanced ``` fences")
    for i, lang in enumerate(fences):
        if i % 2 == 0:
            lang = lang.strip()
            if lang == "":
                rep.err(where, "code fence without a language tag")
            elif lang not in FENCE_LANGS:
                rep.err(where, f"fence language '{lang}' not in {sorted(FENCE_LANGS)}")
    prose = strip_code(md)
    if EMOJI.search(prose):
        rep.err(where, "emoji in prose")
    if HTML_TAG.search(prose):
        rep.err(where, "raw HTML tag in prose")
    if re.search(r"[A-Za-z)]!(\s|$)", prose):
        rep.warn(where, "exclamation mark in prose")
    low = prose.lower()
    for pat in BANNED:
        if re.search(pat, low):
            rep.err(where, f"banned phrase /{pat}/")
    for pat, fix in AMERICAN.items():
        if fix and re.search(pat, low):
            rep.err(where, f"American spelling /{pat}/ (use {fix})")
    if prose.count("—") >= 2:
        rep.warn(where, f"{prose.count('—')} em dashes in prose (avoid em-dash asides)")


def ids_ok(rep: Report, where: str, value: Any, pattern: str) -> bool:
    if not isinstance(value, str) or not re.fullmatch(pattern, value):
        rep.err(where, f"id {value!r} does not match {pattern}")
        return False
    return True


def validate_walkthrough(rep: Report, walk: Any) -> None:
    """The solved lab (`lab_walkthrough`): a title, the file note, a summary list of steps and
    exercises of steps. A step is a question, the one pipeline that answers it, its real output
    and the answer. Ids are unique; outputs follow the GNU conventions of brief/VERIFY.md."""
    where = "lab_walkthrough"
    if not isinstance(walk, dict):
        rep.err(where, "must be an object")
        return
    ids: Counter[str] = Counter()
    for key in ("title", "source"):
        if not isinstance(walk.get(key), str) or not walk[key].strip():
            rep.err(where, f"{key} missing or not a string")
    if ids_ok(rep, f"{where}.id", walk.get("id"), ROUTE_TOKEN.pattern):
        ids[walk["id"]] += 1
    check_md(rep, f"{where}.file_note_md", walk.get("file_note_md"))
    check_md(rep, f"{where}.summary_intro_md", walk.get("summary_intro_md"), required=False)

    def check_steps(label: str, steps: Any) -> None:
        if not isinstance(steps, list) or not steps:
            rep.err(label, "steps must be a non-empty list")
            return
        for i, step in enumerate(steps):
            sw = f"{label}.step[{i}]"
            if not isinstance(step, dict):
                rep.err(sw, "a step must be an object")
                continue
            if ids_ok(rep, sw, step.get("id"), SLUG.pattern):
                sw = f"{label}.{step['id']}"
                ids[step["id"]] += 1
            check_md(rep, f"{sw}.prompt_md", step.get("prompt_md"))
            check_md(rep, f"{sw}.answer_md", step.get("answer_md"))
            check_walk_command(rep, sw, step.get("pipeline"), step.get("output"))

    check_steps(f"{where}.summary_steps", walk.get("summary_steps"))
    exercises = walk.get("exercises")
    if not isinstance(exercises, list) or not exercises:
        rep.err(where, "exercises must be a non-empty list")
        exercises = []
    for i, ex in enumerate(exercises):
        ew = f"{where}.exercise[{i}]"
        if not isinstance(ex, dict):
            rep.err(ew, "an exercise must be an object")
            continue
        if ids_ok(rep, ew, ex.get("id"), SLUG.pattern):
            ew = f"{where}.{ex['id']}"
            ids[ex["id"]] += 1
        if not isinstance(ex.get("title"), str) or not ex["title"].strip():
            rep.err(ew, "title missing")
        check_md(rep, f"{ew}.intro_md", ex.get("intro_md"))
        check_steps(ew, ex.get("steps"))
    for key, n in ids.items():
        if n > 1:
            rep.err(where, f"id {key!r} used {n} times (ids must be unique)")


def check_walk_command(rep: Report, where: str, pipeline: Any, output: Any) -> None:
    """One step's pipeline and output: strings, no padding that macOS adds, `uniq -c` counts in
    a 7-wide field, long outputs trimmed with a '(… N more lines)' line."""
    if not isinstance(pipeline, str) or not pipeline.strip():
        rep.err(where, "pipeline missing or not a string")
        return
    commands = pipeline.split("\n")
    if any(not c.strip() for c in commands) or pipeline != pipeline.strip():
        rep.err(where, "pipeline has an empty line or surrounding blank space")
    if not isinstance(output, str):
        rep.err(where, "output missing or not a string")
        return
    if output.endswith("\n"):
        rep.err(where, "output ends with a newline (the page adds its own line ends)")
    last = QUOTED.sub("", commands[-1])
    if output == "":
        if ">" not in last:
            rep.err(where, "empty output, but the last command does not redirect its output")
        return
    if re.fullmatch(r"\s+\d+", output):
        rep.err(where, "a padded count: GNU wc prints the bare number (VERIFY.md)")
    rows = output.split("\n")
    for k, row in enumerate(rows):
        if row.startswith("(…") and not MORE_LINES.fullmatch(row):
            rep.err(where, f"line {k + 1} looks like a trim marker but is not '(… N more lines)'")
        if row.startswith("(…") and k == 0:
            rep.err(where, "a trim marker cannot be the first line")
    if "uniq -c" in pipeline:
        for row in rows:
            m = COUNT_LINE.match(row)
            if m and len(m.group(1)) + len(m.group(2)) != 7:
                rep.err(where, f"uniq -c count not right-aligned in 7 columns (GNU): {row!r}")
                break
    if len(rows) > LONG_OUTPUT:
        rep.warn(where, f"output of {len(rows)} lines (trim it to its first and last lines)")


def validate_module(path: Path, all_ids: Counter[str]) -> Report:
    rep = Report(path.name)
    try:
        mod = json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        rep.err(path.name, f"cannot parse JSON: {exc}")
        return rep
    mid = mod.get("id")
    if not isinstance(mid, str) or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", mid):
        rep.err("module", f"bad module id {mid!r}")
        return rep
    if path.stem != mid:
        rep.err("module", f"file name {path.stem} != id {mid}")
    for key, typ in [
        ("order", int),
        ("module", str),
        ("title", str),
        ("sessions", list),
        ("predicted", bool),
        ("sources", list),
        ("summary_md", str),
        ("exam_focus_md", str),
        ("sections", list),
        ("terms", list),
        ("traps", list),
        ("flashcards", list),
        ("questions", list),
    ]:
        if not isinstance(mod.get(key), typ):
            rep.err("module", f"field '{key}' missing or not {typ.__name__}")
    if rep.errors:
        return rep
    if mod["module"] not in MODULE_KINDS:
        rep.err("module", f"module must be one of {MODULE_KINDS}")
    check_md(rep, "summary_md", mod["summary_md"])
    check_md(rep, "exam_focus_md", mod["exam_focus_md"])

    special = mid in {"history", "sample-paper"}

    # sections
    sections = mod["sections"]
    sec_ids: set[str] = set()
    lo, hi = (4, 12) if special else (5, 10)
    if not lo <= len(sections) <= hi:
        rep.err("sections", f"{len(sections)} sections (want {lo}–{hi})")
    for i, sec in enumerate(sections):
        w = f"section[{i}]"
        if not ids_ok(rep, w, sec.get("id"), rf"{re.escape(mid)}-s\d+"):
            continue
        sec_ids.add(sec["id"])
        all_ids[sec["id"]] += 1
        if not sec.get("heading"):
            rep.err(w, "missing heading")
        check_md(rep, f"{sec['id']}.body_md", sec.get("body_md"))
        n = words(sec.get("body_md") or "")
        if n < 120:
            rep.err(sec["id"], f"body_md only {n} words (min 150)")
        elif n < 150 or n > 480:
            rep.warn(sec["id"], f"body_md {n} words (aim 150–450)")
        kp = sec.get("key_points")
        if not isinstance(kp, list) or not 2 <= len(kp) <= 5:
            rep.err(sec["id"], "key_points must have 2–5 items")
        else:
            for k in kp:
                check_md(rep, f"{sec['id']}.key_points", k)
        check_md(rep, f"{sec['id']}.exam_note_md", sec.get("exam_note_md"), required=False)
        if not sec.get("source_ref"):
            rep.err(sec["id"], "missing source_ref")
        if not isinstance(sec.get("check"), list) or not 1 <= len(sec["check"]) <= 3:
            rep.err(sec["id"], "check must list 1–3 question ids")

    # terms
    terms = mod["terms"]
    if len(terms) < 8 and not special:
        rep.warn("terms", f"only {len(terms)} terms (aim 8–25)")
    for i, t in enumerate(terms):
        if not t.get("term"):
            rep.err(f"term[{i}]", "missing term")
        check_md(rep, f"term[{i}].definition_md", t.get("definition_md"))
        if t.get("section_ref") not in sec_ids:
            rep.err(
                f"term[{i}]", f"section_ref {t.get('section_ref')!r} not a section of this module"
            )

    for i, trap in enumerate(mod["traps"]):
        check_md(rep, f"trap[{i}]", trap)
    if len(mod["traps"]) < 4:
        rep.warn("traps", f"only {len(mod['traps'])} traps (aim 5+)")

    # flashcards
    cards = mod["flashcards"]
    if len(cards) < 16:
        rep.err("flashcards", f"{len(cards)} flashcards (min 16)")
    for i, c in enumerate(cards):
        w = f"flashcard[{i}]"
        if not ids_ok(rep, w, c.get("id"), rf"{re.escape(mid)}-f\d\d+"):
            continue
        all_ids[c["id"]] += 1
        check_md(rep, f"{c['id']}.front_md", c.get("front_md"))
        check_md(rep, f"{c['id']}.back_md", c.get("back_md"))
        if c.get("kind") not in CARD_KINDS:
            rep.err(c["id"], f"kind must be one of {CARD_KINDS}")
        if c.get("section_ref") not in sec_ids:
            rep.err(c["id"], f"section_ref {c.get('section_ref')!r} not in this module")

    # questions
    qs = mod["questions"]
    q_by_id: dict[str, dict[str, Any]] = {}
    types = Counter(q.get("type") for q in qs)
    levels = Counter(q.get("level") for q in qs)
    correct_pos: Counter[int] = Counter()
    mins = {"mcq": 24, "open": 6, "sort": 2}
    if mid == "sample-paper":
        mins = {"mcq": 6, "open": 3, "sort": 1}
    for t, m in mins.items():
        if types.get(t, 0) < m:
            rep.err("questions", f"{types.get(t, 0)} {t} questions (min {m})")
    for i, q in enumerate(qs):
        w = f"question[{i}]"
        if not ids_ok(rep, w, q.get("id"), rf"{re.escape(mid)}-q\d\d+"):
            continue
        qid = q["id"]
        q_by_id[qid] = q
        all_ids[qid] += 1
        qt = q.get("type")
        if qt not in {"mcq", "open", "sort"}:
            rep.err(qid, f"type {qt!r}")
            continue
        if q.get("level") not in LEVELS:
            rep.err(qid, f"level must be one of {LEVELS}")
        sk = q.get("skills")
        if not isinstance(sk, list) or not 1 <= len(sk) <= 3 or not set(sk) <= SKILLS:
            rep.err(qid, f"skills must be 1–3 of {sorted(SKILLS)}")
        check_md(rep, f"{qid}.stem_md", q.get("stem_md"))
        check_md(rep, f"{qid}.explanation_md", q.get("explanation_md"))
        ne = words(q.get("explanation_md") or "")
        if ne < 25:
            rep.err(qid, f"explanation_md only {ne} words (min 40)")
        elif ne < 40 or ne > 200:
            rep.warn(qid, f"explanation_md {ne} words (aim 40–180)")
        if q.get("section_ref") not in sec_ids:
            rep.err(qid, f"section_ref {q.get('section_ref')!r} not in this module")
        if not q.get("source_ref"):
            rep.err(qid, "missing source_ref")
        if q.get("origin") not in ORIGINS:
            rep.err(qid, f"origin must be one of {ORIGINS}")
        if q.get("verified_by") not in VERIFIED:
            rep.err(qid, f"verified_by must be one of {VERIFIED}")
        stem = q.get("stem_md") or ""
        shows_output = bool(re.search(r"```(text|console)", stem)) or "error:" in stem
        if shows_output and q.get("verified_by") == "reasoning":
            rep.err(qid, "shows tool output but verified_by is 'reasoning' (run it)")
        if mod["predicted"] is False and q.get("origin") == "predicted":
            rep.warn(qid, "origin 'predicted' in a non-predicted module")
        if q.get("origin") == "teacher-variant" and not q.get("variant_of"):
            rep.err(qid, "teacher-variant needs variant_of")
        if q.get("origin") == "teacher-sample":
            check_md(rep, f"{qid}.dissection_md", q.get("dissection_md"))

        if qt == "mcq":
            opts = q.get("options")
            if not isinstance(opts, list) or len(opts) != 4:
                rep.err(qid, "mcq needs exactly 4 options")
                continue
            n_ok = sum(1 for o in opts if o.get("correct") is True)
            if n_ok != 1:
                rep.err(qid, f"{n_ok} correct options (need exactly 1)")
            for j, o in enumerate(opts):
                ow = f"{qid}.option[{'abcd'[j]}]"
                check_md(rep, f"{ow}.text_md", o.get("text_md"))
                check_md(rep, f"{ow}.why_md", o.get("why_md"))
                if not isinstance(o.get("correct"), bool):
                    rep.err(ow, "correct must be true/false")
                txt = (o.get("text_md") or "").lower()
                if re.search(
                    r"all of the above|none of the above|both (a|b|c)\b|\b(a|b|c|d)\) and", txt
                ):
                    rep.err(ow, "option refers to other options")
                if o.get("correct"):
                    correct_pos[j] += 1
            lens = [len(strip_code(o.get("text_md") or "")) for o in opts]
            ok_i = next((j for j, o in enumerate(opts) if o.get("correct")), None)
            if ok_i is not None and lens[ok_i] == max(lens) and lens[ok_i] > 1.6 * sorted(lens)[-2]:
                rep.warn(qid, "correct option is much longer than the others (a giveaway)")
        elif qt == "open":
            parts = q.get("parts")
            if not isinstance(parts, list) or not 2 <= len(parts) <= 4:
                rep.err(qid, "open needs 2–4 parts")
                continue
            total = 0
            for j, p in enumerate(parts):
                pw = f"{qid}.part[{j}]"
                if not p.get("label"):
                    rep.err(pw, "missing label")
                check_md(rep, f"{pw}.prompt_md", p.get("prompt_md"))
                check_md(rep, f"{pw}.model_answer_md", p.get("model_answer_md"))
                check_md(rep, f"{pw}.weak_answers_md", p.get("weak_answers_md"))
                if "```" in (p.get("model_answer_md") or ""):
                    rep.err(pw, "model answer contains a code block (students never write code)")
                m = p.get("marks")
                if not isinstance(m, int) or not 1 <= m <= 3:
                    rep.err(pw, "marks must be an int 1–3")
                    m = 0
                total += m
                rub = p.get("rubric")
                if not isinstance(rub, list) or len(rub) < max(1, m):
                    rep.err(pw, "rubric needs at least `marks` points")
                else:
                    for r in rub:
                        check_md(rep, f"{pw}.rubric", r)
            if not 3 <= total <= 8:
                rep.err(qid, f"total marks {total} (want 3–8)")
            mw = sum(words(p.get("model_answer_md") or "") for p in parts)
            if mw > 170:
                rep.warn(qid, f"model answers total {mw} words (5–8 handwritten lines is ~60–130)")
            if not q.get("lines"):
                rep.err(qid, "missing lines (e.g. '5–8')")
        elif qt == "sort":
            cats = q.get("categories")
            items = q.get("items")
            if not isinstance(cats, list) or not 2 <= len(cats) <= 5:
                rep.err(qid, "sort needs 2–5 categories")
                continue
            cat_ids = {c.get("id") for c in cats}
            for c in cats:
                if not c.get("id") or not c.get("label"):
                    rep.err(qid, "category needs id and label")
            if not isinstance(items, list) or not 4 <= len(items) <= 10:
                rep.err(qid, "sort needs 4–10 items")
                continue
            used = set()
            for j, it in enumerate(items):
                iw = f"{qid}.item[{j}]"
                check_md(rep, f"{iw}.text_md", it.get("text_md"))
                check_md(rep, f"{iw}.why_md", it.get("why_md"))
                if it.get("category") not in cat_ids:
                    rep.err(iw, f"category {it.get('category')!r} not defined")
                used.add(it.get("category"))
            if used != cat_ids:
                rep.err(qid, f"unused categories: {sorted(c for c in cat_ids - used if c)}")

    # checks reference mcq/sort questions in this module
    for sec in sections:
        for ref in sec.get("check") or []:
            if ref not in q_by_id:
                rep.err(sec.get("id", "?"), f"check ref {ref} not a question here")
            elif q_by_id[ref].get("type") not in {"mcq", "sort"}:
                rep.err(sec.get("id", "?"), f"check ref {ref} must be mcq or sort")

    n = len(qs)
    if n and mid != "sample-paper":
        share = {lv: levels.get(lv, 0) / n for lv in LEVELS}
        want = {
            "core": (0.15, 0.35),
            "exam": (0.30, 0.50),
            "hard": (0.18, 0.35),
            "beyond": (0.04, 0.18),
        }
        for lv, (a, b) in want.items():
            if not a <= share[lv] <= b:
                rep.warn("levels", f"{lv} is {share[lv]:.0%} of questions (want {a:.0%}–{b:.0%})")
    n_mcq = sum(correct_pos.values())
    if n_mcq >= 12:
        for j in range(4):
            if correct_pos[j] / n_mcq > 0.38 or correct_pos[j] / n_mcq < 0.12:
                rep.warn(
                    "mcq", f"correct answer is '{'abcd'[j]}' in {correct_pos[j]}/{n_mcq} questions"
                )

    # module extras
    if mid == "pipes-bash":
        if not isinstance(mod.get("sample_files"), dict) or not mod["sample_files"]:
            rep.err("pipes-bash", "sample_files missing")
        pls = mod.get("pipelines")
        if not isinstance(pls, list) or not 6 <= len(pls) <= 12:
            rep.err("pipes-bash", "pipelines must have 6–12 entries")
        else:
            for k, pl in enumerate(pls):
                w = f"pipeline[{k}]"
                if not pl.get("id") or not pl.get("title"):
                    rep.err(w, "needs id and title")
                check_md(rep, f"{w}.goal_md", pl.get("goal_md"))
                check_md(rep, f"{w}.takeaway_md", pl.get("takeaway_md"))
                st = pl.get("stages")
                if not isinstance(st, list) or not 1 <= len(st) <= 6:
                    rep.err(w, "stages must be 1–6")
                    continue
                for s in st:
                    if not s.get("cmd") or "output" not in s:
                        rep.err(w, "stage needs cmd and output")
                    check_md(rep, f"{w}.explain_md", s.get("explain_md"))
    if "lab_walkthrough" in mod:
        validate_walkthrough(rep, mod["lab_walkthrough"])
    if mid == "history":
        commits = mod.get("commits")
        real = []
        if REPO.exists():
            out = subprocess.run(
                ["git", "-C", str(REPO), "log", "--reverse", "--format=%h"],
                capture_output=True,
                text=True,
                check=False,
            )
            real = out.stdout.split()
        if not isinstance(commits, list):
            rep.err("history", "commits missing")
        else:
            hashes = [c.get("hash") for c in commits]
            if real and hashes != real:
                rep.err("history", f"commits must be all {len(real)} hashes oldest first: {real}")
            for c in commits:
                w = f"commit {c.get('hash')}"
                if c.get("kind") not in COMMIT_KINDS:
                    rep.err(w, f"kind must be one of {COMMIT_KINDS}")
                for f in ("summary_md", "concepts_md", "message_md"):
                    check_md(rep, f"{w}.{f}", c.get(f))
                if c.get("section_ref") not in sec_ids:
                    rep.err(w, "section_ref not a history section")
                if not c.get("message"):
                    rep.err(w, "missing message")
    if mid == "sample-paper":
        originals = [q for q in qs if q.get("origin") == "teacher-sample"]
        if len(originals) != 9:
            rep.err("sample-paper", f"{len(originals)} teacher-sample questions (need the 9)")
        for q in qs:
            vo = q.get("variant_of")
            if vo and (vo not in q_by_id or q_by_id[vo].get("origin") != "teacher-sample"):
                rep.err(q["id"], f"variant_of {vo} is not an original")
    return rep


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    paths = (
        sorted((SITE / "content").glob("*.json"))
        if argv == ["--all"]
        else [Path(a).resolve() for a in argv]
    )
    paths = [p for p in paths if not p.name.startswith("_") and p.name not in NON_MODULES]
    all_ids: Counter[str] = Counter()
    failed = False
    for p in paths:
        rep = validate_module(p, all_ids)
        mod = json.loads(p.read_text()) if p.exists() else {}
        qs = mod.get("questions", []) if isinstance(mod, dict) else []
        t = Counter(q.get("type") for q in qs)
        lv = Counter(q.get("level") for q in qs)
        print(
            f"== {p.name}: {len(mod.get('sections', []))} sections, "
            f"{len(mod.get('flashcards', []))} cards, mcq {t['mcq']} open {t['open']} sort {t['sort']} "
            f"| core {lv['core']} exam {lv['exam']} hard {lv['hard']} beyond {lv['beyond']}"
        )
        for line in rep.errors + rep.warnings:
            print("  " + line)
        failed |= bool(rep.errors)
    dupes = [i for i, n in all_ids.items() if n > 1]
    if dupes:
        print(f"ERROR   duplicate ids across files: {dupes[:20]}")
        failed = True
    print("RESULT: FAIL" if failed else "RESULT: PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
