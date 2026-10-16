"""Build the study site: content JSON -> one data blob -> dist/index.html and dist/artifact.html.

Usage:
    uv run python tools/build.py              # content/*.json (not _*), papers.json, plan.json
    uv run python tools/build.py --fixture    # content/_fixture.json + content/plan.json
    uv run python tools/build.py --out DIR    # write the two pages to DIR instead of dist/

The page is app/styles.css plus any app/css/*.css (one file per view, in name order),
app/shell.html, and the scripts listed in app/js/ORDER, all inlined.

Every module is checked with tools/validate.py and every paper with the question rules of
tools/validate_papers.py; the build refuses to run on any error. With --fixture the size rules
(minimum counts of sections, cards, questions, pipelines, commits and papers' shapes) are relaxed,
because the fixture is deliberately small; every other rule still applies.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from collections.abc import Sequence
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markdown_it.token import Token
from markdown_it.utils import EnvType, OptionsDict
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexer import Lexer
from pygments.lexers import (
    BashLexer,
    BashSessionLexer,
    IniLexer,
    PythonLexer,
    TOMLLexer,
    YamlLexer,
)

import validate
import validate_papers

SITE = Path(__file__).resolve().parent.parent
CONTENT = SITE / "content"
APP = SITE / "app"
DIST = SITE / "dist"
REPO = validate.REPO

TITLE = "Software Development Mid-term"
FONTS = (
    "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500"
    "&family=IBM+Plex+Sans+Condensed:wght@500;600"
    "&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap"
)
EXAM = {
    "date": "2026-10-22T14:00:00+02:00",
    "minutes": 60,
    "room": "108",
    "weight": "30%",
    "sessions": "1–10",
}
MAX_BYTES = 16 * 1024 * 1024
LONG_FILE_DIFF = 150
DIFF_EXCLUDES = ("uv.lock", "expenses.csv")
ROUTE_LINK = re.compile(r"#[A-Za-z0-9._~-]+")

# Errors the fixture may break on purpose: it is a small module set, not real content.
FIXTURE_RELAXED = (
    re.compile(r"\d+ sections \(want"),
    re.compile(r"\d+ flashcards \(min"),
    re.compile(r"\d+ (mcq|open|sort) questions \(min"),
    re.compile(r"pipelines must have"),
    re.compile(r"commits must be all"),
    re.compile(r"teacher-sample questions \(need"),
)

LEXERS: dict[str, Lexer] = {
    "python": PythonLexer(),
    "toml": TOMLLexer(),
    "bash": BashLexer(),
    "console": BashSessionLexer(),
    "yaml": YamlLexer(),
    "ini": IniLexer(),
}
LANG_LABEL = {"console": "terminal", "text": "output"}
FORMATTER = HtmlFormatter(nowrap=True)


class BuildError(Exception):
    """A problem that stops the build; the message says what to fix."""


def shown(path: Path) -> str:
    """A path relative to the site when it is inside it, else as given."""
    return str(path.relative_to(SITE)) if path.is_relative_to(SITE) else str(path)


# --------------------------------------------------------------------------- markdown


def render_code(code: str, lang: str) -> str:
    """Highlight one code block at build time and wrap it in the page's code frame."""
    if lang == "diff":
        body = render_diff(code)
    elif lang in LEXERS:
        body = highlight(code, LEXERS[lang], FORMATTER).rstrip("\n")
    elif lang in ("text", ""):
        body = escape(code.rstrip("\n"), quote=False)
    else:
        raise BuildError(f"no highlighter for code fence language {lang!r}")
    label = LANG_LABEL.get(lang, lang)
    tag = f'<span class="code-lang" aria-hidden="true">{escape(label)}</span>' if label else ""
    return (
        f'<div class="code" data-lang="{escape(lang)}">{tag}'
        f'<pre tabindex="0"><code>{body}</code></pre></div>\n'
    )


