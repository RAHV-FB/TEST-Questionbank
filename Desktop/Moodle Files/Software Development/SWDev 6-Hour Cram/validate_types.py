"""Validate the cram's type files (types/S1..S9.json, types/P1..P4.json) against CRAM6_SPEC.md.

Usage (from anywhere; quote the paths, they contain spaces):
    uv run --project "<study-site>" python validate_types.py                  # every S*/P* file
    uv run --project "<study-site>" python validate_types.py types/S3.json   # one or more files

What it checks:
  * the fields and counts of the spec (basics, checks, method, worked, twists, traps, practice);
  * `sample` (S1 to S9 only): its shape, and that the question, the options, the answer and his
    official answer are copied from the teacher's two Markdown files (official.py reads them);
  * every practice id exists in the question bank at core or exam level, is not one of the nine
    sample-paper originals, is not used twice (the other type files are read too), and does not
    file `Returning Any` under "types disagree" (his answer says "Any leaks in");
  * `short_answers`: one entry per part label of every open practice id, written at his length;
  * the main site's Markdown rules: fences tagged and balanced, banned phrases, British spelling,
    no emoji, no raw HTML.
Prints errors and warnings, then RESULT: PASS or RESULT: FAIL (exit code 1).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

# The main site's validator is read, never changed, and imported without leaving bytecode there.
sys.dont_write_bytecode = True
CRAM = Path(__file__).resolve().parent
SITE = CRAM.parent / "study-site"
sys.path.insert(0, str(SITE / "tools"))
import validate  # noqa: E402

import official  # noqa: E402

TYPES_DIR = CRAM / "types"
CONTENT = SITE / "content"

# tid -> (the name shown on the page, the minutes in the spec's table).
TYPES: dict[str, tuple[str, int]] = {
    "S1": ("Q1 Tool error: what do you do next?", 15),
    "S2": ("Q2 Is it a refactoring?", 15),
    "S3": ("Q3 A mypy error: which fix?", 15),
    "S4": ("Q4 A test fails: what can you conclude?", 15),
    "S5": ("Q5 Name the clean-code problem", 15),
    "S6": ("Q6 What does this command print?", 15),
    "S7": ("Q7 Read code and say what is wrong (open)", 25),
    "S8": ("Q8 Compare a diff and two commit messages (open)", 25),
    "S9": ("Q9 Read tool output (open, harder)", 25),
    "P1": ("Process: lifecycle, Agile, Scrum, backlog, Definition of Done", 20),
    "P2": ("The terminal: paths, permissions, pipes, scripts, exit codes", 20),
    "P3": ("The CLI, core and shell, failing well", 20),
    "P4": ("Tests and project setup", 20),
}
# The spec's wording of each P stop, accepted as the type file's name too.
STOP_TEXT: dict[str, str] = {
    "P1": "Same shapes, other topics: lifecycle, Agile, Scrum, backlog, Definition of Done",
    "P2": "Same shapes, other topics: the terminal, paths, permissions, pipes, scripts, exit codes",
    "P3": "Same shapes, other topics: the CLI (typer arguments/options, exit codes), "
    "functional core / imperative shell, failing well",
    "P4": "Same shapes, other topics: tests (TDD, fixtures, parametrize, approx, tmp_path / "
    "CliRunner / monkeypatch, edge cases) and project setup "
    "(uv, uv.lock, src layout, CI as referee)",
}
OPEN_STOPS = ("S7", "S8", "S9")
SAMPLE_STOPS = tuple(f"S{n}" for n in range(1, 10))

TOP_KEYS = {
    "tid",
    "name",
    "minutes",
    "shape_md",
    "one_md",
    "spot_md",
    "basics",
    "checks",
    "method",
    "worked",
    "twists",
    "traps",
    "say_md",
    "practice",
}
OPTIONAL_KEYS = {"sample", "short_answers"}
SAMPLE_KEYS = {
    "qnum",
    "kind",
    "question_md",
    "options",
    "answer",
    "parts",
    "his_answer_md",
    "decoded_md",
}
COUNTS = {
    "checks": (0, 3),
    "method": (3, 5),
    "worked": (0, 1),
    "twists": (3, 5),
    "traps": (3, 4),
}
CHECK_OPTIONS = (3, 4)
BODY_WORDS = (80, 200)  # advised range; a warning outside it
BODY_HARD = (50, 260)  # an error outside it
SHORT_WORDS = (4, 90)  # a short answer: an error outside; a warning above ADVISED_SHORT
ADVISED_SHORT = 45
DECODED_BULLETS = (3, 6)
SPOT_BULLETS = (3, 5)
ALLOWED_LEVELS = {"core", "exam"}
TYPE_FILE = re.compile(r"[SP]\d\.json")
TID = re.compile(r"[SP]\d")

FENCE = re.compile(r"^[ \t]*```[^\n]*\n(.*?)^[ \t]*```[ \t]*$", re.S | re.M)
BULLET = re.compile(r"^[-*] ", re.M)
LIST_MARK = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")
NEGATION = re.compile(r"\b(never|not|no|isn't|doesn't|don't|wrong|instead of|rather than)\b", re.I)


# ----------------------------------------------------------------------------- the bank


def load_bank() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, dict[str, Any]]]]:
    """(every module question by id, with its module id as "mid") and (questions by module)."""
    by_id: dict[str, dict[str, Any]] = {}
    by_module: dict[str, dict[str, dict[str, Any]]] = {}
    for path in sorted(CONTENT.glob("*.json")):
        if path.name.startswith("_") or path.name in validate.NON_MODULES:
            continue
        mod = json.loads(path.read_text(encoding="utf-8"))
        mid = str(mod["id"])
        by_module[mid] = {}
        for q in mod["questions"]:
            q = dict(q)
            q["mid"] = mid
            by_id[str(q["id"])] = q
            by_module[mid][str(q["id"])] = q
    return by_id, by_module


# ------------------------------------------------------------------- text helpers


def norm(text: str) -> str:
    """Whitespace, bold marks and curly quotes folded away, to compare two copies of his words."""
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text.replace("**", "")).strip()


def norm_code(block: str) -> str:
    return "\n".join(line.rstrip() for line in block.strip().splitlines())


def code_blocks(md: str) -> list[str]:
    return [norm_code(b) for b in FENCE.findall(md)]


def prose_lines(md: str) -> list[str]:
    """The prose of a Markdown text, one normalised line each, list marks and fences removed."""
    plain = FENCE.sub("", md)
    out = (norm(LIST_MARK.sub("", line)) for line in plain.splitlines())
    return [line for line in out if line]


def flat(md: str) -> str:
    return " ".join(prose_lines(md))


def strip_letter(text: str) -> str:
    return re.sub(r"^(?:[a-d]\)|\d+\.)\s*", "", text.strip())


def sentences(md: str) -> list[str]:
    plain = FENCE.sub(" ", md)
    return [s for s in re.split(r"(?<=[.!?])\s+|\n", plain) if s.strip()]


def misfiled_any(md: str) -> str | None:
    """A sentence that files `Returning Any` under "types disagree" (his answer: Any leaks in)."""
    for sentence in sentences(md):
        if (
            re.search(r"Returning Any|no-any-return", sentence)
            and re.search(r"disagree", sentence, re.I)
            and not re.search(r"Any leaks in", sentence)
            and not NEGATION.search(sentence)
        ):
            return sentence.strip()
    return None


def strings_in(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [s for item in value for s in strings_in(item)]
    if isinstance(value, dict):
        return [s for item in value.values() for s in strings_in(item)]
    return []


def is_text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def md_field(rep: Any, where: str, value: Any) -> None:
    validate.check_md(rep, where, value)


def count_between(rep: Any, where: str, items: Any, lo: int, hi: int) -> list[Any]:
    """The list when it is a list of lo..hi items, else an error and an empty list."""
    if not isinstance(items, list):
        rep.err(where, "must be a list")
        return []
    if not lo <= len(items) <= hi:
        rep.err(where, f"{len(items)} items (want {lo}–{hi})")
    return items


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def read_type(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc


def claims_of(paths: list[Path]) -> dict[str, dict[str, str]]:
    """Which type claims each practice id, per file: {file name: {id: tid}} (unreadable skipped)."""
    out: dict[str, dict[str, str]] = {}
    for path in paths:
        try:
            data = read_type(path)
        except ValueError:
            continue
        if not isinstance(data, dict) or not isinstance(data.get("practice"), list):
            continue
        tid = str(data.get("tid"))
        out[path.name] = {str(i): tid for i in data["practice"] if isinstance(i, str)}
    return out


def accepted_names(tid: str) -> set[str]:
    """The names a type file may carry: the page name, the spec's wording, or either without
    the "Q3 " or "Same shapes, other topics: " lead."""
    name = TYPES[tid][0]
    names = {name, STOP_TEXT.get(tid, name)}
    for text in list(names):
        names.add(re.sub(r"^Q\d\s+", "", text))
        names.add(re.sub(r"^Same shapes, other topics:\s*", "", text))
    return {n[:1].lower() + n[1:] for n in names} | {n[:1].upper() + n[1:] for n in names}


# ----------------------------------------------------------------------- parts of a file


def check_basics(rep: Any, tid: str, items: list[Any]) -> None:
    seen: set[str] = set()
    for i, block in enumerate(items):
        where = f"basics[{i}]"
        if not isinstance(block, dict):
            rep.err(where, "must be an object")
            continue
        bid = block.get("id")
        if not isinstance(bid, str) or not re.fullmatch(rf"{tid}-b\d+", bid):
            rep.err(where, f"id {bid!r} must look like {tid}-b1")
        elif bid in seen:
            rep.err(where, f"duplicate id {bid}")
        else:
            seen.add(bid)
        md_field(rep, f"{where}.heading", block.get("heading"))
        body = block.get("body_md")
        md_field(rep, f"{where}.body_md", body)
        if isinstance(body, str):
            n = validate.words(body)
            if not BODY_HARD[0] <= n <= BODY_HARD[1]:
                rep.err(where, f"body_md has {n} words (want {BODY_WORDS[0]}–{BODY_WORDS[1]})")
            elif not BODY_WORDS[0] <= n <= BODY_WORDS[1]:
                rep.warn(where, f"body_md has {n} words (advised {BODY_WORDS[0]}–{BODY_WORDS[1]})")
            if len(FENCE.findall(body)) > 2:
                rep.warn(where, "more than two code blocks (two at most)")
        extra = set(block) - {"id", "heading", "body_md"}
        if extra:
            rep.warn(where, f"unknown keys {sorted(extra)}")


def check_checks(rep: Any, tid: str, items: list[Any]) -> None:
    seen: set[str] = set()
    answers: list[int] = []
    for i, check in enumerate(items):
        where = f"checks[{i}]"
        if not isinstance(check, dict):
            rep.err(where, "must be an object")
            continue
        cid = check.get("id")
        if not isinstance(cid, str) or not re.fullmatch(rf"{tid}-c\d+", cid):
            rep.err(where, f"id {cid!r} must look like {tid}-c1")
        elif cid in seen:
            rep.err(where, f"duplicate id {cid}")
        else:
            seen.add(cid)
        md_field(rep, f"{where}.q_md", check.get("q_md"))
        md_field(rep, f"{where}.why_md", check.get("why_md"))
        options = check.get("options")
        if (
            not isinstance(options, list)
            or not CHECK_OPTIONS[0] <= len(options) <= CHECK_OPTIONS[1]
        ):
            rep.err(where, f"options must be a list of {CHECK_OPTIONS[0]}–{CHECK_OPTIONS[1]} texts")
            options = []
        for j, text in enumerate(options):
            md_field(rep, f"{where}.options[{j}]", text)
        if len({str(o).strip() for o in options}) != len(options):
            rep.err(where, "two options have the same text")
        answer = check.get("answer")
        if (
            isinstance(answer, bool)
            or not isinstance(answer, int)
            or not 0 <= answer < len(options)
        ):
            rep.err(where, f"answer {answer!r} is not a valid option index (0–{len(options) - 1})")
        else:
            answers.append(answer)
        extra = set(check) - {"id", "q_md", "options", "answer", "why_md"}
        if extra:
            rep.warn(where, f"unknown keys {sorted(extra)}")
    if len(answers) >= 3 and len(set(answers)) == 1:
        rep.warn("checks", f"every check has the answer at index {answers[0]}: vary the position")


def check_worked(rep: Any, items: list[Any]) -> None:
    for i, example in enumerate(items):
        where = f"worked[{i}]"
        if not isinstance(example, dict):
            rep.err(where, "must be an object")
            continue
        if not is_text(example.get("title")):
            rep.err(where, "missing title")
        md_field(rep, f"{where}.question_md", example.get("question_md"))
        md_field(rep, f"{where}.answer_md", example.get("answer_md"))
        steps = example.get("steps_md")
        if not isinstance(steps, list) or not 2 <= len(steps) <= 5:
            rep.err(where, "steps_md must be a list of 2–5 Markdown strings")
            steps = []
        for j, step in enumerate(steps):
            md_field(rep, f"{where}.steps_md[{j}]", step)
        answer = example.get("answer_md")
        if isinstance(answer, str) and validate.words(answer) > 70:
            rep.warn(where, "answer_md is longer than his answers (one or two sentences per part)")
        extra = set(example) - {"title", "question_md", "steps_md", "answer_md"}
        if extra:
            rep.warn(where, f"unknown keys {sorted(extra)}")


def check_twists(rep: Any, items: list[Any]) -> None:
    for i, twist in enumerate(items):
        where = f"twists[{i}]"
        if not isinstance(twist, dict):
            rep.err(where, "must be an object")
            continue
        md_field(rep, f"{where}.twist_md", twist.get("twist_md"))
        md_field(rep, f"{where}.how_md", twist.get("how_md"))
        how = twist.get("how_md")
        if isinstance(how, str) and validate.words(how) > 60:
            rep.warn(where, "how_md is longer than two sentences")
        extra = set(twist) - {"twist_md", "how_md"}
        if extra:
            rep.warn(where, f"unknown keys {sorted(extra)}")


def check_bullets(rep: Any, where: str, md: Any, lo: int, hi: int) -> None:
    if not isinstance(md, str):
        return
    n = len(BULLET.findall(md))
    if not lo <= n <= hi:
        rep.err(where, f"{n} bullets (want {lo}–{hi})")


# ------------------------------------------------------------------------ the sample


def check_sample(rep: Any, tid: str, sample: Any, source: official.Official | None) -> None:
    where = "sample"
    if not isinstance(sample, dict):
        rep.err(where, "must be an object")
        return
    n = int(tid[1:])
    kind = "open" if tid in OPEN_STOPS else "mcq"
    extra = sorted(set(sample) - SAMPLE_KEYS)
    if extra:
        rep.warn(where, f"unknown keys {extra}")
    if sample.get("qnum") != f"Q{n}":
        rep.err(f"{where}.qnum", f"{sample.get('qnum')!r} must be 'Q{n}'")
    if sample.get("kind") != kind:
        rep.err(f"{where}.kind", f"{sample.get('kind')!r} must be '{kind}' for {tid}")
    for key in ("question_md", "his_answer_md", "decoded_md"):
        md_field(rep, f"{where}.{key}", sample.get(key))
    check_bullets(rep, f"{where}.decoded_md", sample.get("decoded_md"), *DECODED_BULLETS)
    options = sample.get("options")
    parts = sample.get("parts")
    if kind == "mcq":
        if not isinstance(options, list) or len(options) != 4:
            rep.err(f"{where}.options", "an mcq sample needs four options, a) to d) in order")
            options = []
        for j, text in enumerate(options):
            md_field(rep, f"{where}.options[{j}]", text)
        answer = sample.get("answer")
        if isinstance(answer, bool) or not isinstance(answer, int) or not 0 <= answer <= 3:
            rep.err(f"{where}.answer", f"{answer!r} must be an option index 0–3")
        if parts is not None:
            rep.err(f"{where}.parts", "an mcq sample has no parts")
    else:
        if not isinstance(parts, list) or len(parts) != 3:
            rep.err(f"{where}.parts", "an open sample needs its three prompts, in order")
            parts = []
        for j, text in enumerate(parts):
            md_field(rep, f"{where}.parts[{j}]", text)
        if options is not None or sample.get("answer") is not None:
            rep.err(where, "an open sample has no options and no answer index")
    if source is not None:
        check_against_source(rep, n, sample, source)


def check_against_source(
    rep: Any, n: int, sample: dict[str, Any], source: official.Official
) -> None:
    """The question, the options and his answer must be his words (official.py reads them)."""
    where = "sample"
    question = source["questions"][n]
    answer = source["answers"][n]
    text = sample.get("question_md")
    if isinstance(text, str):
        mine = code_blocks(text)
        for block in code_blocks(question["stem"]):
            if block not in mine:
                rep.err(f"{where}.question_md", f"a code block of his Q{n} is missing or changed")
        have = flat(text)
        for line in prose_lines(question["stem"]):
            if line not in have:
                rep.err(f"{where}.question_md", f"his line is missing or changed: {line[:70]!r}")
    given = sample.get("his_answer_md")
    if question["kind"] == "mcq":
        options = [strip_letter(str(o)) for o in as_list(sample.get("options"))]
        if [norm(o) for o in options] != [norm(o) for o in question["options"]]:
            rep.err(f"{where}.options", f"the options are not his; copy them from Q{n}")
        letter = answer["letter"]
        if sample.get("answer") != official.LETTERS.index(letter):
            rep.err(f"{where}.answer", f"his answer to Q{n} is {letter}")
        if isinstance(given, str) and norm(answer["why"]) not in norm(given):
            rep.err(f"{where}.his_answer_md", "his reason is not copied verbatim from his answers")
    else:
        prompts = [strip_letter(str(p)) for p in as_list(sample.get("parts"))]
        if [norm(p) for p in prompts] != [norm(p) for p in question["parts"]]:
            rep.err(f"{where}.parts", f"the prompts are not his; copy them from Q{n}")
        if isinstance(given, str):
            have = norm(given)
            for line in prose_lines(answer["text"]):
                if line not in have:
                    rep.err(f"{where}.his_answer_md", f"his words are missing: {line[:70]!r}")


# ----------------------------------------------------------------- practice and answers


def check_practice(
    rep: Any,
    tid: str,
    ids: list[Any],
    bank: dict[str, dict[str, Any]],
    others: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    """Check the practice ids; returns the bank questions of the ids that exist."""
    seen: set[str] = set()
    picked: list[dict[str, Any]] = []
    for i, qid in enumerate(ids):
        where = f"practice[{i}]"
        if not isinstance(qid, str):
            rep.err(where, "must be a question id string")
            continue
        if qid in seen:
            rep.err(where, f"{qid} is listed twice")
            continue
        seen.add(qid)
        q = bank.get(qid)
        if q is None:
            rep.err(where, f"{qid} is not in the question bank")
            continue
        picked.append(q)
        if q.get("origin") == "teacher-sample":
            rep.err(where, f"{qid} is one of his nine samples: it belongs to the sample block")
        if q.get("level") not in ALLOWED_LEVELS:
            rep.err(where, f"{qid} is level {q.get('level')!r}; use core or exam")
        for file, claimed in others.items():
            other = claimed.get(qid)
            if other is not None and other != tid:
                rep.err(where, f"{qid} is also used by {other} ({file})")
        bad = next((m for s in strings_in(q) if (m := misfiled_any(s))), None)
        if bad:
            rep.err(
                where,
                f"{qid} files an Any error under 'types disagree' ({bad[:60]!r}...); "
                "his answer is 'Any leaks in'. Pick another question",
            )
    check_practice_mix(rep, tid, picked)
    return picked


def check_practice_mix(rep: Any, tid: str, picked: list[dict[str, Any]]) -> None:
    n = len(picked)
    opens = sum(1 for q in picked if q["type"] == "open")
    mcqs = sum(1 for q in picked if q["type"] == "mcq")
    if tid in OPEN_STOPS:
        if not 2 <= opens <= 3:
            rep.err("practice", f"{opens} open questions (want 2–3 for {tid})")
        if mcqs < 1:
            rep.err("practice", "no multiple-choice question")
        elif mcqs != 2:
            rep.warn("practice", f"{mcqs} multiple-choice questions (the spec asks for 2)")
        if n > 6:
            rep.err("practice", f"{n} questions (want 4–6 for {tid})")
    else:
        if not 4 <= n <= 8:
            rep.err("practice", f"{n} questions (want 4–8)")
        if mcqs == 0:
            rep.err("practice", "no multiple-choice question")
        if opens * 2 > n:
            rep.warn("practice", f"{opens} of {n} are open (this stop is mostly multiple choice)")


def check_short_answers(rep: Any, short: Any, picked: list[dict[str, Any]]) -> None:
    """One full-marks answer at his length for every part of every open practice question."""
    open_qs = {str(q["id"]): q for q in picked if q["type"] == "open"}
    if short is None:
        if open_qs:
            rep.err("short_answers", f"missing; needed for {sorted(open_qs)}")
        return
    if not isinstance(short, dict):
        rep.err("short_answers", "must be an object {question id: {part label: text}}")
        return
    for qid in sorted(set(short) - set(open_qs)):
        rep.err("short_answers", f"{qid} is not an open practice question of this stop")
    for qid, q in open_qs.items():
        entry = short.get(qid)
        where = f"short_answers.{qid}"
        if not isinstance(entry, dict):
            rep.err(where, "missing: one answer for each part label")
            continue
        labels = [str(p["label"]) for p in q["parts"]]
        for label in labels:
            if label not in entry:
                rep.err(where, f"part {label} has no short answer")
        for label in sorted(set(entry) - set(labels)):
            rep.err(where, f"part {label} does not exist in {qid} (parts: {labels})")
        for label, text in entry.items():
            check_short_text(rep, f"{where}.{label}", text)


def check_short_text(rep: Any, where: str, text: Any) -> None:
    md_field(rep, where, text)
    if not isinstance(text, str):
        return
    n = validate.words(text)
    if not SHORT_WORDS[0] <= n <= SHORT_WORDS[1]:
        rep.err(where, f"{n} words (a full-marks answer at his length is 1–2 sentences)")
    elif n > ADVISED_SHORT:
        rep.warn(where, f"{n} words (his answers are one or two sentences, about {ADVISED_SHORT})")
    if "```" in text:
        rep.warn(where, "a short answer is prose; no code block")


# --------------------------------------------------------------------------- one file


def validate_type(
    path: Path,
    bank: dict[str, dict[str, Any]],
    others: dict[str, dict[str, str]],
    source: official.Official | None,
) -> Any:
    """Check one type file; returns the validator's report (errors and warnings)."""
    rep = validate.Report(path.name)
    try:
        data = read_type(path)
    except ValueError as exc:
        rep.err("file", str(exc))
        return rep
    if not isinstance(data, dict):
        rep.err("file", "the top level must be an object")
        return rep
    tid = data.get("tid")
    if not isinstance(tid, str) or not TID.fullmatch(tid) or tid not in TYPES:
        rep.err("tid", f"{tid!r} is not one of {sorted(TYPES)}")
        return rep
    missing = sorted(TOP_KEYS - set(data))
    if tid in SAMPLE_STOPS and "sample" not in data:
        missing.append("sample")
    if missing:
        rep.err("file", f"missing keys {missing}")
    extra = sorted(set(data) - TOP_KEYS - OPTIONAL_KEYS)
    if extra:
        rep.warn("file", f"unknown keys {extra}")
    if tid not in SAMPLE_STOPS and "sample" in data:
        rep.err("sample", f"{tid} has no sample block: it opens with spot_md")
    if not path.name.startswith("_") and path.name != f"{tid}.json":
        rep.err("tid", f"file {path.name} holds {tid}: name it {tid}.json")
    if data.get("name") not in accepted_names(tid):
        rep.err("name", f"{data.get('name')!r} must be {TYPES[tid][0]!r}")
    minutes = data.get("minutes")
    if minutes != TYPES[tid][1] or isinstance(minutes, bool):
        rep.err("minutes", f"{minutes!r} must be {TYPES[tid][1]} for {tid}")
    for key in ("shape_md", "one_md", "spot_md", "say_md"):
        md_field(rep, key, data.get(key))
    check_bullets(rep, "spot_md", data.get("spot_md"), *SPOT_BULLETS)
    if not BULLET.search(str(data.get("say_md", ""))):
        rep.err("say_md", "should be a bullet list of the answer formula and key phrases")
    one = data.get("one_md")
    if isinstance(one, str) and validate.words(one) > 45:
        rep.warn("one_md", "the one idea should fit in one sentence")
    shape = data.get("shape_md")
    if isinstance(shape, str) and validate.words(shape) > 70:
        rep.warn("shape_md", "shape_md should be one or two sentences")
    max_basics = 2 if tid in SAMPLE_STOPS else 3
    count_between(rep, "basics", data.get("basics"), 1, max_basics)
    for key, (lo, hi) in COUNTS.items():
        count_between(rep, key, data.get(key), lo, hi)
    check_basics(rep, tid, as_list(data.get("basics")))
    check_checks(rep, tid, as_list(data.get("checks")))
    for i, step in enumerate(as_list(data.get("method"))):
        md_field(rep, f"method[{i}]", step)
    check_worked(rep, as_list(data.get("worked")))
    check_twists(rep, as_list(data.get("twists")))
    for i, trap in enumerate(as_list(data.get("traps"))):
        md_field(rep, f"traps[{i}]", trap)
    if "sample" in data and tid in SAMPLE_STOPS:
        check_sample(rep, tid, data["sample"], source)
    ids = as_list(data.get("practice"))
    picked = check_practice(rep, tid, ids, bank, others)
    check_short_answers(rep, data.get("short_answers"), picked)
    for text in strings_in({k: v for k, v in data.items() if k not in ("practice",)}):
        bad = misfiled_any(text)
        if bad:
            rep.err("text", f"files an Any error under 'types disagree': {bad[:80]!r}")
            break
    return rep


