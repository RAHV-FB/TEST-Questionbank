"""Build the SWDev 12-Hour Cram page.

Usage (quote the paths, they contain spaces):
    uv run --project "<study-site>" python build_cram.py            # all of T01..T12 (required)
    uv run --project "<study-site>" python build_cram.py --example  # types/_example.json only
    uv run --project "<study-site>" python build_cram.py --partial  # the T*.json files that exist
    uv run --project "<study-site>" python build_cram.py --out DIR  # write under DIR, not here
    uv run --project "<study-site>" python build_cram.py --types DIR  # read type files from DIR

Reads types/*.json (files starting with _ are skipped, except with --example), route.json,
exam_intro.json, the bank questions the types practise (from study-site/content), the nine
teacher-sample questions, and study-site/content/papers.json. Renders every Markdown field to
HTML with Pygments highlighting (the main site's renderer), embeds one JSON data block and
writes two pages:
    <out>/SWDev 12-Hour Cram (offline).html     a full document
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

import make_pools  # noqa: E402
import validate_types  # noqa: E402

CONTENT = SITE / "content"
APP = CRAM / "app"
TYPES_DIR = CRAM / "types"
TITLE = "SWDev 12-Hour Cram"
OFFLINE_NAME = "SWDev 12-Hour Cram (offline).html"
FONTS = site_build.FONTS
MAX_BYTES = site_build.MAX_BYTES

KINDS = ("intro", "baseline", "type", "break", "paper", "review", "mistakes", "final")
SAMPLE_ID = "sample"
SAMPLE_MINUTES = 30
SAMPLE_INTRO = (
    "The nine questions the teacher gave as a sample: six multiple choice, then three open "
    "questions. Sit it in 30 minutes, half the real hour, with a pen and no notes. Nothing is "
    "marked until you hand in. The sample shows the kind of question, not the exam."
)
TYPE_FILE = re.compile(r"T\d\d\.json")


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
    """Problems in route.json. `allow_missing`: a type stop may lack its type file."""
    errors: list[str] = []
    seen: Counter[str] = Counter()
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
        if kind == "type" and ref not in names:
            errors.append(f"{where}: type {ref} is not one of {sorted(names)}")
        if kind == "type" and ref in names and ref not in tids and not allow_missing:
            errors.append(f"{where}: no type file for {ref}")
        if kind == "baseline" and ref != SAMPLE_ID:
            errors.append(f"{where}: the baseline must be the sample paper (ref {SAMPLE_ID!r})")
        if kind in ("paper", "review") and ref not in paper_ids:
            errors.append(f"{where}: {ref} is not a paper (have {sorted(paper_ids)})")
    errors.extend(f"route.json: stop {key} appears {n} times" for key, n in seen.items() if n > 1)
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
        path = types_dir / "_example.json"
        if not path.exists():
            raise BuildError(f"{path} is missing")
        return [path]
    return sorted(p for p in types_dir.glob("T*.json") if TYPE_FILE.fullmatch(p.name))


def assign_checks(blocks: int, checks: int) -> list[int]:
    """The basics block that each quick check follows: spread evenly, earlier blocks first."""
    return [min(blocks - 1, (k * blocks) // checks) for k in range(checks)]


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
        "name": t["name"],
        "minutes": t["minutes"],
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


def load_bank() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, dict[str, Any]]]]:
    """(every module question by id, with its module id) and (questions of each module by id)."""
    by_id: dict[str, dict[str, Any]] = {}
    by_module: dict[str, dict[str, dict[str, Any]]] = {}
    for path in sorted(CONTENT.glob("*.json")):
        if path.name.startswith("_") or path.name in validate.NON_MODULES:
            continue
        mod = read_json(path)
        mid = str(mod["id"])
        by_module[mid] = {}
        for q in mod["questions"]:
            q = dict(q)
            q["mid"] = mid
            by_id[str(q["id"])] = q
            by_module[mid][str(q["id"])] = q
    return by_id, by_module


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


def tid_of(q: dict[str, Any], module_questions: dict[str, dict[str, Any]]) -> str:
    """The cram type a question belongs to (the same split as make_pools.py)."""
    return str(make_pools.assign(str(q["mid"]), q, module_questions))


def sample_questions(by_module: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    sample = by_module.get("sample-paper", {})
    originals = [q for q in sample.values() if q.get("origin") == "teacher-sample"]
    originals.sort(key=lambda q: str(q["id"]))
    if len(originals) != 9:
        raise BuildError(
            f"the sample-paper module has {len(originals)} teacher-sample questions, need 9"
        )
    return originals


def paper_questions(paper: dict[str, Any]) -> list[dict[str, Any]]:
    """A mock paper's questions, each tagged with the module it draws on."""
    out = []
    for q in paper["questions"]:
        q = dict(q)
        q["mid"] = q["module_ref"]
        out.append(q)
    return out