def render_diff(code: str) -> str:
    """One block span per line, classed as header, hunk, added, removed or context."""
    lines = code.rstrip("\n").split("\n")
    header = bool(lines) and lines[0].startswith(("diff --git", "--- "))
    out = []
    for line in lines:
        if line.startswith("diff --git"):
            header = True
        if header:
            kind = "d-hunk" if line.startswith("@@") else "d-meta"
            header = not line.startswith("@@")
        elif line.startswith("@@"):
            kind = "d-hunk"
        elif line.startswith("+"):
            kind = "d-add"
        elif line.startswith("-"):
            kind = "d-del"
        elif line.startswith("\\"):
            kind = "d-meta"
        else:
            kind = "d-ctx"
        out.append(f'<span class="dline {kind}">{escape(line, quote=False) or " "}</span>')
    return "".join(out)


def _fence(
    self: RendererHTML, tokens: Sequence[Token], idx: int, options: OptionsDict, env: EnvType
) -> str:
    token = tokens[idx]
    return render_code(token.content, token.info.strip().split(" ")[0])


def _code_block(
    self: RendererHTML, tokens: Sequence[Token], idx: int, options: OptionsDict, env: EnvType
) -> str:
    return render_code(tokens[idx].content, "text")


def _table_open(
    self: RendererHTML, tokens: Sequence[Token], idx: int, options: OptionsDict, env: EnvType
) -> str:
    return '<div class="table-wrap" tabindex="0"><table>\n'


def _table_close(
    self: RendererHTML, tokens: Sequence[Token], idx: int, options: OptionsDict, env: EnvType
) -> str:
    return "</table></div>\n"


def _heading(
    self: RendererHTML, tokens: Sequence[Token], idx: int, options: OptionsDict, env: EnvType
) -> str:
    # Content headings sit below the page's own h1, so they start at h2.
    token = tokens[idx]
    level = min(6, int(token.tag[1]) + 1)
    if token.type == "heading_open":
        return f"<h{level}>"
    return f"</h{level}>\n"


def make_markdown() -> MarkdownIt:
    # Curly quotes in prose only: code spans and fences are untouched, and the other
    # "typographer" replacements (dashes, ellipses, (c)) stay off.
    md = (
        MarkdownIt("commonmark", {"html": False, "typographer": True, "quotes": "“”‘’"})
        .enable("table")
        .enable("smartquotes")
        .disable("replacements")
        .disable("image")
    )
    md.add_render_rule("fence", _fence)
    md.add_render_rule("code_block", _code_block)
    md.add_render_rule("table_open", _table_open)
    md.add_render_rule("table_close", _table_close)
    md.add_render_rule("heading_open", _heading)
    md.add_render_rule("heading_close", _heading)
    return md


MD = make_markdown()
SINGLE_PARAGRAPH = re.compile(r"<p>(.*)</p>\n", re.DOTALL)


def md_html(text: str) -> str:
    """Markdown to HTML; a lone paragraph is unwrapped so it can sit inline (options, rubric)."""
    html: str = MD.render(text)
    one = SINGLE_PARAGRAPH.fullmatch(html)
    inner = str(one.group(1)) if one else ""
    if one and "<p>" not in inner and "</p>" not in inner:
        return inner
    return html.rstrip("\n")


MD_LISTS = ("key_points", "traps", "rubric")
INLINE_KEYS = ("heading", "term")


def convert(node: Any) -> Any:
    """Every *_md key becomes *_html; key_points, traps and rubric become lists of HTML."""
    if isinstance(node, list):
        return [convert(item) for item in node]
    if not isinstance(node, dict):
        return node
    out: dict[str, Any] = {}
    for key, value in node.items():
        if key.endswith("_md") and isinstance(value, str):
            out[key[:-3] + "_html"] = md_html(value)
        elif key in MD_LISTS and isinstance(value, list):
            out[key] = [md_html(str(item)) for item in value]
        else:
            out[key] = convert(value)
        if key in INLINE_KEYS and isinstance(value, str):
            out[key + "_html"] = md_html(value)
    return out