def default_files() -> list[Path]:
    return sorted(p for p in TYPES_DIR.glob("*.json") if TYPE_FILE.fullmatch(p.name))


def validate_files(paths: list[Path]) -> tuple[int, int]:
    """Validate and print each file; returns (errors, warnings)."""
    bank, _ = load_bank()
    try:
        source: official.Official | None = official.load()
    except official.OfficialError as exc:
        print(f"warning: his answers could not be read, the sample block is not checked: {exc}")
        source = None
    # An example file (name starts with _) is only checked against the other example files: the
    # real S*/P* files may use the same questions without that being a clash.
    real = {
        p.resolve(): p
        for p in [*default_files(), *(q for q in paths if not q.name.startswith("_"))]
    }
    examples = {p.resolve(): p for p in paths if p.name.startswith("_")}
    claims_real = claims_of(list(real.values()))
    claims_example = claims_of(list(examples.values()))
    errors = warnings = 0
    for path in paths:
        others = claims_example if path.name.startswith("_") else claims_real
        rep = validate_type(path, bank, {f: c for f, c in others.items() if f != path.name}, source)
        state = "FAIL" if rep.errors else "ok  "
        print(f"{state} {path.name}  {len(rep.errors)} errors, {len(rep.warnings)} warnings")
        for line in [*rep.errors, *rep.warnings]:
            print(f"  {line}")
        errors += len(rep.errors)
        warnings += len(rep.warnings)
    return errors, warnings


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv] or default_files()
    if not paths:
        print(
            "no type files found in types/ (S1.json ... S9.json, P1.json ... P4.json)",
            file=sys.stderr,
        )
        print("RESULT: FAIL")
        return 1
    errors, warnings = validate_files(paths)
    print(f"{len(paths)} files, {errors} errors, {warnings} warnings")
    print("RESULT: FAIL" if errors else "RESULT: PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
