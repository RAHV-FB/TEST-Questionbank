"""Stop S9 of the 6-hour cram: sample Q9, read tool output and judge a shortcut (open, harder).

Writes types/S9.json in the shape given by CRAM6_SPEC.md. The teacher's answer is copied verbatim
from study-site/sources/moodle/midterm-sample-answers.md. The worked example uses three lines of the
real mypy output shown in the bank question sample-paper-q33.
"""

import json
from pathlib import Path

QUESTION = (
    "You run `uv run mypy --strict src` on a teammate's branch:\n\n"
    "```text\n"
    "src/report.py:8: error: Function is missing a type annotation  [no-untyped-def]\n"
    "src/report.py:15: error: Item \"None\" of \"Expense | None\" has no attribute \"category\"  [union-attr]\n"
    "src/report.py:22: error: Returning Any from function declared to return \"float\"  [no-any-return]\n"
    "```"
)

HIS_ANSWER = (
    "1. Line 8 is a missing annotation (\"what type is this?\"). Line 15 is a None not handled (\"this can be "
    "missing\"). Line 22 is Any leaks in (\"I gave up on this value\").\n"
    "2. Line 15. If `Expense | None` is None at runtime (an empty list or a missing id), the program crashes with "
    "an AttributeError for a real user. The other two are weaknesses in the checking, not crashes in themselves.\n"
    "3. No. `# type: ignore` hides the warning without removing the problem. The line 15 crash stays, and now CI "
    "no longer shows it. The honest fixes are to annotate line 8, handle None on line 15 (check it, or change the "
    "type), and give line 22 a real return type. `# type: ignore` is acceptable only for a rare case that is "
    "understood, commented and deliberately accepted."
)

DECODED = (
    "- **The pattern.** A short mypy log, then three parts: sort the errors, find the one that can crash, judge "
    "a shortcut. It is the one open question on tool output.\n"
    "- **Part 1: sort by the words of the message.** `Function is missing a type annotation` is a missing "
    "annotation (\"what type is this?\"). `Item \"None\" of ...` is None not handled (\"this can be "
    "missing\"). `Returning Any ...` is a fourth kind, Any leaks in (\"I gave up on this value\"). Give the "
    "kind for each line number. \"Types disagree\" (\"int here, float there\") is the kind from session 7 "
    "that this log does not contain. Never file `Returning Any` under it.\n"
    "- **Part 2: line 15, with the when and the what.** The value is `None` for an empty list or a missing id, "
    "and the program stops with an `AttributeError` for a real user. The reason is what happens at run time. "
    "The other two are weaknesses in the checking, not crashes in themselves.\n"
    "- **Part 3: \"No\", then the reason, then the fix.** The ignore hides the warning, not the problem: the "
    "crash stays and CI stops showing it. Then one real fix per error: annotate line 8, handle `None` on line "
    "15, give line 22 a real return type. His closing sentence allows an ignore only for a rare case that is "
    "understood, commented and deliberately accepted.\n"
    "- **What does not score.** Copying the bracketed codes, or \"no, ignores are bad practice\" with no "
    "reason. Terms that are not connected to the output earn nothing."
)

SPOT = (
    "- A few lines of `file:line: error: message  [code]` output, with little or no code shown.\n"
    "- The wording \"Sort the errors into the kinds\", \"which one points to a bug that could crash the "
    "program\" and \"Do you accept? Give your reasoning\".\n"
    "- A shortcut to get CI green: `# type: ignore`, `Any`, deleting the hints, running `mypy src` instead of "
    "`mypy src tests`, or switching strict off.\n"
    "- The same shape with other output is possible, for example a red `pytest` line and a proposal to loosen "
    "the assert or rerun the test."
)

BASICS = [
    {
        "id": "S9-b1",
        "heading": "Reading the log: four kinds",
        "body_md": (
            "Read each line in three parts: the file and line (where), the message (what is wrong, in plain "
            "words) and the `[code]` (what to search for). Then sort by the words of the message. Session 7 "
            "teaches three kinds. His Q9 answer uses a fourth.\n\n"
            "| Kind | You read | It means | Fix |\n"
            "|---|---|---|---|\n"
            "| Missing annotation | `Function is missing a type annotation` | \"what type is this?\" | write the "
            "hint |\n"
            "| Types disagree | `Incompatible types in assignment` | \"int here, float there\" | make them "
            "agree (`0.0`) |\n"
            "| None not handled | `Item \"None\" of ...` | \"this can be missing\" | check it, or change the "
            "type |\n"
            "| Any leaks in | `Returning Any from function declared to return \"float\"` | \"I gave up on this "
            "value\" | give the value a real type |\n\n"
            "Never file `Returning Any` under types disagree. A bracketed code is a name to search for, not a "
            "kind."
        ),
    },
    {
        "id": "S9-b2",
        "heading": "Which one crashes, and the type: ignore verdict",
        "body_md": (
            "Only None not handled predicts a crash on an ordinary input. The type says the value can be missing "
            "(an empty list, an unknown id), the code uses it as if it never is, and the program stops with an "
            "`AttributeError`. The `int` and `float` kind of types disagree does not crash: Python adds a float to an "
            "`int` total without complaint. Missing annotation and Any leaks in are weaknesses in the checking, because mypy cannot "
            "check what happens to that value. Name the line, say when the value is `None`, and say what the "
            "user sees.\n\n"
            "`# type: ignore` hides the warning, not the problem. The crash stays, and CI no longer shows it. "
            "The same holds for changing a type to `Any`, deleting the hints, running `mypy src` instead of "
            "`mypy src tests`, or switching strict off: each makes CI green by checking less. The honest fixes "
            "are one line each. An ignore is acceptable only for a rare case that is understood, commented and "
            "deliberately accepted.\n\n"
            "Answer in the order verdict, reason, fix."
        ),
    },
]

