"""Merge the mock-paper part files (content/_papers-*.json) into content/papers.json.

Each part file is {"papers": [...]} written by its own generator script in content/src/.
Run: uv run python content/src/papers.py
"""

import json
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent


def main() -> None:
    papers: list[dict[str, object]] = []
    for part in sorted(CONTENT.glob("_papers-*.json")):
        papers.extend(json.loads(part.read_text())["papers"])
    papers.sort(key=lambda p: str(p["id"]))
    out = CONTENT / "papers.json"
    out.write_text(json.dumps({"papers": papers}, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {out.name}: {[p['id'] for p in papers]}")


if __name__ == "__main__":
    main()