# ---------------------------------------------------------------------------- loading


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"cannot read {path.relative_to(SITE)}: {exc}") from exc


def read_list(path: Path, key: str) -> list[dict[str, Any]]:
    """The list stored under `key` in a JSON file shaped {key: [...]}; [] when the file is absent."""
    if not path.exists():
        return []
    data = read_json(path)
    items = data.get(key) if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise BuildError(f'{shown(path)} must be an object with a "{key}" list')
    return items


def load_sources(fixture: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]], Any]:
    """Return (modules, papers, plan days) for the chosen mode. papers.json and plan.json are
    used when present."""
    plan = read_list(CONTENT / "plan.json", "days")
    if fixture:
        data = read_json(CONTENT / "_fixture.json")
        return list(data.get("modules", [])), list(data.get("papers", [])), plan
    modules = [
        read_json(p)
        for p in sorted(CONTENT.glob("*.json"))
        if not p.name.startswith("_") and p.name not in validate.NON_MODULES
    ]
    return modules, read_list(CONTENT / "papers.json", "papers"), plan


# ------------------------------------------------------------------------- validation


def relaxed(line: str, fixture: bool) -> bool:
    return fixture and any(p.search(line) for p in FIXTURE_RELAXED)


def check_modules(modules: list[dict[str, Any]], fixture: bool) -> list[str]:
    """Run the content validator on each module; return the error lines that apply."""
    errors: list[str] = []
    all_ids: Counter[str] = Counter()
    with tempfile.TemporaryDirectory() as tmp:
        for mod in modules:
            mid = mod.get("id") if isinstance(mod, dict) else None
            if not isinstance(mid, str) or not mid:
                errors.append("ERROR   a module has no id")
                continue
            path = Path(tmp) / f"{mid}.json"
            path.write_text(json.dumps(mod, ensure_ascii=False), encoding="utf-8")
            rep = validate.validate_module(path, all_ids)
            mine = [f"{mid}: {e}" for e in rep.errors if not relaxed(e, fixture)]
            errors.extend(mine)
            state = "FAIL" if mine else "ok  "
            print(f"  {state} {mid:<20} {len(rep.warnings)} warnings")
    dupes = sorted(i for i, n in all_ids.items() if n > 1)
    if dupes:
        errors.append(f"ERROR   duplicate ids across modules: {dupes[:20]}")
    return errors


def check_papers(
    papers: list[dict[str, Any]], modules: list[dict[str, Any]], fixture: bool
) -> list[str]:
    rep = validate.Report("papers")
    sections = {
        str(m.get("id")): {str(s.get("id")) for s in m.get("sections") or [] if isinstance(s, dict)}
        for m in modules
    }
    seen: Counter[str] = Counter()
    for paper in papers:
        if not isinstance(paper, dict):
            rep.err("?", "every paper must be an object")
            continue
        pid = str(paper.get("id", "?"))
        if not re.fullmatch(r"paper-[a-z]", pid):
            rep.err(pid, "paper id must be paper-<letter>")
        kind = paper.get("kind")
        if kind not in validate_papers.KINDS:
            rep.err(pid, f"kind must be one of {sorted(validate_papers.KINDS)}")
        if paper.get("minutes") != 60:
            rep.err(pid, "minutes must be 60")
        if not paper.get("title"):
            rep.err(pid, "missing title")
        validate.check_md(rep, f"{pid}.intro_md", paper.get("intro_md"))
        questions = paper.get("questions") or []
        types = Counter(q.get("type") for q in questions if isinstance(q, dict))
        if types.get("sort"):
            rep.err(pid, "papers contain only mcq and open questions")
        if not fixture and kind in validate_papers.SHAPES:
            for qtype, (lo, hi) in validate_papers.SHAPES[kind].items():
                if not lo <= types.get(qtype, 0) <= hi:
                    rep.err(pid, f"{types.get(qtype, 0)} {qtype} questions (want {lo}–{hi})")
        for q in questions:
            if not isinstance(q, dict):
                rep.err(pid, "every question must be an object")
                continue
            qid = str(q.get("id", "?"))
            seen[qid] += 1
            if not re.fullmatch(rf"{re.escape(pid)}-q\d\d", qid):
                rep.err(qid, f"question id must be {pid}-qNN")
            ref = q.get("module_ref")
            if ref not in sections:
                rep.err(qid, f"module_ref {ref!r} is not a module in this build")
                continue
            validate_papers.check_question(rep, q, sections[ref])
    rep.errors.extend(f"ERROR   duplicate paper question id {i}" for i, n in seen.items() if n > 1)
    return [f"papers: {e}" for e in rep.errors]


