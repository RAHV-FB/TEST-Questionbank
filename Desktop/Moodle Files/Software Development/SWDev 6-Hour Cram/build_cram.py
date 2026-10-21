"""Build the SWDev 6-Hour Cram page.

Usage (quote the paths, they contain spaces):
    uv run --project "<study-site>" python build_cram.py            # S1..S9, P1..P4 (all)
    uv run --project "<study-site>" python build_cram.py --example  # types/_example*.json only
    uv run --project "<study-site>" python build_cram.py --partial  # the S*/P* files that exist
    uv run --project "<study-site>" python build_cram.py --out DIR  # write under DIR, not here
    uv run --project "<study-site>" python build_cram.py --types DIR  # read type files from DIR

Reads types/*.json (files starting with _ are skipped, except with --example), route.json,
exam_intro.json, the bank questions the types practise (from study-site/content), the teacher's
nine sample questions with his official answers (official.py), and Papers A and B from
study-site/content/papers.json. Renders every Markdown field to HTML with Pygments highlighting
(the main site's renderer), embeds one JSON data block and writes two pages:
    <out>/SWDev 6-Hour Cram (offline).html      a full document
    <out>/dist/artifact.html                    the publish shape (no doctype, html, head or body)
The build stops with a message on any missing id or validation error; nothing is written then.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

# The main site's tools are read, never changed, and imported without leaving bytecode there.
sys.dont_write_bytecode = True
CRAM = Path(__file__).resolve().parent
SITE = CRAM.parent / "study-site"
sys.path.insert(0, str(SITE / "tools"))
import build as site_build  # noqa: E402
import validate  # noqa: E402

import official  # noqa: E402
import validate_types  # noqa: E402

CONTENT = SITE / "content"
APP = CRAM / "app"
TYPES_DIR = CRAM / "types"
TITLE = "SWDev 6-Hour Cram"
OFFLINE_NAME = "SWDev 6-Hour Cram (offline).html"
STORAGE_KEY = "swdev-cram6-v1"
FONTS = site_build.FONTS
MAX_BYTES = site_build.MAX_BYTES
MAX_ROUTE_MINUTES = 360

KINDS = ("intro", "baseline", "type", "break", "paper", "review", "mistakes", "final")
SAMPLE_ID = "sample"
SAMPLE_MINUTES = 30
SAMPLE_INTRO = (
    "The nine questions the teacher gave as a sample: six multiple choice, then three open "
    "questions. Sit it in 30 minutes, half the real hour, with a pen and no notes. Nothing is "
    "marked until you hand in, and the review shows his official answers. The sample shows the "
    "kind of question, not the exam."
)
PAPER_IDS = ("paper-a", "paper-b")
TYPE_FILE = re.compile(r"[SP]\d\.json")
EXAMPLE_FILE = re.compile(r"_example.*\.json")

# The stop that teaches a paper question that is not in a type's practice list, by module. A
# question about a mypy error goes to S3, a failing test to S4, a tool error to S1, a command
# that predicts output to S6; the open questions go by what they ask you to read (see tid_for).
BY_MODULE = {
    "project-anatomy": "P4",
    "cli-program": "P3",
    "clean-code": "S5",
    "core-shell-failing": "P3",
    "testing-tdd": "P4",
    "terminal-files": "P2",
    "pipes-bash": "P2",
    "sdlc-agile": "P1",
    "scrum": "P1",
    "history": "S8",
    "refactor-types": "S2",
}
TYPING = re.compile(
    r"mypy|type hint|annotat|\bAny\b|None|strict|type: ignore|union-attr|no-any|no-untyped", re.I
)
PYTEST_FAIL = re.compile(r"FAILED|AssertionError|\bassert\b")
TOOL_ERROR = re.compile(r"\berror:|\bfatal:|\brejected\b|\bFailed\b|\bhint:")


class BuildError(Exception):
    """A problem that stops the build; the message says what to fix."""


_UL = re.compile(r"<ul>(.*?)</ul>", re.S)
_LI = re.compile(r"<li>(.*?)</li>", re.S)
_LETTERED = re.compile(r"\s*(?:<p>)?[a-h]\)\s")


def lettered_lists(html: str) -> str:
    """Mark a list whose items all start "a) ", "b) " so no bullet is drawn before the letter."""

    def mark(found: re.Match[str]) -> str:
        items = _LI.findall(found.group(1))
        if len(items) >= 2 and all(_LETTERED.match(item) for item in items):
            return f'<ul class="lettered">{found.group(1)}</ul>'
        return found.group(0)

    return _UL.sub(mark, html)


def md(text: str) -> str:
    return lettered_lists(str(site_build.md_html(text)))


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"cannot read {path}: {exc}") from exc


def check_md(where: str, text: Any, errors: list[str]) -> None:
    rep = validate.Report(where)
    validate.check_md(rep, where, text)
    errors.extend(str(e) for e in rep.errors)


# ------------------------------------------------------------------------------- route


def load_route() -> list[dict[str, Any]]:
    data = read_json(CRAM / "route.json")
    stops = data.get("stops") if isinstance(data, dict) else None
    if not isinstance(stops, list) or not stops:
        raise BuildError('route.json must be an object with a non-empty "stops" list')
    return list(stops)


def check_route(
    stops: list[dict[str, Any]],
    tids: set[str],
    paper_ids: set[str],
    names: dict[str, str],
    allow_missing: bool,
) -> list[str]:
    """Problems in route.json. `allow_missing`: a type stop may lack its type file (and a type
    may be missing from the route); a full build needs every type on the route exactly once."""
    errors: list[str] = []
    seen: Counter[str] = Counter()
    total = 0
    for i, stop in enumerate(stops):
        where = f"route.json stop {i + 1}"
        kind, ref = stop.get("kind"), stop.get("ref")
        if kind not in KINDS:
            errors.append(f"{where}: kind {kind!r} is not one of {KINDS}")
            continue
        if not isinstance(ref, str) or not re.fullmatch(r"[A-Za-z0-9_~-]+", ref):
            errors.append(f"{where}: ref {ref!r} must match [A-Za-z0-9_~-]+")
            continue
        seen[f"{kind}-{ref}"] += 1
        for key in ("title", "note"):
            if not isinstance(stop.get(key), str) or not str(stop[key]).strip():
                errors.append(f"{where}: missing {key}")
        minutes = stop.get("minutes")
        if isinstance(minutes, bool) or not isinstance(minutes, int) or minutes <= 0:
            errors.append(f"{where}: minutes must be a positive whole number")
        else:
            total += minutes
        if kind == "type" and ref not in names:
            errors.append(f"{where}: type {ref} is not one of {sorted(names)}")
        if kind == "type" and ref in names and ref not in tids and not allow_missing:
            errors.append(f"{where}: no type file for {ref}")
        if kind == "baseline" and ref != SAMPLE_ID:
            errors.append(f"{where}: the baseline must be the sample paper (ref {SAMPLE_ID!r})")
        if kind in ("paper", "review") and ref not in paper_ids:
            errors.append(f"{where}: {ref} is not a paper (have {sorted(paper_ids)})")
    errors.extend(f"route.json: stop {key} appears {n} times" for key, n in seen.items() if n > 1)
    if total > MAX_ROUTE_MINUTES:
        errors.append(
            f"route.json: {total} minutes in all (the cram is {MAX_ROUTE_MINUTES} at most)"
        )
    if not allow_missing:
        for tid in sorted(names):
            if f"type-{tid}" not in seen:
                errors.append(f"route.json: type {tid} is not on the route")
    return errors


def route_data(stops: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": f"{s['kind']}-{s['ref']}",
            "kind": s["kind"],
            "ref": s["ref"],
            "title": s["title"],
            "minutes": s["minutes"],
            "note": s["note"],
        }
        for s in stops
    ]


# ------------------------------------------------------------------------------- types


def type_files(mode: str, types_dir: Path) -> list[Path]:
    if mode == "example":
        found = sorted(
            p for p in types_dir.glob("_example*.json") if EXAMPLE_FILE.fullmatch(p.name)
        )
        if not found:
            raise BuildError(f"no _example*.json in {types_dir}")
        return found
    return sorted(p for p in types_dir.glob("*.json") if TYPE_FILE.fullmatch(p.name))


def assign_checks(blocks: int, checks: int) -> list[int]:
    """The basics block that each quick check follows: spread evenly, earlier blocks first."""
    return [min(blocks - 1, (k * blocks) // checks) for k in range(checks)]


def render_sample(sample: dict[str, Any]) -> dict[str, Any]:
    """The sample block of S1..S9: his question, the way to try it, his answer, what it shows."""
    return {
        "qnum": sample["qnum"],
        "kind": sample["kind"],
        "question_html": md(sample["question_md"]),
        "options": [md(o) for o in sample.get("options", [])],
        "answer": sample.get("answer"),
        "parts": [md(p) for p in sample.get("parts", [])],
        "his_answer_html": md(sample["his_answer_md"]),
        "decoded_html": md(sample["decoded_md"]),
    }


def render_type(t: dict[str, Any]) -> dict[str, Any]:
    blocks = [
        {
            "id": b["id"],
            "heading_html": md(b["heading"]),
            "body_html": md(b["body_md"]),
            "checks": [],
        }
        for b in t["basics"]
    ]
    for check, at in zip(t["checks"], assign_checks(len(blocks), len(t["checks"])), strict=True):
        blocks[at]["checks"].append(
            {
                "id": check["id"],
                "q_html": md(check["q_md"]),
                "options": [md(o) for o in check["options"]],
                "answer": check["answer"],
                "why_html": md(check["why_md"]),
            }
        )
    return {
        "tid": t["tid"],
        "name": validate_types.TYPES[t["tid"]][0],
        "minutes": t["minutes"],
        "sample": render_sample(t["sample"]) if t.get("sample") else None,
        "shape_html": md(t["shape_md"]),
        "one_html": md(t["one_md"]),
        "spot_html": md(t["spot_md"]),
        "basics": blocks,
        "method": [md(s) for s in t["method"]],
        "worked": [
            {
                "title": w["title"],
                "question_html": md(w["question_md"]),
                "steps": [md(s) for s in w["steps_md"]],
                "answer_html": md(w["answer_md"]),
            }
            for w in t["worked"]
        ],
        "twists": [
            {"twist_html": md(x["twist_md"]), "how_html": md(x["how_md"])} for x in t["twists"]
        ],
        "traps": [md(x) for x in t["traps"]],
        "say_html": md(t["say_md"]),
        "practice": list(t["practice"]),
    }


# ----------------------------------------------------------------------------- questions


def question_data(q: dict[str, Any], tid: str, paper: str | None = None) -> dict[str, Any]:
    """One full question for the page: every *_md becomes *_html, every other field is kept
    (provenance included), plus the cram type it belongs to and, in a paper, the paper."""
    out: dict[str, Any] = site_build.convert(q)
    out["tid"] = tid
    if paper:
        out["paper"] = paper
    return out


def check_question(q: dict[str, Any]) -> list[str]:
    qid = q["id"]
    problems: list[str] = []
    if q["type"] == "mcq":
        if len(q.get("options", [])) != 4 or sum(1 for o in q["options"] if o.get("correct")) != 1:
            problems.append(f"{qid}: an mcq needs 4 options with exactly one correct")
    elif q["type"] == "open":
        if not q.get("parts"):
            problems.append(f"{qid}: an open question needs parts")
    elif q["type"] == "sort":
        if not q.get("items") or not q.get("categories"):
            problems.append(f"{qid}: a sort question needs categories and items")
    else:
        problems.append(f"{qid}: unknown type {q['type']!r}")
    return problems


def tid_for(q: dict[str, Any]) -> str:
    """The stop that teaches a paper question (used for "Revise first" and the mistakes list).
    Practice questions take the stop that practises them instead; the nine samples take Sn."""
    mid = str(q["mid"])
    stem = str(q.get("stem_md", ""))
    skills = set(q.get("skills", []))
    if q["type"] == "open":
        if "read-diff" in skills:
            return "S8"
        return "S9" if "read-tool-output" in skills else "S7"
    if mid == "refactor-types":
        return "S3" if TYPING.search(stem) else "S2"
    if mid == "project-anatomy" and TOOL_ERROR.search(stem):
        return "S1"
    if mid == "testing-tdd" and PYTEST_FAIL.search(stem):
        return "S4"
    if mid == "pipes-bash" and "predict-output" in skills:
        return "S6"
    return BY_MODULE[mid]


def sample_questions(by_module: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    sample = by_module.get("sample-paper", {})
    originals = [q for q in sample.values() if q.get("origin") == "teacher-sample"]
    originals.sort(key=lambda q: str(q["id"]))
    if len(originals) != 9:
        raise BuildError(
            f"the sample-paper module has {len(originals)} teacher-sample questions, need 9"
        )
    return originals


def sample_number(q: dict[str, Any]) -> int:
    return int(str(q["id"]).rsplit("q", 1)[1])


def attach_teacher_answer(data: dict[str, Any], n: int, source: official.Official) -> None:
    """Put his official answer on one of the nine originals, for the paper's review."""
    answer = source["answers"][n]
    if answer["kind"] == "mcq":
        data["teacher_answer_html"] = md(official.answer_md(answer))
    else:
        data["teacher_parts_html"] = {label: md(text) for label, text in answer["parts"].items()}