# --------------------------------------------------------------------------------- build


def build_data(mode: str, types_dir: Path) -> tuple[dict[str, Any], list[str]]:
    """The whole data block, and a list of warnings. Raises BuildError listing every problem."""
    errors: list[str] = []
    warnings: list[str] = []
    names, pools = validate_types.load_pools()
    stops = load_route()

    # types
    files = type_files(mode, types_dir)
    claims = validate_types.claims_of(
        sorted(p for p in types_dir.glob("T*.json") if TYPE_FILE.fullmatch(p.name))
    )
    claims.update(validate_types.claims_of(files))
    raw_types: dict[str, dict[str, Any]] = {}
    for path in files:
        rep = validate_types.validate_type(path, names, pools, claims)
        errors.extend(f"{path.name}: {e}" for e in rep.errors)
        warnings.extend(f"{path.name}: {w}" for w in rep.warnings)
        if not rep.errors:
            data = read_json(path)
            raw_types[str(data["tid"])] = data
    missing = sorted(set(names) - set(raw_types))
    if mode == "full" and missing:
        errors.append(f"missing type files: {missing}")

    # bank, sample, papers
    by_id, by_module = load_bank()
    sample = sample_questions(by_module)
    papers_raw = read_json(CONTENT / "papers.json")["papers"]
    papers_by_id = {str(p["id"]): p for p in papers_raw}
    paper_ids = {SAMPLE_ID, *papers_by_id}
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
        for qid in t["practice"]:
            q = by_id.get(qid)
            if q is None:
                errors.append(f"{tid}: practice id {qid} is not in the bank")
                continue
            errors.extend(check_question(q))
            questions[qid] = question_data(q, tid)
    for q in sample:
        errors.extend(check_question(q))
        tid = tid_of(q, by_module["sample-paper"])
        if q["id"] not in questions:
            questions[str(q["id"])] = question_data(q, tid)
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
    for paper in papers_raw:
        qs = paper_questions(paper)
        for q in qs:
            errors.extend(check_question(q))
            module_questions = by_module.get(str(q["mid"]), {})
            questions[str(q["id"])] = question_data(
                q, tid_of(q, module_questions), str(paper["id"])
            )
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

    intro = read_json(CRAM / "exam_intro.json")
    check_md("exam_intro limits_md", intro["limits_md"], errors)
    for key in ("technique",):
        for i, text in enumerate(intro[key]):
            check_md(f"exam_intro {key}[{i}]", text, errors)
    for i, fact in enumerate(intro["facts"]):
        check_md(f"exam_intro facts[{i}]", fact["value_md"], errors)
    for shape in intro["shapes"]:
        check_md(f"exam_intro shape {shape['n']}", shape["ask_md"], errors)
        for tid in shape["tids"]:
            if tid not in names:
                errors.append(f"exam_intro shape {shape['n']}: unknown type {tid}")
    check_md("sample intro", SAMPLE_INTRO, errors)

    if errors:
        raise BuildError("\n".join(errors))

    data = {
        "meta": {
            "title": TITLE,
            "exam": site_build.EXAM,
            "built": datetime.now().astimezone().isoformat(timespec="seconds"),
            "mode": mode,
            "missing": missing if mode != "full" else [],
        },
        "names": names,
        "route": route_data(stops),
        "intro": {
            "facts": [
                {"label": f["label"], "value_html": md(f["value_md"])} for f in intro["facts"]
            ],
            "limits_html": md(intro["limits_md"]),
            "technique": [md(t) for t in intro["technique"]],
            "shapes": [
                {"n": s["n"], "type": s["type"], "ask_html": md(s["ask_md"]), "tids": s["tids"]}
                for s in intro["shapes"]
            ],
        },
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