CHECKS = [
    {
        "id": "S9-c1",
        "q_md": "Which kind is `Returning Any from function declared to return \"float\"`?",
        "options": [
            "Missing annotation",
            "Types disagree",
            "Any leaks in: \"I gave up on this value\"",
            "None not handled",
        ],
        "answer": 2,
        "why_md": (
            "The function promised a `float` and returns a value mypy can only call `Any`, usually because it came "
            "from untyped code such as `json.load`. It is not types disagree: no real types clash."
        ),
    },
    {
        "id": "S9-c2",
        "q_md": "A function returns `Expense | None` and the caller reads `.category` without a check. When does it crash?",
        "options": [
            "Every time it runs.",
            "When the list is empty or the id is missing, because the value is `None`.",
            "Never: mypy would have stopped the program first.",
        ],
        "answer": 1,
        "why_md": (
            "mypy only reports the problem. The program still runs, and on an ordinary empty input it raises an "
            "`AttributeError`."
        ),
    },
    {
        "id": "S9-c3",
        "q_md": "A teammate adds `# type: ignore` to the line-15 error. What has changed?",
        "options": [
            "Nothing in the program: the crash is still there and CI no longer shows it.",
            "The crash is fixed.",
            "mypy now checks that line more strictly.",
        ],
        "answer": 0,
        "why_md": "The ignore changes what mypy reports, not what Python runs.",
    },
]

METHOD = [
    "Read each line in three parts: where (file and line), what (the message), and the `[code]`.",
    "Part 1: sort by the words of the message. Give the kind for every line number, with a few words of why.",
    "Part 2: pick the `None` line. Say when the value is `None` (an empty list, a missing id) and what the user "
    "sees (an `AttributeError`).",
    "Part 3: verdict first (\"No\"), then the reason (the crash survives the ignore), then the real fix for "
    "each error.",
    "One or two sentences for each part. Number them as the question does.",
]

WORKED = [
    {
        "title": "Same shape, three lines of a real CI log",
        "question_md": (
            "CI is red at the Types step. Your teammate says \"pytest passes on my laptop\". You read three lines "
            "of the log (trimmed). Line 13 is `def read_expenses(path):`, and line 36 builds the `Largest single "
            "expense` line from `largest.merchant`.\n\n"
            "```text\n"
            "src/expense_tracker/report.py:13: error: Function is missing a type annotation  [no-untyped-def]\n"
            "src/expense_tracker/report.py:35: error: Incompatible types in assignment (expression has type "
            "\"float\", variable has type \"int\")  [assignment]\n"
            "src/expense_tracker/report.py:36: error: Item \"None\" of \"Expense | None\" has no attribute "
            "\"merchant\"  [union-attr]\n"
            "```\n\n"
            "1. Sort the three errors into the kinds from session 7.\n"
            "2. Which one could crash the program for a real user, and why?\n"
            "3. Your teammate proposes `# type: ignore` on all three. Do you accept?"
        ),
        "steps_md": [
            "Part 1: read the words. \"Missing a type annotation\" is one kind, \"Incompatible types\" another, "
            "`Item \"None\" of` the third.",
            "Part 2: the `None` line. `largest` is `None` when the file has no expenses.",
            "Part 3: verdict, reason, fix. The crash on line 36 would stay behind a green tick.",
        ],
        "answer_md": (
            "1. Line 13 is a missing annotation. Line 35 is types disagree (a `float` into an `int`). Line 36 is "
            "None not handled.\n"
            "2. Line 36. `largest` is `None` when the file has no expenses, so `largest.merchant` raises an "
            "`AttributeError`. The other two do not crash by themselves.\n"
            "3. No. `# type: ignore` hides the report, not the problem: the crash stays and CI stops showing it. "
            "I would annotate line 13, start the total at `0.0` and check for `None`."
        ),
    }
]