PRACTICE_MODES = ("next10", "weak", "new", "sample")
PRACTICE_TYPES = ("any", "mcq", "open", "sort")
LABS = ("pipes", "perms", "paths", "chains")
TOP_LEVEL = ("home", "plan", "learn", "practice", "exam", "cards", "glossary", "labs", "more")


class Known:
    """What a build contains, for checking that plan links lead somewhere."""

    def __init__(self, modules: list[dict[str, Any]], papers: list[dict[str, Any]]) -> None:
        def items(mod: dict[str, Any], key: str) -> list[dict[str, Any]]:
            found = mod.get(key)
            return [x for x in found if isinstance(x, dict)] if isinstance(found, list) else []

        self.modules = {str(m.get("id")) for m in modules}
        self.sections = {
            str(s.get("id")) for m in modules for s in items(m, "sections") if s.get("id")
        }
        self.questions = {
            str(q.get("id")) for m in modules for q in items(m, "questions") if q.get("id")
        } | {str(q.get("id")) for p in papers for q in items(p, "questions") if q.get("id")}
        self.papers = {str(p.get("id")) for p in papers} | (
            {"sample"} if "sample-paper" in self.modules else set()
        )
        self.pipelines = {str(x.get("id")) for m in modules for x in items(m, "pipelines")}
        self.commits = {str(x.get("hash")) for m in modules for x in items(m, "commits")}


def plan_link_known(link: str, known: Known) -> bool:
    """True when `link` (#view.arg.arg) follows the router's grammar (app/API.md) and everything
    it names is in the build."""
    view, *args = link.removeprefix("#").split(".")
    if view not in (*TOP_LEVEL, "history", "q"):
        return False
    if view == "learn":
        if not args:
            return True
        if args[0] not in known.modules or len(args) > 2:
            return False
        return len(args) == 1 or args[1] == "end" or f"{args[0]}-{args[1]}" in known.sections
    if view == "practice":
        if not args:
            return True
        mode, scope, kind = (args + [None, None])[:3]
        return (
            mode in PRACTICE_MODES
            and len(args) <= 3
            and (scope is None or scope == "all" or scope in known.modules | known.sections)
            and (kind is None or kind in PRACTICE_TYPES)
        )
    if view == "q":
        return len(args) == 1 and args[0] in known.questions
    if view == "cards":
        return len(args) <= 1 and (not args or args[0] in known.modules)
    if view == "exam":
        return len(args) <= 1 and (not args or args[0] == "bank" or args[0] in known.papers)
    if view == "history":
        if "history" not in known.modules:
            return False
        rest = args[1:] if args[:1] == ["guess"] else args
        return len(rest) <= 1 and (not rest or rest[0] in known.commits)
    if view == "labs":
        if not args:
            return True
        return args[0] in LABS and (
            len(args) == 1 or (args[0] == "pipes" and args[1] in known.pipelines)
        )
    return not args  # home, plan, glossary, more