def paper_questions(paper: dict[str, Any]) -> list[dict[str, Any]]:
    """A mock paper's questions, each tagged with the module it draws on."""
    out = []
    for q in paper["questions"]:
        q = dict(q)
        q["mid"] = q["module_ref"]
        out.append(q)
    return out


def short_answers_html(raw: dict[str, Any], qid: str) -> dict[str, str]:
    return {str(label): md(str(text)) for label, text in raw[qid].items()}


# ---------------------------------------------------------------------------- the intro


def intro_data(
    errors: list[str], names: dict[str, str], source: official.Official
) -> dict[str, Any]:
    """The "How he marks" page: exam_intro.json rendered, his guide checked against his file."""
    intro = read_json(CRAM / "exam_intro.json")
    check_md("exam_intro limits_md", intro["limits_md"], errors)
    for i, fact in enumerate(intro["facts"]):
        check_md(f"exam_intro facts[{i}]", fact["value_md"], errors)
    for key in ("formula", "plan", "mcq"):
        for i, item in enumerate(intro[key]):
            check_md(f"exam_intro {key}[{i}]", item["text_md"], errors)
    marking = intro["marking"]
    check_md("exam_intro marking intro_md", marking["intro_md"], errors)
    his = [(label, text) for label, text in source["marking"]]
    mine = [(str(m["label"]), str(m["text"])) for m in marking["items"]]
    if mine != his:
        errors.append(
            "exam_intro.json: the marking guide must be his, word for word "
            f"(midterm-sample-answers.md has {his})"
        )
    for shape in intro["shapes"]:
        check_md(f"exam_intro shape {shape['n']}", shape["ask_md"], errors)
        for tid in shape["tids"]:
            if tid not in names:
                errors.append(f"exam_intro shape {shape['n']}: unknown type {tid}")
    plan_minutes = sum(int(item["minutes"]) for item in intro["plan"])
    if plan_minutes != 60:
        errors.append(f"exam_intro.json: the time plan adds up to {plan_minutes} minutes, not 60")
    check_md("sample intro", SAMPLE_INTRO, errors)
    return {
        "facts": [{"label": f["label"], "value_html": md(f["value_md"])} for f in intro["facts"]],
        "limits_html": md(intro["limits_md"]),
        "marking": {
            "intro_html": md(marking["intro_md"]),
            "items": [{"label": label, "text": text} for label, text in his],
        },
        "formula": [{"label": f["label"], "text_html": md(f["text_md"])} for f in intro["formula"]],
        "mcq": [md(m["text_md"]) for m in intro["mcq"]],
        "plan": [
            {"minutes": p["minutes"], "label": p["label"], "text_html": md(p["text_md"])}
            for p in intro["plan"]
        ],
        "shapes": [
            {"n": s["n"], "type": s["type"], "ask_html": md(s["ask_md"]), "tids": s["tids"]}
            for s in intro["shapes"]
        ],
    }