TWISTS = [
    {
        "twist_md": "The log has `Returning Any from function declared to return \"float\"  [no-any-return]`.",
        "how_md": (
            "Any leaks in: \"I gave up on this value\". It comes from something untyped such as `json.load`. Give "
            "the value a real type, for example `float(...)`. It weakens the checking and does not crash by "
            "itself."
        ),
    },
    {
        "twist_md": "The log has `Missing type arguments for generic type \"dict\"  [type-arg]`.",
        "how_md": (
            "Missing annotation: what does the dict hold? Write `dict[str, float]`. The hint exists but is "
            "incomplete."
        ),
    },
    {
        "twist_md": "CI is red at Types with `Function is missing a return type annotation` in `tests/`, and `mypy src` is green on the laptop.",
        "how_md": (
            "CI runs `mypy src tests`, and strict wants `-> None` on every test. Add it. Do not narrow CI to "
            "`mypy src` or switch strict off: that makes CI green by checking less."
        ),
    },
    {
        "twist_md": "The teammate proposes changing the return type to `Any`, or deleting the hints.",
        "how_md": (
            "Both make the checker blind. `Any` is `# type: ignore` at the level of one value, and the crash is "
            "still there."
        ),
    },
    {
        "twist_md": "The output is a red `pytest` line and the teammate proposes widening the tolerance or rerunning.",
        "how_md": (
            "Same verdict: no. It hides what the test told you. Check the requirement first, then fix the code or "
            "the test."
        ),
    },
]

TRAPS = [
    "`Returning Any` is Any leaks in: \"I gave up on this value\". It is not types disagree, because no two real "
    "types clash.",
    "Picking the `int` against `float` error as the crash. Python adds the two without complaint. The `None` line "
    "is the one that crashes.",
    "\"No, ignores are bad practice.\" That is a slogan. Give the reason: the crash is still there behind a green "
    "CI.",
    "Copying the bracketed codes as the answer to part 1. A code is a name to search for. Name the kind.",
]

SAY = (
    "- \"Line 8 is a missing annotation, line 15 is None not handled, line 22 is Any leaks in (I gave up on this "
    "value).\"\n"
    "- \"Line 15. If the value is `None` (an empty list or a missing id), the program crashes with an "
    "`AttributeError` for a real user. The other two are weaknesses in the checking.\"\n"
    "- \"No. `# type: ignore` hides the warning, not the problem: the crash stays and CI no longer shows it.\"\n"
    "- \"I would annotate, handle `None` and give the value a real type.\"\n"
    "- An ignore is acceptable only for a rare case that is understood, commented and deliberately accepted."
)

PRACTICE = [
    "sample-paper-q48",
    "sample-paper-q38",
    "sample-paper-q34",
    "history-q35",
    "refactor-types-q41",
]

SHORT_ANSWERS = {
    "history-q35": {
        "1": "It is the red step: the tests say what done means before the code exists, and watching them fail shows "
        "they can fail. The stub lets them import the function, so they fail on behaviour and not on an import "
        "error.",
        "2": "`1e421bc` is green: the smallest code that passes, a loop with a `seen` set that keeps the first of "
        "each expense. `d3df52b` is refactor: the same behaviour in one line with `dict.fromkeys`, tests still green.",
        "3": "`@dataclass(frozen=True)` on `Expense`, from `017f926`. `dict.fromkeys` needs hashable items and a "
        "frozen dataclass is hashable, so without it the tests fail with `unhashable type`.",
    },
    "refactor-types-q41": {
        "1": "It turns on strict mode for every mypy run: every function now needs a full signature, where "
        "`check_untyped_defs` only checked the bodies of untyped functions.",
        "2": "The teammate ran `mypy src`, which never opens `tests/`. CI runs `mypy src tests`, and under strict "
        "the two test functions without `-> None` are errors.",
        "3": "Add `-> None` to the two tests and run `uv run mypy src tests` exactly as CI does before pushing. Do "
        "not change CI to `mypy src` or switch strict off: that makes CI green by checking less.",
    },
}

S9 = {
    "tid": "S9",
    "name": "Read tool output (open, harder)",
    "minutes": 25,
    "shape_md": (
        "Sample Q9, the harder open question: a `mypy --strict` log with three errors, then three parts. Sort the "
        "errors into the kinds from session 7, say which one can crash for a real user and why, and judge a "
        "teammate's `# type: ignore` shortcut."
    ),
    "one_md": (
        "Read each error by its words, sort it into one of four kinds, and name the one that can crash a real "
        "user: the value that can be missing."
    ),
    "sample": {
        "qnum": "Q9",
        "kind": "open",
        "question_md": QUESTION,
        "parts": [
            "Sort the three errors into the kinds we discussed in session 7.",
            "Which one points to a bug that could crash the program for a real user, and why?",
            "Your teammate proposes silencing all three with `# type: ignore` \"to get CI green\". Do you accept? "
            "Give your reasoning.",
        ],
        "his_answer_md": HIS_ANSWER,
        "decoded_md": DECODED,
    },
    "spot_md": SPOT,
    "basics": BASICS,
    "checks": CHECKS,
    "method": METHOD,
    "worked": WORKED,
    "twists": TWISTS,
    "traps": TRAPS,
    "say_md": SAY,
    "practice": PRACTICE,
    "short_answers": SHORT_ANSWERS,
}

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "S9.json"
    with out.open("w", encoding="utf-8") as handle:
        json.dump(S9, handle, ensure_ascii=False, indent=1)
        handle.write("\n")
    print(f"wrote {out}")