def check_plan(plan: Any, known: Known) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(plan, list):
        return ['plan: content/plan.json must hold a "days" list'], warnings
    if not plan:
        return errors, ["plan: content/plan.json is absent or empty, so the plan page is empty"]
    ids: Counter[str] = Counter()
    for day in plan:
        if not isinstance(day, dict):
            errors.append("plan: every day must be an object")
            continue
        did = day.get("id", "?")
        for key in ("id", "date", "label", "title"):
            if not isinstance(day.get(key), str) or not day.get(key):
                errors.append(f"plan {did}: missing {key}")
        if not re.fullmatch(r"\d{4}-\d\d-\d\d", str(day.get("date", ""))):
            errors.append(f"plan {did}: date must be YYYY-MM-DD")
        items = day.get("items")
        if not isinstance(items, list) or not items:
            errors.append(f"plan {did}: items must be a non-empty list")
            continue
        for item in items:
            if not isinstance(item, dict):
                errors.append(f"plan {did}: every item must be an object")
                continue
            ids[str(item.get("id"))] += 1
            if not item.get("id") or not item.get("label"):
                errors.append(f"plan {did}: every item needs an id and a label")
            link = str(item.get("link", ""))
            if not ROUTE_LINK.fullmatch(link):
                errors.append(f"plan {did}: link {link!r} is not a route (#[A-Za-z0-9._~-]+)")
            elif not plan_link_known(link, known):
                warnings.append(f"plan {did}: {link} points at nothing in this build yet")
    errors.extend(f"plan: duplicate item id {i}" for i, n in ids.items() if n > 1)
    return errors, warnings


# ---------------------------------------------------------------------------- history


