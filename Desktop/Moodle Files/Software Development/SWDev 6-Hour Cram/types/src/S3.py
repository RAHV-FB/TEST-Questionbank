"""S3 (sample Q3): a mypy error, which fix? Writes ../S3.json.

Facts from session 7 slides 8-10, labs/07-refactor.md and the teacher's Q3/Q9 answers (the fourth
kind, "Any leaks in"). Tool output is copied from the bank (refactor-types-q33 run) or was run for
this file (the Ticket example, mypy 2.4.0 with --strict). Practice ids are mcq only, core or exam.
"""

import json
from pathlib import Path

S3 = {
    "tid": "S3",
    "name": "A mypy error: which fix?",
    "minutes": 15,
    "shape_md": (
        "Sample Q3: a short snippet, one `mypy --strict` line and four fixes. The wrong fixes silence "
        "mypy and leave the program exactly as it was."
    ),
    "one_md": (
        "Name the kind of error and take the fix that deals with the problem, because "
        "`# type: ignore` and `Any` only change what mypy says and the crash stays."
    ),
    "sample": {
        "qnum": "Q3",
        "kind": "mcq",
        "question_md": (
            "`mypy --strict` reports this error on the code below:\n\n"
            "```python\n"
            "def find_expense(expenses: list[Expense], expense_id: int) -> Expense | None: ...\n\n"
            "expense = find_expense(expenses, 3)\n"
            "total += expense.amount\n"
            "```\n\n"
            "```text\n"
            "error: Item \"None\" of \"Expense | None\" has no attribute \"amount\"  [union-attr]\n"
            "```\n\n"
            "Which fix is most appropriate?"
        ),
        "options": [
            "Add `# type: ignore` to the line",
            "Handle the `None` case before using `expense.amount`",
            "Change the return type of `find_expense` to `Any`",
            "Delete the type annotations from the function",
        ],
        "answer": 1,
        "his_answer_md": (
            "**b.** The error says the value can be None. Handle that case. `# type: ignore` and `Any` hide "
            "the problem and keep the crash. Removing annotations makes the checker blind."
        ),
        "decoded_md": (
            "- **The pattern.** Code, one mypy line, \"which fix?\". The message already says the kind in plain "
            "words: `Item \"None\" of \"Expense | None\"` means the value can be missing. That is session 7's "
            "None not handled (\"this can be missing\").\n"
            "- **Why b.** The slide's fix for that kind is \"check it, or change the type\". Either way the "
            "missing case gets an answer.\n"
            "- **Why a, c and d tempt.** Each one makes the message go away. a) hides the line from mypy. "
            "c) `Any` tells mypy to stop checking every use of the result. d) removes what mypy needs to see "
            "the `None`; his word is \"blind\", and under `--strict` it also adds a new missing-annotation error.\n"
            "- **The test behind all four.** Does it change what happens when the value is `None`, or only "
            "what mypy says? Only b changes what happens.\n"
            "- **Level.** One sentence reading the error, one sentence on why the silent fixes keep the crash."
        ),
    },
    "spot_md": (
        "- A short function, one line of `mypy --strict` output with a `[code]` in brackets, and \"Which fix is most appropriate?\".\n"
        "- Several options only silence mypy: `# type: ignore`, `Any`, deleted annotations, or CI told to check less.\n"
        "- The message words tell the kind: `missing a type annotation`, `Item \"None\" of`, `Returning Any`, `Incompatible types`.\n"
        "- The same line may come back in an open question: sort the errors, say which one crashes."
    ),
    "basics": [
        {
            "id": "S3-b1",
            "heading": "Read the line and name the kind",
            "body_md": (
                "A mypy line has three parts: the file and line (where), the message (what is wrong, in plain "
                "words) and the `[code]` (what to search for). Read the first error, fix it, run again.\n\n"
                "Session 7 sorts strict errors into kinds. His Q9 answer adds a fourth.\n\n"
                "| Kind | He asks | In the message | Fix |\n|---|---|---|---|\n"
                "| Missing annotation | \"what type is this?\" | `missing a type annotation`, `Need type annotation` | write the hint, such as `dict[str, float]` |\n"
                "| None not handled | \"this can be missing\" | `Item \"None\" of ...` | check it, or change the type |\n"
                "| Any leaks in | \"I gave up on this value\" | `Returning Any from function declared to return \"float\"` | convert the value, `float(...)`, or annotate the variable |\n"
                "| Types disagree | \"`int` here, `float` there\" | `Incompatible types` | make them agree, `0.0` and not `0` |\n\n"
                "Only None not handled predicts a crash for a user. The slide: \"Empty list → None → crash at 2 a.m.\""
            ),
        },
        {
            "id": "S3-b2",
            "heading": "Fixes that only change what mypy says",
            "body_md": (
                "| \"Fix\" | What it does to mypy | What it does to Python |\n|---|---|---|\n"
                "| `# type: ignore` | stops reporting that line | nothing |\n"
                "| return type `Any` | stops checking every use of the value | nothing |\n"
                "| delete the annotations | adds a missing-annotation error and hides the `None` | nothing |\n\n"
                "A real run on a lookup that returns `Expense | None`, with `# type: ignore` on the last line "
                "(traceback trimmed to its last line):\n\n"
                "```console\n"
                "$ uv run mypy --strict ignored.py\n"
                "Success: no issues found in 1 source file\n"
                "$ uv run python ignored.py\n"
                "AttributeError: 'NoneType' object has no attribute 'amount'\n"
                "```\n\n"
                "mypy says Success and the program still crashes. Ask one question of any fix: does it change "
                "what happens when the value is missing, or only what mypy says?"
            ),
        },
    ],
    "checks": [
        {
            "id": "S3-c1",
            "q_md": "mypy says `Need type annotation for \"totals\"` for the line `totals = {}`. Which kind is it?",
            "options": [
                "Missing annotation",
                "None not handled",
                "Types disagree",
            ],
            "answer": 0,
            "why_md": "An empty `{}` has no type yet, so you say what it will hold: `totals: dict[str, float] = {}`.",
        },
        {
            "id": "S3-c2",
            "q_md": "`find_expense` can return `None`. Which change leaves the crash in place?",
            "options": [
                "Check `if expense is None` and show a message",
                "Change the return type to `Any`",
                "Raise a clear error for an id that does not exist",
            ],
            "answer": 1,
            "why_md": (
                "`Any` switches the checking off. The function still returns `None` and `.amount` still fails. "
                "The other two decide what happens when there is no result."
            ),
        },
    ],
    "method": [
        "Read the message and the `[code]`. Ignore the rest of the file until you know the kind.",
        "Name the kind: missing annotation, None not handled, Any leaks in, or types disagree.",
        "Take that kind's fix. For `None`, decide what the program does when the value is missing.",
        "Cross out the options that only silence mypy: `# type: ignore`, `Any`, deleted annotations, CI told to check less.",
        "If it is open, say what stays broken if you silence it: \"the crash stays and CI no longer shows it\".",
    ],
    "worked": [
        {
            "title": "Same shape, other topic: the parking lot",
            "question_md": (
                "`mypy --strict` reports this error on the code below:\n\n"
                "```python\n"
                "def find_ticket(tickets: list[Ticket], plate: str) -> Ticket | None: ...\n\n"
                "def fee_for(tickets: list[Ticket], plate: str) -> int:\n"
                "    return find_ticket(tickets, plate).minutes * 2\n"
                "```\n\n"
                "```text\n"
                "error: Item \"None\" of \"Ticket | None\" has no attribute \"minutes\"  [union-attr]\n"
                "```\n\n"
                "Which fix is most appropriate?\n\n"
                "- a) Add `# type: ignore` to the line\n"
                "- b) Check for `None` first and decide what `fee_for` does when there is no ticket\n"
                "- c) Change the return type of `find_ticket` to `Any`\n"
                "- d) Delete the type annotations from `find_ticket`"
            ),
            "steps_md": [
                "The message says `Item \"None\" of \"Ticket | None\"`: the value can be missing. That is None not handled.",
                "The fix for that kind is to check it, or change the type. Only b does that.",
                "a), c) and d) make the message go away and leave the crash for a plate with no ticket.",
            ],
            "answer_md": (
                "**b.** The error says the ticket can be `None`, for a plate that has none. Check that case first, "
                "then raise a clear error or return a fee of zero. `# type: ignore` and `Any` hide the problem and "
                "keep the crash, and deleting annotations makes mypy blind."
            ),
        }
    ],
    "twists": [
        {
            "twist_md": "The error is `Returning Any from function declared to return \"float\"`, and the value came from `json.load`.",
            "how_md": (
                "Any leaks in: the value came from something untyped. Convert it with `float(...)` or annotate the "
                "variable. `# type: ignore[no-any-return]` names the code and is still only silence."
            ),
        },
        {
            "twist_md": "The error is `Missing type arguments for generic type \"dict\"` or `Need type annotation`.",
            "how_md": "Missing annotation. Write the hint, and read the function to see what the dictionary holds.",
        },
        {
            "twist_md": "A teammate adds `# type: ignore` \"to get CI green\".",
            "how_md": "The `None` crash stays and CI no longer shows it. Fix the cause: annotate, handle the `None`, give a real return type.",
        },
        {
            "twist_md": "CI is red at the Types step and green on your laptop.",
            "how_md": "You ran `mypy src`; CI runs `mypy src tests`. Every test needs `-> None`. Do not make CI check less.",
        },
        {
            "twist_md": "Four errors, the first one `Function is missing a type annotation`.",
            "how_md": "Read the first error, fix it, run again. The calls to that function and the `Returning Any` below often come from it.",
        },
    ],
    "traps": [
        "\"`# type: ignore` makes it safe.\" mypy reads the comment and Python does not. Same line, same crash.",
        "\"`Any` is a type, so the error is fixed.\" `Any` switches checking off for every use of the value, typos included.",
        "\"Delete the annotations so mypy has nothing to complain about.\" Under `--strict` that is a new error, and mypy can no longer see the `None`.",
        "\"ruff and pytest are green, so the mypy error is pedantic.\" mypy finds the crash on the input nobody tried, such as an empty list.",
    ],
    "say_md": (
        "- The error says the value can be `None`. I handle that case before using it, or change the type.\n"
        "- `# type: ignore` and `Any` hide the problem and keep the crash. Removing annotations makes the checker blind.\n"
        "- Four kinds: missing annotation, None not handled, Any leaks in, types disagree. Only `None` predicts a crash.\n"
        "- Read the first error, fix it, run again."
    ),
    "practice": [
        "refactor-types-q30",
        "refactor-types-q18",
        "refactor-types-q17",
        "refactor-types-q28",
        "refactor-types-q29",
        "refactor-types-q33",
    ],
    "short_answers": {},
}

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "S3.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(S3, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {out}")