# --------------------------------------------------------------------------------- build


def build_data(mode: str, types_dir: Path) -> tuple[dict[str, Any], list[str]]:
    """The whole data block, and a list of warnings. Raises BuildError listing every problem."""
    errors: list[str] = []
    warnings: list[str] = []
    names = {tid: name for tid, (name, _) in validate_types.TYPES.items()}
    stops = load_route()
    try:
        source = official.load()
    except official.OfficialError as exc:
        raise BuildError(f"his sample questions or answers cannot be read: {exc}") from exc

    # the bank, the sample paper and the papers
    by_id, by_module = validate_types.load_bank()
    sample = sample_questions(by_module)
    papers_raw = [
        p for p in read_json(CONTENT / "papers.json")["papers"] if str(p["id"]) in PAPER_IDS
    ]
    papers_by_id = {str(p["id"]): p for p in papers_raw}
    if sorted(papers_by_id) != sorted(PAPER_IDS):
        errors.append(f"papers.json must hold {PAPER_IDS}, has {sorted(papers_by_id)}")
    paper_ids = {SAMPLE_ID, *papers_by_id}

    # types
    files = type_files(mode, types_dir)
    siblings = files if mode == "example" else type_files("full", types_dir)
    claims = validate_types.claims_of(sorted({*siblings, *files}))
    raw_types: dict[str, dict[str, Any]] = {}
    for path in files:
        others = {f: c for f, c in claims.items() if f != path.name}
        rep = validate_types.validate_type(path, by_id, others, source)
        errors.extend(f"{path.name}: {e}" for e in rep.errors)
        warnings.extend(f"{path.name}: {w}" for w in rep.warnings)
        if not rep.errors:
            data = read_json(path)
            raw_types[str(data["tid"])] = data
    missing = sorted(set(names) - set(raw_types))
    if mode == "full" and missing:
        errors.append(f"missing type files: {missing}")
    errors.extend(check_route(stops, set(raw_types), paper_ids, names, mode != "full"))
    for stop in stops:
        if (
            stop["kind"] == "type"
            and stop["ref"] in raw_types
            and stop["minutes"] != raw_types[stop["ref"]]["minutes"]
        ):
            warnings.append(
                f"route {stop['ref']}: {stop['minutes']} min in route.json, "
                f"{raw_types[stop['ref']]['minutes']} min in the type file (route.json wins)"
            )

    questions: dict[str, dict[str, Any]] = {}
    for tid, t in sorted(raw_types.items()):
        shorts = t.get("short_answers") or {}
        for qid in t["practice"]:
            q = by_id.get(qid)
            if q is None:
                errors.append(f"{tid}: practice id {qid} is not in the bank")
                continue
            errors.extend(check_question(q))
            data = question_data(q, tid)
            if q["type"] == "open" and qid in shorts:
                data["short_answers_html"] = short_answers_html(shorts, qid)
            questions[qid] = data
    for q in sample:
        errors.extend(check_question(q))
        n = sample_number(q)
        data = question_data(q, f"S{n}")
        attach_teacher_answer(data, n, source)
        questions[str(q["id"])] = data
    paper_list: list[dict[str, Any]] = [
        {
            "id": SAMPLE_ID,
            "title": "The teacher's sample paper",
            "kind": "sample",
            "minutes": SAMPLE_MINUTES,
            "intro_html": md(SAMPLE_INTRO),
            "questions": [str(q["id"]) for q in sample],
        }
    ]
    for pid in PAPER_IDS:
        paper = papers_by_id.get(pid)
        if paper is None:
            continue
        qs = paper_questions(paper)
        for q in qs:
            errors.extend(check_question(q))
            questions[str(q["id"])] = question_data(q, tid_for(q), pid)
        paper_list.append(
            {
                "id": paper["id"],
                "title": paper["title"],
                "kind": paper["kind"],
                "minutes": paper["minutes"],
                "intro_html": md(paper["intro_md"]),
                "questions": [str(q["id"]) for q in qs],
            }
        )

    intro = intro_data(errors, names, source)
    if errors:
        raise BuildError("\n".join(errors))

    data = {
        "meta": {
            "title": TITLE,
            "exam": site_build.EXAM,
            "built": datetime.now().astimezone().isoformat(timespec="seconds"),
            "mode": mode,
            "missing": missing if mode != "full" else [],
            "storage_key": STORAGE_KEY,
        },
        "names": names,
        "route": route_data(stops),
        "intro": intro,
        "types": {tid: render_type(t) for tid, t in sorted(raw_types.items())},
        "papers": paper_list,
        "questions": questions,
    }
    return data, warnings