def git(*args: str) -> str:
    try:
        done = subprocess.run(
            ["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else exc
        raise BuildError(f"git {' '.join(args)} failed in {REPO}: {detail}") from exc
    return done.stdout


def split_file_diffs(patch: str) -> list[str]:
    chunks = re.split(r"(?m)^(?=diff --git )", patch)
    return [c for c in chunks if c.startswith("diff --git ")]


HUNK = re.compile(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


DIFF_LEXERS: dict[str, type[Lexer]] = {
    ".py": PythonLexer,
    ".toml": TOMLLexer,
    ".yml": YamlLexer,
    ".yaml": YamlLexer,
}


def diff_lexer(path: str) -> Lexer | None:
    """The lexer for a file in a diff, by its name; None leaves the code plain. Leading and
    trailing blank lines are kept so line numbers stay true."""
    lexer = DIFF_LEXERS.get(Path(path).suffix)
    return lexer(stripnl=False, ensurenl=True) if lexer else None


def highlighted_lines(text: str, path: str) -> list[str]:
    """A whole file, highlighted as one piece so strings and docstrings that span lines come
    out right, then split into lines (Pygments closes and reopens its spans at each line end)."""
    if not text:
        return []
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    lexer = diff_lexer(path)
    if lexer is None:
        return [escape(line, quote=False) for line in lines]
    out = highlight(text, lexer, FORMATTER).split("\n")
    if out and out[-1] == "":
        out.pop()
    if len(out) != len(lines):
        raise BuildError(f"highlighting {path} gave {len(out)} lines for {len(lines)}")
    return out


def file_version(rev: str, path: str) -> list[str]:
    return highlighted_lines(git("show", f"{rev}:{path}"), path)


def render_file_diff(lines: list[str], old: list[str], new: list[str]) -> str:
    """One file's diff as classed lines, the code highlighted from the whole old and new files.
    Context and added lines come from the new file, removed lines from the old one."""
    out = []
    old_i = new_i = 0
    in_hunk = False
    for line in lines:
        hunk = HUNK.match(line)
        if hunk:
            old_i, new_i = int(hunk.group(1)) - 1, int(hunk.group(2)) - 1
            in_hunk = True
            kind, code = "d-hunk", escape(line, quote=False)
        elif not in_hunk or line.startswith("\\"):
            kind, code = "d-meta", escape(line, quote=False)
        elif line.startswith("+"):
            kind, code = "d-add", "+" + new[new_i]
            new_i += 1
        elif line.startswith("-"):
            kind, code = "d-del", "-" + old[old_i]
            old_i += 1
        else:
            kind, code = "d-ctx", " " + new[new_i]
            old_i += 1
            new_i += 1
        out.append(f'<span class="dline {kind}">{code or " "}</span>')
    return (
        '<div class="code" data-lang="diff"><span class="code-lang" aria-hidden="true">diff</span>'
        f'<pre tabindex="0"><code>{"".join(out)}</code></pre></div>\n'
    )


def file_diff(chunk: str, sha: str) -> dict[str, Any]:
    lines = chunk.rstrip("\n").split("\n")
    head = re.match(r"diff --git a/(.+?) b/(.+)$", lines[0])
    if not head:
        raise BuildError(f"unexpected diff header: {lines[0]}")
    old, new = head.group(1), head.group(2)
    status = "modified"
    if any(line.startswith("new file mode") for line in lines[:4]):
        status = "added"
    elif any(line.startswith("deleted file mode") for line in lines[:4]):
        status = "deleted"
    elif old != new:
        status = "renamed"
    first_hunk = next((i for i, line in enumerate(lines) if line.startswith("@@")), len(lines))
    body = lines[first_hunk:]
    added = sum(1 for line in body if line.startswith("+"))
    removed = sum(1 for line in body if line.startswith("-"))
    old_lines = file_version(f"{sha}^", old) if removed else []
    new_lines = file_version(sha, new) if body and status != "deleted" else []
    return {
        "path": new,
        "old_path": old if status == "renamed" else None,
        "status": status,
        "added": added,
        "removed": removed,
        "lines": len(body),
        "collapsed": len(body) > LONG_FILE_DIFF,
        "html": render_file_diff(lines, old_lines, new_lines),
    }


def count(text: str) -> int | str:
    """A --numstat count; binary files show "-"."""
    return int(text) if text.isdigit() else text


def commit_details(sha: str) -> dict[str, Any]:
    """Everything the history view shows about one commit, read from git at build time."""
    date = git("show", "-s", "--format=%aI", sha).strip()
    body = git("show", "-s", "--format=%B", sha).strip()
    stat = git("show", "--stat=72", "--format=", sha).strip("\n")
    excludes = [f":(exclude,glob)**/{name}" for name in DIFF_EXCLUDES]
    patch = git("show", "--format=", "--no-color", "-M", sha, "--", ".", *excludes)
    hidden = []
    for row in git("show", "--numstat", "--format=", sha).splitlines():
        parts = row.split("\t")
        if len(parts) == 3 and parts[2].split("/")[-1] in DIFF_EXCLUDES:
            hidden.append({"path": parts[2], "added": count(parts[0]), "removed": count(parts[1])})
    return {
        "date": date,
        "body": body,
        "stat": stat,
        "files": [file_diff(chunk, sha) for chunk in split_file_diffs(patch)],
        "hidden": hidden,
    }


def tag_notes() -> dict[str, tuple[str, str]]:
    """Every tag of the repository: name -> (full hash of its commit, annotation subject)."""
    rows = git("for-each-ref", "refs/tags", "--format=%(refname:short)%09%(contents:subject)")
    notes = {}
    for row in rows.splitlines():
        name, _, note = row.partition("\t")
        notes[name] = (git("rev-list", "-n", "1", name).strip(), note)
    return notes


def attach_history(modules: list[dict[str, Any]]) -> None:
    """Attach git's view of each history commit; a tag the content names must be git's tag."""
    for mod in modules:
        if mod.get("id") != "history":
            continue
        tags = tag_notes()
        for commit in mod.get("commits", []):
            sha = str(commit["hash"])
            details = commit_details(sha)
            tag = commit.get("tag")
            if tag:
                full, note = tags.get(tag, ("", ""))
                if not full.startswith(sha):
                    raise BuildError(f"history: {sha} says tag {tag}, but git puts {tag} elsewhere")
                details["tag_note"] = note
            commit["git"] = details


# ----------------------------------------------------------------------------- output


QUOTES = re.compile(r"[`\"'‘’“”]")


def glossary_key(term: str) -> str:
    """A–Z by the words themselves: backticks and quotes do not count; symbols sort first."""
    return QUOTES.sub("", term).strip().casefold()


def glossary(modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries = []
    for mod in modules:
        for term in mod.get("terms", []):
            entries.append(
                {
                    "term": term["term"],
                    "term_html": term["term_html"],
                    "definition_html": term["definition_html"],
                    "mid": mod["id"],
                    "section_ref": term["section_ref"],
                }
            )
    return sorted(entries, key=lambda e: (glossary_key(e["term"]), e["mid"]))


def data_blob(
    modules: list[dict[str, Any]], papers: list[dict[str, Any]], plan: Any, fixture: bool
) -> str:
    mods = convert(sorted(modules, key=lambda m: (m.get("order", 99), m["id"])))
    data = {
        "meta": {
            "exam": EXAM,
            "built": datetime.now().astimezone().isoformat(timespec="seconds"),
            "fixture": fixture,
        },
        "modules": mods,
        "papers": convert(papers),
        "plan": convert(plan),
        "glossary": glossary(mods),
    }
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # Safe inside <script type="application/json">: no "</script" and no "<!--".
    return text.replace("</", "<\\/").replace("<!--", "<\\u0021--")


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
    """app/styles.css (tokens and shared components), then each view's app/css/*.css by name."""
    files = [APP / "styles.css", *sorted((APP / "css").glob("*.css"))]
    parts = []
    for path in files:
        css = path.read_text(encoding="utf-8")
        if re.search(r"</style", css, re.IGNORECASE):
            raise BuildError(f"{shown(path)} contains '</style'")
        parts.append(css.strip())
    return "\n\n".join(parts)


def page_parts(blob: str) -> tuple[str, str]:
    css = stylesheet()
    shell = (APP / "shell.html").read_text(encoding="utf-8").strip()
    head = (
        f"<title>{TITLE}</title>\n<style>\n{css.strip()}\n</style>\n"
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'<link rel="stylesheet" href="{FONTS}">\n'
    )
    body = (
        f"{shell}\n"
        f'<script type="application/json" id="study-data">{blob}</script>\n'
        f"<script>\n{js_bundle()}</script>\n"
    )
    return head, body


def write_pages(head: str, body: str, out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    artifact = out / "artifact.html"
    artifact.write_text(head + body, encoding="utf-8")
    index = out / "index.html"
    index.write_text(
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"{head}</head>\n<body>\n{body}</body>\n</html>\n",
        encoding="utf-8",
    )
    return [index, artifact]


def build(fixture: bool, out: Path) -> int:
    modules, papers, plan = load_sources(fixture)
    source = "content/_fixture.json" if fixture else "content/*.json"
    print(f"Building from {source}: {len(modules)} modules, {len(papers)} papers")
    if not modules:
        raise BuildError("no modules found (use --fixture until content/<id>.json exists)")
    errors = check_modules(modules, fixture)
    errors += check_papers(papers, modules, fixture)
    plan_errors, plan_warnings = check_plan(plan, Known(modules, papers))
    errors += plan_errors
    for line in plan_warnings:
        print(f"  warning {line}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise BuildError(f"{len(errors)} content errors; nothing was written")
    attach_history(modules)
    blob = data_blob(modules, papers, plan, fixture)
    head, body = page_parts(blob)
    paths = write_pages(head, body, out)
    print(f"  data blob {len(blob.encode()) / 1024:,.0f} KiB")
    for path in paths:
        size = path.stat().st_size
        print(f"  wrote {shown(path)}  {size / 1024:,.0f} KiB")
        if size > MAX_BYTES:
            raise BuildError(f"{path.name} is over the 16 MB artifact limit")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--fixture", action="store_true", help="build from content/_fixture.json")
    parser.add_argument(
        "--out", type=Path, default=DIST, help="folder for index.html and artifact.html (dist/)"
    )
    args = parser.parse_args(argv)
    try:
        return build(args.fixture, args.out.resolve())
    except BuildError as exc:
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
