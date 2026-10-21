"""Read the teacher's nine sample questions and his official answers (verbatim sources).

The two Markdown files live in the main site's sources and are never changed:
    study-site/sources/moodle/midterm-sample-questions.md   the nine questions
    study-site/sources/moodle/midterm-sample-answers.md     his answers and his marking guide

`load()` returns the questions by number, the answers by number and his marking guide. The type
validator checks the `sample` block of S1 to S9 against it, and the build puts his answers into the
sample paper's review. Both read the same parse, so his words are never retyped.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TypedDict

SITE = Path(__file__).resolve().parent.parent / "study-site"
QUESTIONS = SITE / "sources" / "moodle" / "midterm-sample-questions.md"
ANSWERS = SITE / "sources" / "moodle" / "midterm-sample-answers.md"

LETTERS = "abcd"
MCQ_NUMBERS = (1, 2, 3, 4, 5, 6)
OPEN_NUMBERS = (7, 8, 9)


class SampleQuestion(TypedDict):
    n: int
    kind: str  # "mcq" or "open"
    stem: str  # the Markdown above the options or the numbered parts
    options: list[str]  # mcq: the four option texts, without "a) "
    parts: list[str]  # open: the numbered prompts, without "1. "


class SampleAnswer(TypedDict):
    n: int
    kind: str
    letter: str  # mcq: "a" to "d" ("" for an open question)
    why: str  # mcq: his reason ("" for an open question)
    parts: dict[str, str]  # open: part label -> his answer for that part, as Markdown
    text: str  # open: his whole block


class Official(TypedDict):
    questions: dict[int, SampleQuestion]
    answers: dict[int, SampleAnswer]
    marking: list[tuple[str, str]]  # his marking guide: (label, text)


class OfficialError(Exception):
    """The source files are missing or not in the expected shape."""


QUESTION_HEAD = re.compile(r"^###\s+Q(\d+)\b")
OPTION = re.compile(r"^- ([a-d])\) (.*)$")
PART = re.compile(r"^(\d+)\. (.*)$")
TABLE_ROW = re.compile(r"^\|\s*Q(\d+)\s*\|\s*([a-d])\s*\|\s*(.*?)\s*\|\s*$")
ANSWER_HEAD = re.compile(r"^##\s+Q(\d+)\b")
GUIDE_HEAD = re.compile(r"^##\s+Marking guide", re.IGNORECASE)
GUIDE_LINE = re.compile(r"^- ([^:]+): (.*)$")


def read(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise OfficialError(f"cannot read {path}: {exc}") from exc


def parse_questions(lines: list[str]) -> dict[int, SampleQuestion]:
    blocks: dict[int, list[str]] = {}
    current: int | None = None
    for line in lines:
        head = QUESTION_HEAD.match(line)
        if head:
            current = int(head.group(1))
            blocks[current] = []
        elif line.startswith("## "):
            current = None
        elif current is not None:
            blocks[current].append(line)
    out: dict[int, SampleQuestion] = {}
    for n, block in blocks.items():
        stem: list[str] = []
        options: list[str] = []
        parts: list[str] = []
        in_code = False
        started = False
        for line in block:
            if line.strip().startswith("```"):
                in_code = not in_code
            option = None if in_code else OPTION.match(line)
            part = None if in_code else PART.match(line)
            if option:
                options.append(option.group(2).strip())
                started = True
            elif part:
                parts.append(part.group(2).strip())
                started = True
            elif not started:
                stem.append(line)
        out[n] = {
            "n": n,
            "kind": "mcq" if options else "open",
            "stem": "\n".join(stem).strip(),
            "options": options,
            "parts": parts,
        }
    return out


def parse_parts(block: list[str]) -> dict[str, str]:
    """Split an open answer at its top-level numbers; sub-bullets stay with their part."""
    parts: dict[str, list[str]] = {}
    label: str | None = None
    for line in block:
        part = PART.match(line)
        if part:
            label = part.group(1)
            parts[label] = [part.group(2)]
        elif label is not None:
            parts[label].append(re.sub(r"^ {1,3}", "", line))
    return {k: "\n".join(v).strip() for k, v in parts.items()}


def parse_answers(lines: list[str]) -> tuple[dict[int, SampleAnswer], list[tuple[str, str]]]:
    answers: dict[int, SampleAnswer] = {}
    marking: list[tuple[str, str]] = []
    section: str | None = None
    open_blocks: dict[int, list[str]] = {}
    current: int | None = None
    for line in lines:
        row = TABLE_ROW.match(line)
        if row:
            n = int(row.group(1))
            answers[n] = {
                "n": n,
                "kind": "mcq",
                "letter": row.group(2),
                "why": row.group(3),
                "parts": {},
                "text": "",
            }
            continue
        head = ANSWER_HEAD.match(line)
        if head:
            current = int(head.group(1))
            section = "open"
            open_blocks[current] = []
        elif GUIDE_HEAD.match(line):
            section = "guide"
            current = None
        elif line.startswith("## "):
            section = None
            current = None
        elif section == "open" and current is not None:
            open_blocks[current].append(line)
        elif section == "guide":
            guide = GUIDE_LINE.match(line)
            if guide:
                marking.append((guide.group(1).strip(), guide.group(2).strip()))
    for n, block in open_blocks.items():
        text = "\n".join(block).strip()
        answers[n] = {
            "n": n,
            "kind": "open",
            "letter": "",
            "why": "",
            "parts": parse_parts(block),
            "text": text,
        }
    return answers, marking


def load() -> Official:
    questions = parse_questions(read(QUESTIONS))
    answers, marking = parse_answers(read(ANSWERS))
    problems: list[str] = []
    for n in (*MCQ_NUMBERS, *OPEN_NUMBERS):
        if n not in questions:
            problems.append(f"{QUESTIONS.name}: Q{n} not found")
        if n not in answers:
            problems.append(f"{ANSWERS.name}: the answer to Q{n} not found")
    for n in MCQ_NUMBERS:
        if n in questions and len(questions[n]["options"]) != 4:
            problems.append(f"{QUESTIONS.name}: Q{n} should have four options")
    for n in OPEN_NUMBERS:
        if n in answers and not answers[n]["parts"]:
            problems.append(f"{ANSWERS.name}: Q{n} has no numbered parts")
        if n in questions and not questions[n]["parts"]:
            problems.append(f"{QUESTIONS.name}: Q{n} has no numbered parts")
    if len(marking) != 3:
        problems.append(f"{ANSWERS.name}: expected three lines in the marking guide")
    if problems:
        raise OfficialError("; ".join(problems))
    return {"questions": questions, "answers": answers, "marking": marking}


def answer_md(answer: SampleAnswer) -> str:
    """His answer as Markdown for display: the letter and reason, or the numbered parts."""
    if answer["kind"] == "mcq":
        return f"**{answer['letter']})** {answer['why']}"
    return "\n".join(
        f"{label}. " + text.replace("\n", "\n   ") for label, text in answer["parts"].items()
    )