def js_bundle() -> str:
    order_file = APP / "js" / "ORDER"
    names = [
        line.strip()
        for line in order_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    on_disk = {p.name for p in (APP / "js").glob("*.js")}
    missing = [n for n in names if n not in on_disk]
    unlisted = sorted(on_disk - set(names))
    repeated = sorted(n for n, count in Counter(names).items() if count > 1)
    if missing or unlisted or repeated:
        raise BuildError(
            f"app/js/ORDER: missing files {missing}, unlisted files {unlisted}, "
            f"files listed twice {repeated}"
        )
    parts = ['"use strict";']
    for name in names:
        src = (APP / "js" / name).read_text(encoding="utf-8")
        if re.search(r"</script", src, re.IGNORECASE):
            raise BuildError(f"app/js/{name} contains '</script'")
        parts.append(f"/* ---- {name} ---- */\n{src.strip()}")
    return "\n".join(parts) + "\n"


def stylesheet() -> str:
    css = (APP / "cram.css").read_text(encoding="utf-8")
    if re.search(r"</style", css, re.IGNORECASE):
        raise BuildError("app/cram.css contains '</style'")
    return css.strip()


def page_parts(data: dict[str, Any]) -> tuple[str, str]:
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # Safe inside <script type="application/json">: no "</script" and no "<!--".
    blob = blob.replace("</", "<\\/").replace("<!--", "<\\u0021--")
    shell = (APP / "shell.html").read_text(encoding="utf-8").strip()
    head = (
        f"<title>{TITLE}</title>\n<style>\n{stylesheet()}\n</style>\n"
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'<link rel="stylesheet" href="{FONTS}">\n'
    )
    body = (
        f"{shell}\n"
        f'<script type="application/json" id="cram-data">{blob}</script>\n'
        f"<script>\n{js_bundle()}</script>\n"
    )
    return head, body


def write_pages(head: str, body: str, out: Path) -> list[Path]:
    (out / "dist").mkdir(parents=True, exist_ok=True)
    artifact = out / "dist" / "artifact.html"
    artifact.write_text(head + body, encoding="utf-8")
    offline = out / OFFLINE_NAME
    offline.write_text(
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"{head}</head>\n<body>\n{body}</body>\n</html>\n",
        encoding="utf-8",
    )
    return [offline, artifact]


def build(mode: str, out: Path, types_dir: Path) -> int:
    print(f"Building the cram ({mode}) from {types_dir.name}/, route.json and the study-site bank")
    data, warnings = build_data(mode, types_dir)
    for line in warnings:
        print(f"  warning {line}")
    head, body = page_parts(data)
    paths = write_pages(head, body, out)
    kinds = Counter(q["type"] for q in data["questions"].values())
    print(
        f"  {len(data['types'])} types, {len(data['questions'])} questions {dict(kinds)}, "
        f"{len(data['papers'])} papers, {len(data['route'])} stops, "
        f"{sum(s['minutes'] for s in data['route'])} minutes"
    )
    if data["meta"]["missing"]:
        print(f"  not built (no type file): {', '.join(data['meta']['missing'])}")
    for path in paths:
        size = path.stat().st_size
        print(f"  wrote {path}  {size / 1024:,.0f} KiB")
        if size > MAX_BYTES:
            raise BuildError(f"{path.name} is over the 16 MB artifact limit")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--example", action="store_true", help="build from types/_example.json only")
    group.add_argument("--partial", action="store_true", help="build the T*.json files that exist")
    parser.add_argument("--out", type=Path, default=CRAM, help="base folder for the two pages")
    parser.add_argument("--types", type=Path, default=TYPES_DIR, help="folder of the type files")
    args = parser.parse_args(argv)
    mode = "example" if args.example else "partial" if args.partial else "full"
    try:
        return build(mode, args.out.resolve(), args.types.resolve())
    except BuildError as exc:
        print(f"BUILD FAILED:\n{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
