"""Split the verified study-site question bank into one disjoint pool per cram exercise type.

Run: uv run --project ../study-site python make_pools.py   -> writes pools.json
"""

import json
import re
from collections import Counter
from pathlib import Path

BANK = Path(__file__).resolve().parent.parent / "study-site" / "content"
TYPES = {
    "T01": "Tool errors and project setup",
    "T02": "Programs and the command line",
    "T03": "Clean-code problems",
    "T04": "Refactoring or not",
    "T05": "mypy errors and the right fix",
    "T06": "Core, shell and failing well",
    "T07": "Failing tests, pytest and TDD",
    "T08": "Paths, files and permissions",
    "T09": "Pipes, text wrangling and bash scripts",
    "T10": "Process: lifecycle, Agile and Scrum",
    "T11": "Diffs and commit messages",
    "T12": "Writing the open answers",
}
BY_MODULE = {
    "project-anatomy": "T01",
    "cli-program": "T02",
    "clean-code": "T03",
    "core-shell-failing": "T06",
    "testing-tdd": "T07",
    "terminal-files": "T08",
    "pipes-bash": "T09",
    "sdlc-agile": "T10",
    "scrum": "T10",
    "history": "T11",
}
SAMPLE_ORIGINAL = {1: "T01", 2: "T04", 3: "T05", 4: "T07", 5: "T03", 6: "T09"}
TYPING = re.compile(r"mypy|type hint|annotat|\bAny\b|None|strict|type: ignore|union-attr|no-any|no-untyped", re.I)


def assign(mid: str, q: dict[str, object], by_id: dict[str, dict[str, object]]) -> str:
    if mid == "sample-paper":
        orig = q if q.get("origin") == "teacher-sample" else by_id.get(str(q.get("variant_of")), q)
        num = int(str(orig["id"]).rsplit("q", 1)[1])
        if q["type"] == "open" or num > 6:
            return "T12"
        return SAMPLE_ORIGINAL[num]
    if mid == "refactor-types":
        return "T05" if TYPING.search(str(q.get("stem_md", ""))) else "T04"
    return BY_MODULE[mid]


def main() -> None:
    pools: dict[str, list[dict[str, object]]] = {t: [] for t in TYPES}
    for path in sorted(BANK.glob("*.json")):
        if path.name.startswith("_") or path.name in {"plan.json", "papers.json"}:
            continue
        mod = json.loads(path.read_text())
        by_id = {q["id"]: q for q in mod["questions"]}
        for q in mod["questions"]:
            tid = assign(mod["id"], q, by_id)
            stem = re.sub(r"\s+", " ", re.sub(r"```.*?```", "[artefact]", q["stem_md"], flags=re.S))
            pools[tid].append({"id": q["id"], "type": q["type"], "level": q["level"],
                               "skills": q["skills"], "stem": stem[:220]})
    out = {"types": TYPES, "pools": pools}
    Path("pools.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    for tid, items in pools.items():
        c = Counter(i["type"] for i in items)
        print(tid, TYPES[tid], len(items), dict(c))


if __name__ == "__main__":
    main()
