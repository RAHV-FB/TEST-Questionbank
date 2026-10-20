"""Validate the cram's type files (types/<tid>.json) against CRAM_SPEC.md.

Usage (from anywhere; quote the paths, they contain spaces):
    uv run --project "<study-site>" python validate_types.py                 # every types/T*.json
    uv run --project "<study-site>" python validate_types.py types/T05.json  # one or more files

Checks fields and counts, that every practice id is in pools.json for the file's tid, that no
id is used by two types (the other type files in types/ are read too), that every check has a
valid answer index, and the Markdown rules of the main site (fences tagged and balanced, banned
phrases, British spelling, no emoji or raw HTML). Prints errors and warnings, then RESULT: PASS
or RESULT: FAIL (exit code 1).
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

TYPES_DIR = CRAM / "types"
POOLS = CRAM / "pools.json"

LEVEL_RANK = {"core": 0, "exam": 1, "hard": 2, "beyond": 3}
TOP_KEYS = {
    "tid",
    "name",
    "shape_md",
    "minutes",
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
COUNTS = {
    "basics": (2, 4),
    "checks": (3, 5),
    "method": (3, 6),
    "worked": (1, 2),
    "twists": (4, 8),
    "traps": (4, 8),
    "practice": (10, 14),
}
CHECK_OPTIONS = (3, 4)
BODY_WORDS = (120, 320)  # advised range; a warning outside it
BODY_HARD = (90, 400)  # an error outside it
MINUTES = (15, 90)
TID = re.compile(r"T\d\d")
TYPE_FILE = re.compile(r"T\d\d\.json")


def load_pools() -> tuple[dict[str, str], dict[str, dict[str, dict[str, Any]]]]:
    """(names by tid, pool question summaries by tid and id) from pools.json."""
    data = json.loads(POOLS.read_text(encoding="utf-8"))
    names: dict[str, str] = data["types"]
    pools = {tid: {str(q["id"]): q for q in items} for tid, items in data["pools"].items()}
    return names, pools


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
        if not isinstance(steps, list) or not 2 <= len(steps) <= 8:
            rep.err(where, "steps_md must be a list of 2–8 Markdown strings")
            steps = []
        for j, step in enumerate(steps):
            md_field(rep, f"{where}.steps_md[{j}]", step)
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
        extra = set(twist) - {"twist_md", "how_md"}
        if extra:
            rep.warn(where, f"unknown keys {sorted(extra)}")


def check_practice(
    rep: Any,
    tid: str,
    ids: list[Any],
    pool: dict[str, dict[str, Any]],
    others: dict[str, dict[str, str]],
) -> None:
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
        if qid not in pool:
            rep.err(where, f"{qid} is not in pools.json for {tid}")
            continue
        picked.append(pool[qid])
        for file, claimed in others.items():
            other = claimed.get(qid)
            if other is not None and other != tid:
                rep.err(where, f"{qid} is also used by {other} ({file})")
    if not picked:
        return
    n = len(picked)
    levels = [str(q["level"]) for q in picked]
    core = levels.count("core")
    hard = levels.count("hard") + levels.count("beyond")
    opens = sum(1 for q in picked if q["type"] == "open")
    if core > max(2, round(n * 0.35)):
        rep.warn("practice", f"{core} of {n} questions are core (aim for about 20%)")
    if hard < round(n * 0.2):
        rep.warn("practice", f"only {hard} of {n} questions are hard or beyond (aim for about 30%)")
    if tid == "T12":
        if opens * 2 < n:
            rep.warn("practice", f"T12 is mostly open, but only {opens} of {n} are open")
    elif not 2 <= opens <= 4:
        rep.warn("practice", f"{opens} open questions (an open-heavy type wants 2–4)")
    ranks = [LEVEL_RANK.get(level, 1) for level in levels]
    backwards = sum(1 for a, b in zip(ranks, ranks[1:], strict=False) if b < a)
    if backwards > max(3, n // 3):
        rep.warn("practice", "order is not core to hard (open questions may close the list)")
    kinds = {str(q["type"]) for q in picked}
    if "mcq" not in kinds:
        rep.err("practice", "no multiple-choice question")


def validate_type(
    path: Path,
    names: dict[str, str],
    pools: dict[str, dict[str, dict[str, Any]]],
    others: dict[str, dict[str, str]],
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
    missing = sorted(TOP_KEYS - set(data))
    if missing:
        rep.err("file", f"missing keys {missing}")
    extra = sorted(set(data) - TOP_KEYS)
    if extra:
        rep.warn("file", f"unknown keys {extra}")
    tid = data.get("tid")
    if not isinstance(tid, str) or not TID.fullmatch(tid) or tid not in names:
        rep.err("tid", f"{tid!r} is not one of {sorted(names)}")
        return rep
    if not path.name.startswith("_") and path.name != f"{tid}.json":
        rep.err("tid", f"file {path.name} holds {tid}: name it {tid}.json")
    if data.get("name") != names[tid]:
        rep.err("name", f"{data.get('name')!r} must be {names[tid]!r}")
    minutes = data.get("minutes")
    if (
        isinstance(minutes, bool)
        or not isinstance(minutes, int)
        or not MINUTES[0] <= minutes <= MINUTES[1]
    ):
        rep.err(
            "minutes", f"{minutes!r} must be a whole number of minutes ({MINUTES[0]}–{MINUTES[1]})"
        )
    for key in ("shape_md", "one_md", "spot_md", "say_md"):
        md_field(rep, key, data.get(key))
    for key, (lo, hi) in COUNTS.items():
        count_between(rep, key, data.get(key), lo, hi)
    check_basics(rep, tid, data["basics"] if isinstance(data.get("basics"), list) else [])
    check_checks(rep, tid, data["checks"] if isinstance(data.get("checks"), list) else [])
    for i, step in enumerate(data["method"] if isinstance(data.get("method"), list) else []):
        md_field(rep, f"method[{i}]", step)
    check_worked(rep, data["worked"] if isinstance(data.get("worked"), list) else [])
    check_twists(rep, data["twists"] if isinstance(data.get("twists"), list) else [])
    for i, trap in enumerate(data["traps"] if isinstance(data.get("traps"), list) else []):
        md_field(rep, f"traps[{i}]", trap)
    practice = data.get("practice")
    check_practice(
        rep,
        tid,
        practice if isinstance(practice, list) else [],
        pools.get(tid, {}),
        {file: claimed for file, claimed in others.items() if file != path.name},
    )
    return rep


def default_files() -> list[Path]:
    return sorted(p for p in TYPES_DIR.glob("T*.json") if TYPE_FILE.fullmatch(p.name))


def validate_files(paths: list[Path]) -> tuple[int, int]:
    """Validate and print each file; returns (errors, warnings)."""
    names, pools = load_pools()
    siblings = default_files()
    everyone = {p.resolve(): p for p in [*siblings, *paths]}
    others = claims_of(list(everyone.values()))
    errors = warnings = 0
    for path in paths:
        rep = validate_type(path, names, pools, others)
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
        print("no type files found in types/ (T01.json ... T12.json)", file=sys.stderr)
        print("RESULT: FAIL")
        return 1
    errors, warnings = validate_files(paths)
    print(f"{len(paths)} files, {errors} errors, {warnings} warnings")
    print("RESULT: FAIL" if errors else "RESULT: PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
